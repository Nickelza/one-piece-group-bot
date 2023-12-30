from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.GroupChat import GroupChat
from src.model.UnmutedUser import UnmutedUser
from src.model.enums.SavedMediaName import SavedMediaName
from src.service.message_service import full_media_send


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, group_chat: GroupChat
) -> None:
    """
    Manage the silence screen
    :param update: The update object
    :param context: The context object
    :param group_chat: The group chat
    :return: None
    """

    group_chat.is_muted = True
    group_chat.save()

    UnmutedUser.delete().where(UnmutedUser.group_chat == group_chat).execute()

    # Confirmation message
    await full_media_send(
        context,
        saved_media_name=SavedMediaName.SILENCE,
        update=update,
        caption=phrases.SILENCE_ACTIVE,
    )
