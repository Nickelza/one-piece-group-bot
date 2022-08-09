import datetime

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
from src.model.enums.PredictionStatus import PredictionStatus, get_prediction_status_name_by_key
from src.model.error.CustomException import PredictionException
from src.service.bounty_service import round_belly_up, add_bounty
from src.service.math_service import get_percentage_from_value, get_value_from_percentage
from src.service.message_service import escape_valid_markdown_chars, full_message_send


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

        prediction.status = PredictionStatus.SENT.value
        prediction.send_date = datetime.datetime.now()

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
            (Emoji.CORRECT.value if prediction_option.is_correct else "")
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
    optional_text += phrases.PREDICTION_WAGERS_REFUNDED if prediction.refund_wager else ""
    # Multiple bets allowed
    optional_text += phrases.PREDICTION_MULTIPLE_BETS_ALLOWED if prediction.allow_multiple_choices else ""
    # Bet withdrawal allowed
    optional_text += phrases.PREDICTION_CAN_WITHDRAW_BETS if prediction.can_withdraw_bet else ""

    # Append \n if not empty
    optional_text = "\n" + optional_text if optional_text != "" else ""
    added_text += optional_text

    # Prediction text
    prediction_text = phrases.PREDICTION_TEXT.format(
        escape_valid_markdown_chars(prediction.question),
        options_text,
        get_prediction_status_name_by_key(PredictionStatus(prediction.status)),
        added_text)

    return prediction_text


def close_bets(context: CallbackContext, prediction: Prediction) -> None:
    """
    Close bets
    :param context: Telegram context
    :param prediction: Prediction
    """
    if PredictionStatus(prediction.status) is not PredictionStatus.SENT:
        raise PredictionException(phrases.PREDICTION_NOT_IN_SENT_STATUS)

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

            invalid_prediction_option_user.delete_instance()

    # Update status
    prediction.status = PredictionStatus.BETS_CLOSED.value
    prediction.end_date = datetime.datetime.now()
    prediction.save()

    # Update prediction message
    refresh(context, prediction)

    # Send message in reply notifying users that bets are closed
    full_message_send(context, phrases.PREDICTION_CLOSED_FOR_BETS, chat_id=Env.OPD_GROUP_ID.get(),
                      reply_to_message_id=prediction.message_id)


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

    total_wager = sum(prediction_option_user.wager for prediction_option_user in prediction_options_users)
    total_correct_wager = sum(prediction_option_user.wager for prediction_option_user in prediction_options_users
                              if prediction_option_user.prediction_option.is_correct)

    for prediction_option_user in prediction_options_users:
        user: User = prediction_option_user.user

        # Correct prediction
        if prediction_option_user.prediction_option.is_correct:
            # What percent of the total correct wager is this user's wager
            percentage_of_correct_wager = get_percentage_from_value(prediction_option_user.wager, total_correct_wager)

            # How much is this percentage in the total wager
            value_from_total_wager = round_belly_up(get_value_from_percentage(total_wager, percentage_of_correct_wager))

            # Add to bounty
            user = add_bounty(user, value_from_total_wager, pending_belly_amount=prediction_option_user.wager)

        # Subtract bet wager from user pending bounty
        user.pending_bounty -= prediction_option_user.wager

        # Should refund wager or no correct options
        if prediction.refund_wager or len(prediction_options_correct) == 0:
            user.bounty += prediction_option_user.wager

        user.save()

    # Update status
    prediction.status = PredictionStatus.RESULT_SET.value
    prediction.result_set_date = datetime.datetime.now()
    prediction.save()

    # Refresh prediction
    refresh(context, prediction)

    # Send message in reply notifying users that results are set
    full_message_send(context, phrases.PREDICTION_RESULTS_SET, chat_id=Env.OPD_GROUP_ID.get(),
                      reply_to_message_id=prediction.message_id)


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

    return PredictionOptionUser.select().where((PredictionOptionUser.prediction == prediction)
                                               & (PredictionOptionUser.user == user))


def get_prediction_options_users(prediction: Prediction) -> list[PredictionOptionUser]:
    """
    Get all prediction options users for a prediction
    :param prediction: Prediction
    :return: List of prediction options users
    """
    return PredictionOptionUser.select().where(PredictionOptionUser.prediction == prediction)
