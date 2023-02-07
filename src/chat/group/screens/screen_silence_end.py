from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Group import Group
from src.model.Topic import Topic
from src.model.UnmutedUser import UnmutedUser
from src.service.message_service import full_message_send


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, group: Group, topic: Topic) -> None:
    """
    Manage the silence end screen
    :param update: The update object
    :param context: The context object
    :param group: The group
    :param topic: The topic
    :return: None
    """

    if topic:
        topic.is_muted = False
        topic.save()
    else:
        group.is_muted = False
        group.save()

    UnmutedUser.delete().where(UnmutedUser.group == group, UnmutedUser.topic == topic).execute()

    # Confirmation message
    await full_message_send(context, phrases.SILENCE_END, update=update)
