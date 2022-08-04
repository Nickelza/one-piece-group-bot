import datetime

from telegram import Message
from telegram.error import BadRequest
from telegram.ext import CallbackContext

import resources.Environment as Env
import resources.phrases as phrases
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.enums.PredictionStatus import PredictionStatus, get_prediction_status_name_by_key
from src.model.error.CustomException import PredictionException
from src.service.math_service import get_percentage_from_value
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
    prediction_options_users: list[PredictionOptionUser] = PredictionOptionUser.select().where(
        PredictionOptionUser.prediction_option.in_(prediction_options))
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
            len(prediction_option_users)
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


def set_results(context: CallbackContext, prediction: Prediction) -> None:
    """
    Set results
    :param context: Telegram context
    :param prediction: Prediction
    """
    if PredictionStatus(prediction.status) is not PredictionStatus.BETS_CLOSED:
        raise PredictionException(phrases.PREDICTION_NOT_IN_BETS_CLOSED_STATUS)


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
