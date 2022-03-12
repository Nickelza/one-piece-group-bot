from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.service.message_service import full_message_send


def manage(update: Update, context: CallbackContext) -> None:
    """
    Manage the bounty screen.
    """

    full_message_send(context, phrases.SHOW_BOUNTY_DEPRECATED, update)
