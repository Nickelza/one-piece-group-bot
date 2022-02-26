from telegram import Update
from telegram.ext import CallbackContext

from src.service.message_service import full_message_send


def manage(update: Update, context: CallbackContext) -> None:
    """
    Manage the start screen
    :param update: The update
    :param context: The context
    :return: None
    """

    text = "Welcome to @onepiecegroup Bot\\!"
    full_message_send(context, text, update)
