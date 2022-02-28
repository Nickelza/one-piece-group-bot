from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.service.message_service import full_message_send


def manage(update: Update, context: CallbackContext) -> None:
    """
    Manage the start screen
    :param update: The update
    :param context: The context
    :return: None
    """

    full_message_send(context, phrases.PVT_CHAT_START, update)
