from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.GroupChat import GroupChat
from src.model.Prediction import Prediction
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.service.message_service import full_message_send
from src.service.prediction_service import get_prediction_options_user, get_user_prediction_status_text, \
    get_prediction_from_message_id, refresh


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, group_chat: GroupChat = None
                   ) -> tuple[Prediction, list[PredictionOptionUser]] | tuple[None, None]:
    """
    Validate the prediction bet
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param group_chat: The group chat from which to get the prediction if getting from message id
    :return: None if validation failed or (prediction) if validation succeeded
    """

    error_tuple = None, None

    # Get prediction from message id
    prediction: Prediction = get_prediction_from_message_id(group_chat, update.message.reply_to_message.message_id)
    if prediction is None:
        await full_message_send(context, phrases.PREDICTION_NOT_FOUND_IN_REPLY, update=update, add_delete_button=True)
        return error_tuple

    prediction_options_user: list[PredictionOptionUser] = get_prediction_options_user(prediction, user)

    return prediction, prediction_options_user


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, group_chat: GroupChat) -> None:
    """
    Manage the change region request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param group_chat: The group chat
    :return: None
    """
    validation_tuple = await validate(update, context, user, group_chat=group_chat)

    # Need single assignment to enable IDE type detection
    prediction: Prediction = validation_tuple[0]
    prediction_options_user: list[PredictionOptionUser] = validation_tuple[1]

    if prediction is None:
        return

    ot_text = get_user_prediction_status_text(prediction, user, prediction_options_user)
    await full_message_send(context, ot_text, update=update, add_delete_button=True)

    await refresh(context, prediction, group_chat=group_chat)
