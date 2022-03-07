from telegram import Update, PhotoSize

import constants as c
from src.service.download_service import generate_temp_file_path


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
