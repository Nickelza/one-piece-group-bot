from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.User import User
from src.service.message_service import full_message_send


def manage(update: Update, context: CallbackContext, user: User) -> None:
    """
    Manage the silence end screen
    :param update: The update object
    :param context: The context object
    :param user: The user
    :return: None
    """

    # Unmute all the users
    User.update(is_muted=False).execute()
    user.should_update_model = False

    # Confirmation message
    full_message_send(context, phrases.SILENCE_END, update=update)
