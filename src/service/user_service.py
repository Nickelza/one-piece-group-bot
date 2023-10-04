from pathlib import Path
from typing import Sequence, Optional

from telegram import Update, PhotoSize, UserProfilePhotos, File

import constants as c
from src.model.GroupChat import GroupChat
from src.model.LegendaryPirate import LegendaryPirate
from src.model.UnmutedUser import UnmutedUser
from src.model.User import User
from src.model.enums.BossType import BossType
from src.model.enums.LeaderboardRank import PIRATE_KING
from src.service.download_service import generate_temp_file_path
from src.service.leaderboard_service import get_current_leaderboard_rank


async def get_user_profile_photo(update: Update) -> str | None:
    """
    Gets the user's profile photo
    :param update: Telegram update
    :return: The path of the user's profile photo
    """

    # Get users last photo
    photo_path: Optional[Path] = None
    try:
        # More verbose to get IDE hints
        user_profile_photos: UserProfilePhotos = await update.effective_user.get_profile_photos(limit=1)
        last_set_photos: Sequence[PhotoSize] = user_profile_photos.photos[0]
        last_set_photo: PhotoSize = last_set_photos[-1]
        file: File = await last_set_photo.get_file()
        photo_path: Path = await file.download_to_drive(generate_temp_file_path(c.TG_PROFILE_PHOTO_EXTENSION))
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

    if LegendaryPirate.get_or_none(LegendaryPirate.user == user) is not None:
        return BossType.LEGENDARY_PIRATE

    if get_current_leaderboard_rank(user, group_chat) == PIRATE_KING:
        return BossType.PIRATE_KING

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

    return (UnmutedUser
            .get_or_none(UnmutedUser.user == user, UnmutedUser.group_chat == group_chat) is None)
