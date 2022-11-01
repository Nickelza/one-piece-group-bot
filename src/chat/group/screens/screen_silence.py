from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.SavedMedia import SavedMedia
from src.model.User import User
from src.model.enums.SavedMediaName import SavedMediaName
from src.service.message_service import full_media_send


def manage(update: Update, context: CallbackContext, user: User) -> None:
    """
    Manage the silence screen
    :param update: The update object
    :param context: The context object
    :param user: The user
    :return: None
    """

    # Mutes all the users
    User.update(is_muted=True).execute()
    user.should_update_model = False

    # Confirmation message
    silence_media = SavedMedia.logical_get(SavedMediaName.SILENCE)
    full_media_send(context, silence_media, update=update, caption=phrases.SILENCE_ACTIVE)
