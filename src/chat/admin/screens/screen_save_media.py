from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.SavedMedia import SavedMedia
from src.model.enums.SavedMediaType import SavedMediaType
from src.service.message_service import full_message_send, escape_valid_markdown_chars


def manage(update: Update, context: CallbackContext) -> None:
    """
    Manage the save media screen
    :param update: The update
    :param context: The context
    :return: None
    """

    message_parts = update.message.text.split(' ')
    if len(message_parts) != 2:
        update.message.reply_text(phrases.SAVE_MEDIA_INVALID_FORMAT)
        return

    name = message_parts[1]

    # Is in reply to a message
    if update.message.reply_to_message is None:
        full_message_send(context, phrases.COMMAND_NOT_IN_REPLY_ERROR, update)
        return

    # Is in reply to a media message
    if not (update.message.reply_to_message.animation is not None
            or (update.message.reply_to_message.photo is not None
                and len(update.message.reply_to_message.photo) > 0)
            or update.message.reply_to_message.sticker is not None):
        full_message_send(context, phrases.SAVE_MEDIA_NOT_IN_REPLY_TO_MEDIA, update)
        return

    # Save the media
    saved_media: SavedMedia = SavedMedia.get_or_none(SavedMedia.name == name)
    if saved_media is None:
        saved_media = SavedMedia()
        saved_media.name = name

    if update.message.reply_to_message.animation is not None:  # Animation
        saved_media.type = SavedMediaType.ANIMATION
        saved_media.media_id = update.message.reply_to_message.animation.file_id
    elif (update.message.reply_to_message.photo is not None
          and len(update.message.reply_to_message.photo) > 0):  # Photo
        saved_media.type = SavedMediaType.PHOTO
        saved_media.media_id = update.message.reply_to_message.photo[-1].file_id
    elif update.message.reply_to_message.video is not None:  # Video
        saved_media.type = SavedMediaType
        saved_media.media_id = update.message.reply_to_message.video.file_id
    else:  # Not supported
        accepted_types = [e.name for e in SavedMediaType]
        ot_text = phrases.SAVED_MEDIA_UNKNOWN_TYPE.format(str(accepted_types))
        full_message_send(context, ot_text, update)
        return

    saved_media.save()

    # Send the response
    ot_text = phrases.SAVE_MEDIA_SUCCESS.format(escape_valid_markdown_chars(name))
    full_message_send(context, ot_text, update)
