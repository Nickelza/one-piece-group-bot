import datetime
import logging
from datetime import datetime

from telegram import Message
from telegram.error import BadRequest
from telegram.ext import ContextTypes

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


async def send(context: ContextTypes.DEFAULT_TYPE, prediction: Prediction, is_resent: bool = False) -> None:
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

    message: Message = await full_message_send(context, get_prediction_text(prediction), chat_id=Env.OPD_GROUP_ID.get())
    await message.pin(disable_notification=True)

    prediction.message_id = message.message_id
    prediction.save()


def get_prediction_text(prediction: Prediction, add_bets_command: bool = True) -> str:
    """
    Get prediction text
    :param prediction: Prediction
    :param add_bets_command: If to add commands on how to place and remove bets
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
    if prediction.refund_wager:
        enabled_emoji = Emoji.PREDICTION_FEATURE_ENABLED
        max_refund_text = phrases.PREDICTION_WAGERS_REFUNDED_MAX.format(
            get_belly_formatted(prediction.max_refund_wager))
    else:
        enabled_emoji = Emoji.PREDICTION_FEATURE_DISABLED
        max_refund_text = ""
    optional_text += phrases.PREDICTION_WAGERS_REFUNDED.format(enabled_emoji, max_refund_text)

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
    if add_bets_command:
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


def get_user_prediction_status_text(prediction: Prediction, user: User,
                                    prediction_options_user: list[PredictionOptionUser] = None, add_header: bool = True,
                                    add_bets_command: bool = True) -> str:
    """
    Get the prediction status text
    :param prediction: The prediction
    :param user: The user
    :param prediction_options_user: The options the user has bet on
    :param add_header: Whether to add the "Bets" header
    :param add_bets_command: Whether to add the command to remove all bets
    :return: The prediction status text
    """

    if prediction_options_user is None:
        prediction_options_user = get_prediction_options_user(prediction, user)

    if len(prediction_options_user) == 0:
        return phrases.PREDICTION_BET_USER_HAS_NOT_BET

    total_win_amount = 0
    total_win_count = 0
    total_loss_count = 0
    prediction_status: PredictionStatus = PredictionStatus(prediction.status)
    ot_text = phrases.PREDICTION_STATUS_BETS_HEADER if add_header else ""

    for prediction_option_user in prediction_options_user:
        prediction_option: PredictionOption = prediction_option_user.prediction_option

        # Option
        ot_text += phrases.PREDICTION_STATUS_OPTION.format(prediction_option.number,
                                                           escape_valid_markdown_chars(prediction_option.option),
                                                           get_belly_formatted(prediction_option_user.wager))

        # If the prediction results are not set, assume the option is correct
        is_potential = prediction_status is not PredictionStatus.RESULT_SET

        potential_win_amount = get_prediction_option_user_win(prediction_option_user,
                                                              is_potential=is_potential)

        potential_win_amount_formatted = get_belly_formatted(potential_win_amount)

        # Result not set, add potential win
        if prediction_status is not PredictionStatus.RESULT_SET:
            ot_text += phrases.PREDICTION_STATUS_POTENTIAL_WIN.format(potential_win_amount_formatted)
        else:
            # Result set, add win or loss amount
            if prediction_option.is_correct:
                ot_text += phrases.PREDICTION_STATUS_RESULT_WIN.format(potential_win_amount_formatted)
                total_win_amount += potential_win_amount
                total_win_count += 1
            else:
                ot_text += phrases.PREDICTION_STATUS_RESULT_LOST
                total_win_amount -= prediction_option_user.wager if not prediction.refund_wager else 0
                total_loss_count += 1

                # Wagers are refunded
                if prediction.refund_wager:
                    ot_text += phrases.PREDICTION_STATUS_RESULT_LOSS_REFUNDED

    # Multiple bet options
    if len(prediction_options_user) > 1:
        # Result set, show net win or loss amount
        if prediction_status is PredictionStatus.RESULT_SET:
            if total_win_amount >= 0:  # Won
                if total_loss_count > 0:  # At least one option was wrong, show net win
                    ot_text += phrases.PREDICTION_STATUS_NET_WIN.format(get_belly_formatted(total_win_amount))
                else:  # All options were correct, show total win
                    ot_text += phrases.PREDICTION_STATUS_TOTAL_WIN.format(get_belly_formatted(total_win_amount))
            else:
                total_loss_amount = abs(total_win_amount)
                if total_win_count > 0:  # At least one option was correct, show net loss
                    ot_text += phrases.PREDICTION_STATUS_NET_LOSS.format(get_belly_formatted(total_loss_amount))
                else:  # All options were wrong, show total loss
                    ot_text += phrases.PREDICTION_STATUS_TOTAL_LOSS.format(get_belly_formatted(total_loss_amount))
        # Open prediction, show command to remove single bet
        elif add_bets_command and prediction_status is PredictionStatus.SENT and prediction.can_withdraw_bet:
            ot_text += phrases.PREDICTION_BET_HOW_TO_REMOVE_BET

    # Open prediction, show command to remove all bets
    if add_bets_command and prediction_status is PredictionStatus.SENT and prediction.can_withdraw_bet:
        ot_text += phrases.PREDICTION_BET_HOW_TO_REMOVE_ALL_BETS

    return ot_text


async def close_bets(context: ContextTypes.DEFAULT_TYPE, prediction: Prediction) -> None:
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
    await refresh(context, prediction)

    # Send message in reply notifying users that bets are closed
    await full_message_send(context, phrases.PREDICTION_CLOSED_FOR_BETS, chat_id=Env.OPD_GROUP_ID.get(),
                            reply_to_message_id=prediction.message_id)

    # Send notification to users
    for user_id, value in users_invalid_prediction_options.items():
        user: User = value[0]
        prediction_options_user = value[1]
        total_refund = value[2]

        notification: PredictionBetInvalidNotification = PredictionBetInvalidNotification(
            prediction, prediction_options_user, total_refund)

        await send_notification(context, user, notification)


async def set_results(context: ContextTypes.DEFAULT_TYPE, prediction: Prediction) -> None:
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
            await add_bounty(user, win_amount, pending_belly_amount=prediction_option_user.wager)

            # Add to total win
            users_total_win[user.id][1] += win_amount
        else:
            # Remove from total win
            users_total_win[user.id][1] -= prediction_option_user.wager

        # Subtract bet wager from user pending bounty
        user.pending_bounty -= prediction_option_user.wager

        # Should refund wager or no correct options
        if prediction.refund_wager or len(prediction_options_correct) == 0:
            if len(prediction_options_correct) == 0:
                # No correct options, refund full wager
                user.bounty += prediction_option_user.wager
            else:
                # Cap refund
                user.bounty += min(prediction_option_user.wager, prediction.max_refund_wager)

        user.save()

    # Update status
    prediction.status = PredictionStatus.RESULT_SET
    prediction.result_set_date = datetime.now()
    prediction.save()

    # Refresh prediction
    await refresh(context, prediction)

    # Send message in reply notifying users that results are set
    await full_message_send(context, phrases.PREDICTION_RESULTS_SET, chat_id=Env.OPD_GROUP_ID.get(),
                            reply_to_message_id=prediction.message_id)

    # Send notification to users
    for user_id, value in users_total_win.items():
        user: User = value[0]
        total_win: int = value[1]
        user_prediction_options: list[PredictionOption] = value[2]

        notification: PredictionResultNotification = PredictionResultNotification(
            prediction, user_prediction_options, prediction_options_correct, total_win)

        await send_notification(context, user, notification)


async def refresh(context: ContextTypes.DEFAULT_TYPE, prediction: Prediction) -> None:
    """
    Refresh prediction
    :param context: Telegram context
    :param prediction: Prediction
    """
    if PredictionStatus(prediction.status) is PredictionStatus.NEW:
        raise PredictionException(phrases.PREDICTION_NOT_SENT)

    try:
        await full_message_send(context, get_prediction_text(prediction), chat_id=Env.OPD_GROUP_ID.get(),
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


async def send_scheduled_predictions(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send scheduled predictions
    :param context: Telegram context
    """

    # Select not sent predictions with send date in the past
    predictions: list[Prediction] = Prediction.select().where((Prediction.send_date.is_null(False))
                                                              & (Prediction.send_date <= datetime.now())
                                                              & (Prediction.status == PredictionStatus.NEW))

    for prediction in predictions:
        await send(context, prediction)


