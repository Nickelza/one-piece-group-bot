from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.GroupChat import GroupChat
from src.model.UnmutedUser import UnmutedUser
from src.model.User import User
from src.service.message_service import full_message_send


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, target_user: User, group_chat: GroupChat) -> None:
    """
    Manage the speak screen
    :param update: The update object
    :param context: The context object
    :param target_user: The target user in case of a reply
    :param group_chat: The group chat
    :return: None
    """

    # Unmute target user
    unmuted_user: UnmutedUser = UnmutedUser()
    unmuted_user.user = target_user
    unmuted_user.group_chat = group_chat
    unmuted_user.save()

    # Confirmation message
    ot_text = phrases.SPEAK.format(target_user.get_markdown_mention())
    await full_message_send(context, ot_text, update=update)
