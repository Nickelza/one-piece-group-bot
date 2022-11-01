from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.User import User
from src.service.message_service import full_message_send


def manage(update: Update, context: CallbackContext, target_user: User) -> None:
    """
    Manage the speak screen
    :param update: The update object
    :param context: The context object
    :param target_user: The target user in case of a reply
    :return: None
    """

    # Unmute target user
    target_user.is_muted = False
    target_user.save()

    # Confirmation message
    ot_text = phrases.SPEAK.format(target_user.get_markdown_mention())
    full_message_send(context, ot_text, update=update)
