from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Prediction import Prediction
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.service.message_service import full_message_send
from src.service.prediction_service import get_prediction_options_user, get_user_prediction_status_text


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User
                   ) -> tuple[Prediction, list[PredictionOptionUser]] | tuple[None, None]:
    """
    Validate the prediction bet
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :return: None if validation failed or (prediction) if validation succeeded
    """

    error_tuple = None, None

    # Get prediction from message id
    prediction: Prediction = Prediction.get_or_none(Prediction.message_id == update.message.reply_to_message.message_id)
    if prediction is None:
        await full_message_send(context, phrases.PREDICTION_NOT_FOUND_IN_REPLY, update=update, add_delete_button=True)
        return error_tuple

    prediction_options_user: list[PredictionOptionUser] = get_prediction_options_user(prediction, user)

    return prediction, prediction_options_user


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User) -> None:
    """
    Manage the change region request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :return: None
    """
    validation_tuple = await validate(update, context, user)

    # Need single assignment to enable IDE type detection
    prediction: Prediction = validation_tuple[0]
    prediction_options_user: list[PredictionOptionUser] = validation_tuple[1]

    if prediction is None:
        return

    ot_text = get_user_prediction_status_text(prediction, user, prediction_options_user)
    await full_message_send(context, ot_text, update=update, add_delete_button=True)
