from pathlib import Path
from typing import Sequence, Optional

from telegram import Update, PhotoSize, UserProfilePhotos, File, ChatMember, Message
from telegram import User as TelegramUser, ChatMemberAdministrator
from telegram.constants import ChatMemberStatus
from telegram.error import BadRequest
from telegram.ext import ContextTypes

import constants as c
from src.model.Group import Group
from src.model.GroupChat import GroupChat
from src.model.UnmutedUser import UnmutedUser
from src.model.User import User
from src.model.enums.BossType import BossType
from src.model.enums.LeaderboardRank import PIRATE_KING
from src.model.error.CustomException import AnonymousAdminException
from src.service.leaderboard_service import get_current_leaderboard_rank
from src.utils.download_utils import generate_temp_file_path


async def get_user_profile_photo(update: Update) -> str | None:
    """
    Gets the user's profile photo
    :param update: Telegram update
    :return: The path of the user's profile photo
    """

    # Anonymous admin, no photo available
    if update.effective_message.sender_chat is not None:
        return None

    # Get users last photo
    photo_path: Optional[Path] = None
    try:
        # More verbose to get IDE hints
        user_profile_photos: UserProfilePhotos = await update.effective_user.get_profile_photos(
            limit=1
        )
        last_set_photos: Sequence[PhotoSize] = user_profile_photos.photos[0]
        last_set_photo: PhotoSize = last_set_photos[-1]
        file: File = await last_set_photo.get_file()
        photo_path: Path = await file.download_to_drive(
            generate_temp_file_path(c.TG_PROFILE_PHOTO_EXTENSION)
        )
    except (AttributeError, IndexError):
        pass

    return photo_path


def get_boss_type(user: User, group_chat: GroupChat = None) -> BossType | None:
    """
    Get the boss type of the user
    :param user: The user
    :param group_chat: The group chat
    :return: The boss type
    """

    if user.is_admin:
        return BossType.ADMIN

    if user.is_legendary_pirate():
        return BossType.LEGENDARY_PIRATE

    if get_current_leaderboard_rank(user, group_chat) == PIRATE_KING:
        return BossType.PIRATE_KING

    if user.is_warlord():
        return BossType.WARLORD

    if group_chat is not None:
        # Check for Pirate King in global leaderboard
        if get_current_leaderboard_rank(user) == PIRATE_KING:
            return BossType.PIRATE_KING

    return None


def user_is_boss(user: User, group_chat: GroupChat = None) -> bool:
    """
    Returns True if the user is a boss
    :param user: The user
    :param group_chat: The group chat chat
    :return: True if the user is a boss
    """

    return get_boss_type(user, group_chat) is not None


def user_is_muted(user: User, group_chat: GroupChat) -> bool:
    """
    Returns True if the user is muted
    :param user: The user
    :param group_chat: The group chat chat
    :return: True if the user is muted
    """

    if group_chat is None:
        return False

    if user_is_boss(user):
        return False

    if not group_chat.is_muted:
        return False

    return (
        UnmutedUser.get_or_none(UnmutedUser.user == user, UnmutedUser.group_chat == group_chat)
        is None
    )


async def get_chat_member(
    user: User,
    group_chat: GroupChat,
    update: Update = None,
    context: ContextTypes.DEFAULT_TYPE = None,
    tg_group_id: str = None,
) -> ChatMember | None:
    """
    Returns the chat member of the user
    :param user: The user
    :param group_chat: The group chat
    :param update: The update
    :param context: The context
    :param tg_group_id: The chat id
    :return: The chat member
    """

    if update is None and group_chat is None and tg_group_id is None:
        raise ValueError("update or group_chat or tg_group_id must be specified")

    if group_chat is not None and context is None:
        raise ValueError("context must be specified if group_chat is specified")

    from telegram.error import Forbidden

    try:
        if update is not None:
            return await update.effective_chat.get_member(int(user.tg_user_id))
        elif group_chat is not None:  # To avoid IDE warning
            group: Group = group_chat.group
            return await context.bot.get_chat_member(group.tg_group_id, str(user.tg_user_id))
        elif tg_group_id is not None:
            return await context.bot.get_chat_member(tg_group_id, str(user.tg_user_id))
        else:
            raise ValueError("update or group_chat must be specified")
    except (Forbidden, BadRequest):  # Bot kicked from the group chat or user not found
        return None


async def user_is_chat_member(
    user: User,
    update: Update = None,
    context: ContextTypes.DEFAULT_TYPE = None,
    group_chat: GroupChat = None,
    tg_group_id: str = None,
) -> bool:
    """
    Returns True if the user is a member of the chat
    :param user: The user
    :param update: The update
    :param context: The context
    :param group_chat: The group chat
    :param tg_group_id: The chat id
    :return: True if the user is a member of the chat
    """

    chat_member: ChatMember = await get_chat_member(user, group_chat, update, context, tg_group_id)
    return chat_member is not None and chat_member.status not in [
        ChatMemberStatus.LEFT,
        ChatMemberStatus.BANNED,
    ]


async def user_is_chat_admin(
    user: User,
    update: Update = None,
    context: ContextTypes.DEFAULT_TYPE = None,
    group_chat: GroupChat = None,
    tg_group_id: str = None,
) -> bool:
    """
    Returns True if the user is an admin of the chat
    :param user: The user
    :param update: The update
    :param context: The context
    :param group_chat: The group chat
    :param tg_group_id: The chat id
    :return: True if the user is an admin of the chat
    """

    chat_member: ChatMember = await get_chat_member(user, group_chat, update, context, tg_group_id)
    return chat_member is not None and chat_member.status in [
        ChatMemberStatus.OWNER,
        ChatMemberStatus.ADMINISTRATOR,
    ]


async def get_effective_tg_user_id(
    effective_user: TelegramUser, effective_message: Message
) -> str:
    """
    Get the effective Telegram user ID, even if anonymous admin
    :param effective_user: The effective user
    :param effective_message: The effective message
    :return: The effective Telegram user ID
    """

    if effective_message.sender_chat is None:
        return str(effective_user.id)

    # Anonymous admin
    # Get all chat admins
    # noinspection PyTypeChecker
    chat_admins: list[ChatMemberAdministrator] = await effective_message.chat.get_administrators()

    if len(chat_admins) == 0:
        raise AnonymousAdminException()

    # Just 1 admin, must be the one that sent the message
    if len(chat_admins) == 1:
        return str(chat_admins[0].user.id)

    # Message without author signature, no way to determine user
    if effective_message.author_signature is None:
        raise AnonymousAdminException()

    # Get the admin with the same title as the author signature, if unique
    admins_with_same_title = [
        a for a in chat_admins if a.custom_title == effective_message.author_signature
    ]

    # No Admin with title, should never happen
    if len(admins_with_same_title) == 0:
        raise ValueError(f"Admin with title {effective_message.author_signature} not found")

    # More than one Admin with same title, no way to determine user
    if len(admins_with_same_title) > 1:
        raise AnonymousAdminException()

    return str(admins_with_same_title[0].user.id)
