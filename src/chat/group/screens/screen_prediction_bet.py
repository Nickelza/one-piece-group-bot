from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.chat.common.screens.screen_prediction_bet import validate
from src.model.GroupChat import GroupChat
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.User import User
from src.model.enums.Command import Command
from src.service.message_service import full_message_send
from src.service.prediction_service import (
    refresh,
    save_prediction_option_user,
)


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    command: Command,
    group_chat: GroupChat,
) -> None:
    """
    Manage the change region request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param command: The command
    :param group_chat: The group chat
    :return: None
    """
    validation_tuple = await validate(update, context, user, command, group_chat=group_chat)

    # Need single assignment to enable IDE type detection
    prediction: Prediction = validation_tuple[0]
    prediction_option: PredictionOption = validation_tuple[1]
    wager: int = validation_tuple[2]
    option_number: int = validation_tuple[3]

    if prediction is None or prediction_option is None or wager is None or option_number is None:
        return

    await save_prediction_option_user(prediction_option, user, wager)

    # Send success message
    ot_text = phrases.PREDICTION_BET_SUCCESS + phrases.PREDICTION_BET_HOW_TO_VIEW_BET_STATUS
    await full_message_send(context, ot_text, update=update, add_delete_button=True)

    # Update prediction text
    await refresh(context, prediction, group_chat=group_chat)
