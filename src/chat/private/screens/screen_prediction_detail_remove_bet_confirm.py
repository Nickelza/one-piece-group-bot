from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.chat.group.screens.screen_prediction_bet_remove import validate
from src.chat.private.screens.screen_prediction_detail_remove_bet import PredictionRemoveBetReservedKeys, \
    manage as manage_prediction_detail_remove_bet
from src.model.PredictionOption import PredictionOption
from src.model.User import User
from src.model.error.CustomException import PredictionException
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send
from src.service.prediction_service import delete_prediction_option_for_user


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the prediction detail screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    prediction_option: PredictionOption = PredictionOption.get(
        PredictionOption.id == inbound_keyboard.get(PredictionRemoveBetReservedKeys.PREDICTION_OPTION_ID))

    await validate_and_delete(context, prediction_option, update, user)

    # Go back to the prediction detail remove bet screen
    await manage_prediction_detail_remove_bet(update, context, inbound_keyboard, user, called_from_remove_confirm=True)


async def validate_and_delete(context: ContextTypes.DEFAULT_TYPE, prediction_option, update, user):
    """
    Validate and delete the prediction option for the user if valid
    :param context: The context
    :param prediction_option: The prediction option
    :param update: The update
    :param user: The user
    """

    try:
        await validate(update, user, prediction_option=prediction_option)

        # Delete the prediction option for the user
        await delete_prediction_option_for_user(user, prediction_option)
        ot_text = phrases.PREDICTION_BET_REMOVE_SUCCESS
    except PredictionException as pe:
        ot_text = pe.message

    # Show alert message
    await full_message_send(context, ot_text, update=update, answer_callback=True, show_alert=True)
