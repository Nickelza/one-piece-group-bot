from telegram import Update, PhotoSize
from telegram.constants import CHATMEMBER_CREATOR, CHATMEMBER_ADMINISTRATOR

import constants as c
from src.model.User import User
from src.model.enums.LeaderboardRank import PIRATE_KING
from src.service.download_service import generate_temp_file_path
from src.service.leaderboard_service import get_current_leaderboard_rank


def get_user_profile_photo(update: Update) -> str | None:
    """
    Gets the user's profile photo
    :param update: Telegram update
    :return: The path of the user's profile photo
    """

    # Get users last photo
    photo_path = None
    try:
        photo: PhotoSize = update.effective_user.get_profile_photos(limit=1).photos[0][-1]
        photo_path = photo.get_file().download(generate_temp_file_path(c.TG_PROFILE_PHOTO_EXTENSION))
    except (AttributeError, IndexError):
        pass

    return photo_path


def user_is_boss(user: User, update: Update) -> bool:
    """
    Returns True if the user is a boss
    :param user: The user
    :param update: The update
    :return: True if the user is a boss
    """

    # Is admin field
    if user.is_admin:
        return True

    # User is chat admin
    if update.effective_chat.get_member(user.tg_user_id).status in [CHATMEMBER_CREATOR, CHATMEMBER_ADMINISTRATOR]:
        return True

    # User is Pirate King
    if get_current_leaderboard_rank(user) == PIRATE_KING:
        return True

    return False


def user_is_muted(user: User, update: Update) -> bool:
    """
    Returns True if the user is muted
    :param user: The user
    :param update: The update
    :return: True if the user is muted
    """

    return user.is_muted and not user_is_boss(user, update)
