from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.chat.common.screens.screen_prediction_bet_remove import validate
from src.model.GroupChat import GroupChat
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.model.enums.Command import Command
from src.model.error.CustomException import PredictionException
from src.service.message_service import full_message_send
from src.service.prediction_service import (
    refresh,
    delete_prediction_option_user,
    delete_prediction_option_for_user,
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

    try:
        validation_tuple = await validate(update, user, command, group_chat=group_chat)

        # Need single assignment to enable IDE type detection
        prediction: Prediction = validation_tuple[0]
        prediction_option: PredictionOption = validation_tuple[1]
        prediction_options_user: list[PredictionOptionUser] = validation_tuple[2]
    except PredictionException as pe:
        await full_message_send(context, pe.message, update=update, add_delete_button=True)
        return

    if prediction_option is None:
        # Remove all bets on this prediction
        for prediction_option_user in prediction_options_user:
            await delete_prediction_option_user(user, prediction_option_user)

        await full_message_send(
            context,
            phrases.PREDICTION_BET_REMOVE_ALL_SUCCESS,
            update=update,
            add_delete_button=True,
        )
    else:
        # Remove bet on this prediction option
        await delete_prediction_option_for_user(user, prediction_option)

        await full_message_send(
            context, phrases.PREDICTION_BET_REMOVE_SUCCESS, update=update, add_delete_button=True
        )

    # Update prediction text
    await refresh(context, prediction, group_chat=group_chat)
