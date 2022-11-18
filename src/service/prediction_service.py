import datetime
import logging
from datetime import datetime

from telegram import Message
from telegram.error import BadRequest
from telegram.ext import CallbackContext

import resources.Environment as Env
import resources.phrases as phrases
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.Notification import PredictionResultNotification, PredictionBetInvalidNotification
from src.model.enums.PredictionStatus import PredictionStatus, get_prediction_status_name_by_key
from src.model.error.CustomException import PredictionException
from src.service.bounty_service import round_belly_up, add_bounty, get_belly_formatted
from src.service.math_service import get_percentage_from_value, get_value_from_percentage
from src.service.message_service import escape_valid_markdown_chars, full_message_send
from src.service.notification_service import send_notification


def send(context: CallbackContext, prediction: Prediction, is_resent: bool = False) -> None:
    """
    Send prediction
    :param context: Telegram context
    :param prediction: Prediction
    :param is_resent: If prediction was already sent
    """

    # Do not change status or message_id if prediction is resent
    if not is_resent:
        if PredictionStatus(prediction.status) is not PredictionStatus.NEW:
            raise PredictionException(phrases.PREDICTION_NOT_IN_NEW_STATUS)

        prediction.status = PredictionStatus.SENT
        prediction.send_date = datetime.now()

    message: Message = full_message_send(context, get_prediction_text(prediction), chat_id=Env.OPD_GROUP_ID.get())
    message.pin(disable_notification=True)

    prediction.message_id = message.message_id
    prediction.save()


def get_prediction_text(prediction: Prediction) -> str:
    """
    Get prediction text
    :param prediction: Prediction
    :return: Prediction text
    """

    # Options text
    options_text = ""
    prediction_options: list[PredictionOption] = prediction.prediction_options
    prediction_options_users: list[PredictionOptionUser] = get_prediction_options_users(prediction)
    total_wager = sum(prediction_option_user.wager for prediction_option_user in prediction_options_users)

    for index, prediction_option in enumerate(prediction_options):
        prediction_option_users: list[PredictionOptionUser] = [
            prediction_option_user for prediction_option_user in prediction_options_users
            if prediction_option_user.prediction_option.id == prediction_option.id
        ]
        option_wager = sum(prediction_option_user.wager for prediction_option_user in prediction_option_users)
        options_text += phrases.PREDICTION_TEXT_OPTION.format(
            prediction_option.number,
            escape_valid_markdown_chars(prediction_option.option),
            get_percentage_from_value(option_wager, total_wager, add_decimal=False),
            (Emoji.CORRECT if prediction_option.is_correct else "")
        )

    added_text = ""

    # Closing date if not None
    added_text += phrases.PREDICTION_CLOSING_DATE.format(prediction.end_date) \
        if prediction.end_date is not None else ""
    # Cut Off date if not None
    added_text += phrases.PREDICTION_CUT_OFF_DATE.format(prediction.cut_off_date) \
        if prediction.cut_off_date is not None else ""

    optional_text = ""
    # Wagers refunded
    enabled_emoji = Emoji.PREDICTION_FEATURE_ENABLED if prediction.refund_wager else Emoji.PREDICTION_FEATURE_DISABLED
    optional_text += phrases.PREDICTION_WAGERS_REFUNDED.format(enabled_emoji)
    # Multiple bets allowed
    enabled_emoji = (Emoji.PREDICTION_FEATURE_ENABLED if prediction.allow_multiple_choices
                     else Emoji.PREDICTION_FEATURE_DISABLED)
    optional_text += phrases.PREDICTION_MULTIPLE_BETS_ALLOWED.format(enabled_emoji)
    # Bet withdrawal allowed
    enabled_emoji = (Emoji.PREDICTION_FEATURE_ENABLED if prediction.can_withdraw_bet
                     else Emoji.PREDICTION_FEATURE_DISABLED)
    optional_text += phrases.PREDICTION_CAN_WITHDRAW_BETS.format(enabled_emoji)

    # Add command to place and remove bets if prediction is open
    how_to_bet_command_text = ""
    how_to_remove_bet_command_text = ""
    if PredictionStatus(prediction.status) is PredictionStatus.SENT:
        how_to_bet_command_text = phrases.PREDICTION_BET_HOW_TO_PLACE_BET

        if prediction.can_withdraw_bet:
            how_to_remove_bet_command_text = phrases.PREDICTION_BET_HOW_TO_REMOVE_ALL_BETS

    # Append \n if not empty
    optional_text = "\n" + optional_text if optional_text != "" else ""
    added_text += optional_text

    # Prediction text
    prediction_text = phrases.PREDICTION_TEXT.format(
        escape_valid_markdown_chars(prediction.question),
        options_text,
        get_belly_formatted(total_wager),
        get_prediction_status_name_by_key(PredictionStatus(prediction.status)),
        added_text,
        how_to_bet_command_text,
        how_to_remove_bet_command_text)

    return prediction_text


