from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Group import Group
from src.model.Topic import Topic
from src.model.UnmutedUser import UnmutedUser
from src.model.enums.SavedMediaName import SavedMediaName
from src.service.message_service import full_media_send


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, group: Group, topic: Topic) -> None:
    """
    Manage the silence screen
    :param update: The update object
    :param context: The context object
    :param group: The group
    :param topic: The topic
    :return: None
    """

    if topic:
        topic.is_muted = True
        topic.save()
    else:
        group.is_muted = True
        group.save()

    UnmutedUser.delete().where(UnmutedUser.group == group, UnmutedUser.topic == topic).execute()

    # Confirmation message
    await full_media_send(
        context, saved_media_name=SavedMediaName.SILENCE, update=update, caption=phrases.SILENCE_ACTIVE)
