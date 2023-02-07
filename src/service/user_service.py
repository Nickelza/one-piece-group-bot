from pathlib import Path
from typing import Sequence, Optional

from telegram import Update, PhotoSize, UserProfilePhotos, File

import constants as c
from src.model.Group import Group
from src.model.LegendaryPirate import LegendaryPirate
from src.model.Topic import Topic
from src.model.UnmutedUser import UnmutedUser
from src.model.User import User
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


async def user_is_boss(user: User) -> bool:
    """
    Returns True if the user is a boss
    :param user: The user
    :return: True if the user is a boss
    """

    # Is admin field
    if user.is_admin:
        return True

    # User is Pirate King
    if get_current_leaderboard_rank(user) == PIRATE_KING:
        return True

    # User is a Legendary Pirate
    if LegendaryPirate.get_or_none(LegendaryPirate.user == user) is not None:
        return True

    return False


async def user_is_muted(user: User, group: Group, topic: Topic) -> bool:
    """
    Returns True if the user is muted
    :param user: The user
    :param group: The group
    :param topic: The topic
    :return: True if the user is muted
    """

    if topic:
        if not topic.is_muted:
            return False
    elif not group.is_muted:  # Don't check if group is muted if in a topic
        return False

    if await user_is_boss(user):
        return False

    return (UnmutedUser
            .get_or_none(UnmutedUser.user == user, UnmutedUser.group == group, UnmutedUser.topic == topic) is None)