def close_bets(context: CallbackContext, prediction: Prediction) -> None:
    """
    Close bets
    :param context: Telegram context
    :param prediction: Prediction
    """
    if PredictionStatus(prediction.status) is not PredictionStatus.SENT:
        raise PredictionException(phrases.PREDICTION_NOT_IN_SENT_STATUS)

    # Dictionary with key: user_id, value: user, prediction option user, total refund
    users_invalid_prediction_options: dict[int, [User, list[PredictionOptionUser], int]] = {}

    # If cut off date is not None, delete all PredictionOptionUsers with date > cut off date and return wager
    if prediction.cut_off_date is not None:
        invalid_prediction_option_users: list[PredictionOptionUser] = PredictionOptionUser.select().where(
            (PredictionOptionUser.prediction == prediction)
            & (PredictionOptionUser.date > prediction.cut_off_date))
        for invalid_prediction_option_user in invalid_prediction_option_users:
            user: User = invalid_prediction_option_user.user
            # Return wager and subtract from pending bounty
            user.pending_bounty -= invalid_prediction_option_user.wager
            user.bounty += invalid_prediction_option_user.wager
            user.save()

            # Add to users_invalid_prediction_options
            if user.id not in users_invalid_prediction_options:
                users_invalid_prediction_options[user.id] = [user, [], 0]

            users_invalid_prediction_options[user.id][1].append(invalid_prediction_option_user)
            users_invalid_prediction_options[user.id][2] += invalid_prediction_option_user.wager

            invalid_prediction_option_user.delete_instance()

    # Update status
    prediction.status = PredictionStatus.BETS_CLOSED
    prediction.end_date = datetime.now()
    prediction.save()

    # Update prediction message
    refresh(context, prediction)

    # Send message in reply notifying users that bets are closed
    full_message_send(context, phrases.PREDICTION_CLOSED_FOR_BETS, chat_id=Env.OPD_GROUP_ID.get(),
                      reply_to_message_id=prediction.message_id)

    # Send notification to users
    for user_id, value in users_invalid_prediction_options.items():
        user: User = value[0]
        prediction_options_user = value[1]
        total_refund = value[2]

        notification: PredictionBetInvalidNotification = PredictionBetInvalidNotification(
            prediction, prediction_options_user, total_refund)

        send_notification(context, user, notification)


def set_results(context: CallbackContext, prediction: Prediction) -> None:
    """
    Set results
    :param context: Telegram context
    :param prediction: Prediction
    """
    if PredictionStatus(prediction.status) is not PredictionStatus.BETS_CLOSED:
        raise PredictionException(phrases.PREDICTION_NOT_IN_BETS_CLOSED_STATUS)

    prediction_options: list[PredictionOption] = prediction.prediction_options
    prediction_options_correct: list[PredictionOption] = [prediction_option for prediction_option in prediction_options
                                                          if prediction_option.is_correct]
    prediction_options_users: list[PredictionOptionUser] = get_prediction_options_users(prediction)

    # Dictionary with key: user_id, value: list (user, total_win, list of prediction_options)
    users_total_win: dict[int, list[User, int, list[PredictionOption]]] = {}

    for prediction_option_user in prediction_options_users:
        user: User = prediction_option_user.user

        # If user is not in dictionary, add it
        if user.id not in users_total_win:
            users_total_win[user.id] = [user, 0, []]

        # Add prediction option to list
        prediction_option: PredictionOption = prediction_option_user.prediction_option
        users_total_win[user.id][2].append(prediction_option)

        # Correct prediction
        if prediction_option.is_correct:
            win_amount = get_prediction_option_user_win(prediction_option_user,
                                                        prediction_options_users=prediction_options_users)
            # Add to bounty
            add_bounty(user, win_amount, pending_belly_amount=prediction_option_user.wager)

            # Add to total win
            users_total_win[user.id][1] += win_amount
        else:
            # Remove from total win
            users_total_win[user.id][1] -= prediction_option_user.wager

        # Subtract bet wager from user pending bounty
        user.pending_bounty -= prediction_option_user.wager

        # Should refund wager or no correct options
        if prediction.refund_wager or len(prediction_options_correct) == 0:
            user.bounty += prediction_option_user.wager

        user.save()

    # Update status
    prediction.status = PredictionStatus.RESULT_SET
    prediction.result_set_date = datetime.now()
    prediction.save()

    # Refresh prediction
    refresh(context, prediction)

    # Send message in reply notifying users that results are set
    full_message_send(context, phrases.PREDICTION_RESULTS_SET, chat_id=Env.OPD_GROUP_ID.get(),
                      reply_to_message_id=prediction.message_id)

    # Send notification to users
    for user_id, value in users_total_win.items():
        user: User = value[0]
        total_win: int = value[1]
        user_prediction_options: list[PredictionOption] = value[2]

        notification: PredictionResultNotification = PredictionResultNotification(
            prediction, user_prediction_options, prediction_options_correct, total_win)

        send_notification(context, user, notification)