async def close_scheduled_predictions(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Close scheduled predictions
    :param context: Telegram context
    """

    # Select sent predictions with end date in the past
    predictions: list[Prediction] = Prediction.select().where((Prediction.end_date.is_null(False))
                                                              & (Prediction.end_date <= datetime.now())
                                                              & (Prediction.status == PredictionStatus.SENT))

    for prediction in predictions:
        await close_bets(context, prediction)


async def remove_all_bets_from_active_predictions(context: ContextTypes.DEFAULT_TYPE) -> None:
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
                await full_message_send(context, phrases.PREDICTION_ALL_BETS_REMOVED_FOR_BOUNTY_RESET,
                                        chat_id=Env.OPD_GROUP_ID.get(), reply_to_message_id=prediction.message_id,
                                        allow_sending_without_reply=False)
            except BadRequest as br:  # Log error if reply message is not found
                if 'Replied message not found' in br.message:
                    logging.error(f"Replied message not found for prediction {prediction.id}")
        else:
            logging.error(f"Prediction {prediction.id} has no message_id")


def user_has_bet_on_prediction(prediction: Prediction, user: User) -> bool:
    """
    Check if user bet on prediction
    :param prediction: Prediction
    :param user: User
    :return: True if user bet on prediction
    """

    return len(get_prediction_options_user(prediction, user)) > 0


def get_user_prediction_status_emoji(prediction: Prediction, user: User) -> Emoji:
    """
    Get user prediction status emoji for a user
    :param prediction: Prediction
    :param user: User
    :return: User prediction status emoji
    """

    prediction_status = PredictionStatus(prediction.status)
    if user_has_bet_on_prediction(prediction, user):
        if prediction_status is PredictionStatus.SENT:
            return Emoji.PREDICTION_OPEN
        elif prediction_status is PredictionStatus.BETS_CLOSED:
            return Emoji.PREDICTION_CLOSED
        else:  # Result is set
            net_win = get_prediction_net_win(prediction, user)
            if net_win > 0:
                return Emoji.LOG_POSITIVE
            else:
                return Emoji.LOG_NEGATIVE
    else:  # If user didn't bet on prediction, and it's not open, it won't show up in the list
        return Emoji.PREDICTION_NEW


def get_prediction_net_win(prediction: Prediction, user: User) -> int:
    """
    Get net win for a user, without considering refunds, only for predictions with result set
    :param prediction: Prediction
    :param user: User
    :return: Net win
    """

    prediction_options_user: list[PredictionOptionUser] = get_prediction_options_user(prediction, user)

    if PredictionStatus(prediction.status) is not PredictionStatus.RESULT_SET:
        raise ValueError(f"Prediction {prediction.id} results are not set, so net win can't be calculated")

    net_win = 0
    for pou in prediction_options_user:
        prediction_option: PredictionOption = pou.prediction_option
        if prediction_option.is_correct:
            net_win += get_prediction_option_user_win(pou)
        else:
            net_win -= pou.wager

    return net_win


def save_prediction_option_user(prediction_option: PredictionOption, user: User, wager: int) -> PredictionOptionUser:
    """
    Save the prediction option user
    :param prediction_option: The prediction option
    :param user: The user
    :param wager: The wager
    :return: The prediction option user
    """
    # Find existing prediction option user if it exists
    prediction_option_user: PredictionOptionUser = PredictionOptionUser.get_or_none(
        (PredictionOptionUser.user == user)
        & (PredictionOptionUser.prediction_option == prediction_option))
    # User has already bet on this option, add the wager to the existing bet
    if prediction_option_user is not None:
        prediction_option_user.wager += wager
    else:
        # Create prediction option user
        prediction_option_user = PredictionOptionUser()
        prediction_option_user.prediction = prediction_option.prediction
        prediction_option_user.prediction_option = prediction_option
        prediction_option_user.user = user
        prediction_option_user.wager = wager
    prediction_option_user.date = datetime.now()
    prediction_option_user.save()

    return prediction_option_user


def delete_prediction_option_user(user: User, prediction_option_user: PredictionOptionUser) -> None:
    """
    Delete a prediction option user
    :param user: The user object
    :param prediction_option_user: The prediction option user
    :return: None
    """
    # Return wager
    user.pending_bounty -= prediction_option_user.wager
    user.bounty += prediction_option_user.wager

    # Delete prediction option user
    prediction_option_user.delete_instance()


def delete_prediction_option_for_user(user: User, prediction_option: PredictionOption) -> None:
    """
    Delete a prediction option for a user
    :param user: The user object
    :param prediction_option: The prediction option
    :return: None
    """
    prediction_option_user: PredictionOptionUser = PredictionOptionUser.get_or_none(
        (PredictionOptionUser.user == user) & (PredictionOptionUser.prediction_option == prediction_option))

    if prediction_option_user is not None:  # Should always be true
        delete_prediction_option_user(user, prediction_option_user)
