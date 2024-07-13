from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.GroupChat import GroupChat
from src.model.UnmutedUser import UnmutedUser
from src.service.message_service import full_message_send


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, group_chat: GroupChat
) -> None:
    """
    Manage the silence end screen
    :param update: The update object
    :param context: The context object
    :param group_chat: The group chat
    :return: None
    """

    if not group_chat.is_muted:
        await full_message_send(
            context, phrases.SILENCE_NOT_ACTIVE, update=update, add_delete_button=True
        )
        return

    group_chat.is_muted = False
    group_chat.save()

    UnmutedUser.delete().where(UnmutedUser.group_chat == group_chat).execute()

    # Confirmation message
    await full_message_send(context, phrases.SILENCE_END, update=update, add_delete_button=True)