def refresh(context: CallbackContext, prediction: Prediction) -> None:
    """
    Refresh prediction
    :param context: Telegram context
    :param prediction: Prediction
    """
    if PredictionStatus(prediction.status) is PredictionStatus.NEW:
        raise PredictionException(phrases.PREDICTION_NOT_SENT)

    try:
        full_message_send(context, get_prediction_text(prediction), chat_id=Env.OPD_GROUP_ID.get(),
                          edit_message_id=prediction.message_id)
    except BadRequest as br:  # Tolerate if message text is the same
        if br.message != "Message is not modified: specified new message content and reply markup are exactly the " \
                         "same as a current content and reply markup of the message":
            raise br


def get_prediction_options_user(prediction: Prediction, user: User) -> list[PredictionOptionUser]:
    """
    Get all prediction options for a user
    :param prediction: Prediction
    :param user: User
    :return: List of prediction options user
    """

    result = (PredictionOptionUser.select()
              .join(PredictionOption)
              .where((PredictionOptionUser.prediction == prediction) & (PredictionOptionUser.user == user))
              .order_by(PredictionOption.number.asc()))

    return result


def get_prediction_options_users(prediction: Prediction) -> list[PredictionOptionUser]:
    """
    Get all prediction options users for a prediction
    :param prediction: Prediction
    :return: List of prediction options users
    """
    return PredictionOptionUser.select().where(PredictionOptionUser.prediction == prediction)


def get_prediction_option_user_win(prediction_option_user: PredictionOptionUser,
                                   prediction_options_users: list[PredictionOptionUser] = None,
                                   is_potential: bool = False) -> int:
    """
    Get prediction option user potential win
    :param prediction_option_user: PredictionOptionUser for which to get potential win
    :param prediction_options_users: List of PredictionOptionUser for the same prediction
    :param is_potential: If True, assume that the prediction option is correct
    :return: Prediction option user potential win
    """

    if prediction_options_users is None:
        prediction_options_users = get_prediction_options_users(prediction_option_user.prediction)

    total_wager = sum(prediction_option_user.wager for prediction_option_user in prediction_options_users)

    if not is_potential:
        total_correct_wager = sum(pou.wager for pou in prediction_options_users if pou.prediction_option.is_correct)
    else:
        total_correct_wager = sum(pou.wager for pou in prediction_options_users
                                  if pou.prediction_option == prediction_option_user.prediction_option)

    # What percent of the total correct wager is this user's wager
    percentage_of_correct_wager = get_percentage_from_value(prediction_option_user.wager, total_correct_wager)

    # How much is this percentage in the total wager
    value_from_total_wager = round_belly_up(get_value_from_percentage(total_wager, percentage_of_correct_wager))

    return value_from_total_wager


def send_scheduled_predictions(context: CallbackContext) -> None:
    """
    Send scheduled predictions
    :param context: Telegram context
    """

    # Select not sent predictions with send date in the past
    predictions: list[Prediction] = Prediction.select().where((Prediction.send_date.is_null(False))
                                                              & (Prediction.send_date <= datetime.now())
                                                              & (Prediction.status == PredictionStatus.NEW))

    for prediction in predictions:
        send(context, prediction)


def close_scheduled_predictions(context: CallbackContext) -> None:
    """
    Close scheduled predictions
    :param context: Telegram context
    """

    # Select sent predictions with end date in the past
    predictions: list[Prediction] = Prediction.select().where((Prediction.end_date.is_null(False))
                                                              & (Prediction.end_date <= datetime.now())
                                                              & (Prediction.status == PredictionStatus.SENT))

    for prediction in predictions:
        close_bets(context, prediction)


def remove_all_bets_from_active_predictions(context: CallbackContext) -> None:
    """
    Remove all bets from active predictions due to bounty reset
    :param context: Telegram context
    """

    # Select active predictions
    active_statuses = [PredictionStatus.SENT, PredictionStatus.BETS_CLOSED]
    predictions: list[Prediction] = Prediction.select().where(Prediction.status.in_(active_statuses))

    for prediction in predictions:
        PredictionOptionUser.delete().where(PredictionOptionUser.prediction == prediction).execute()
        if prediction.message_id is not None:  # Should always be true
            try:
                full_message_send(context, phrases.PREDICTION_ALL_BETS_REMOVED_FOR_BOUNTY_RESET,
                                  chat_id=Env.OPD_GROUP_ID.get(), reply_to_message_id=prediction.message_id,
                                  allow_sending_without_reply=False)
            except BadRequest as br:  # Log error if reply message is not found
                if 'Replied message not found' in br.message:
                    logging.error(f"Replied message not found for prediction {prediction.id}")
        else:
            logging.error(f"Prediction {prediction.id} has no message_id")
