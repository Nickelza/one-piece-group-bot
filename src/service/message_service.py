import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMedia, InputMediaPhoto,\
    InputMediaVideo, InputMediaAnimation
from telegram.ext import CallbackContext

import constants as c
from src.model.pojo.Keyboard import Keyboard
from src.model.SavedMedia import SavedMedia
from src.model.enums.SavedMediaType import SavedMediaType
import resources.phrases as phrases


def escape_invalid_markdown_chars(text: str) -> str:
    """
    Escape invalid markdown chars
    :param text: Text
    :return: Escaped text
    """

    escape_chars = r'~>#+-=|{}.!'

    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


def escape_valid_markdown_chars(text: str) -> str:
    """
    Escape valid markdown chars
    :param text: Text
    :return: Escaped text
    """

    escape_chars = r'_*[]()'

    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


def get_chat_id(update: Update = None, chat_id: int = None) -> int:
    """
    Get chat id
    :param update: Update object. Required if chat_id is None
    :param chat_id: Chat id. Required if update is None
    :return: Chat id
    """

    if chat_id is not None:
        return chat_id

    if update is None or update.effective_chat is None or update.effective_chat.id is None:
        raise Exception(phrases.EXCEPTION_CHAT_ID_NOT_PROVIDED)

    return update.effective_chat.id


def get_keyboard(keyboard: list[list[Keyboard]]) -> InlineKeyboardMarkup | None:
    """
    Get keyboard markup
    :param keyboard: Keyboard object
    :return: Keyboard markup
    """

    keyboard_markup = None
    if keyboard is not None:
        keyboard_list: list[list[InlineKeyboardButton]] = []
        for row in keyboard:
            keyboard_row: list[InlineKeyboardButton] = []
            for button in row:
                if button.url is not None:
                    keyboard_row.append(InlineKeyboardButton(button.text, url=button.url))
                else:
                    keyboard_row.append(InlineKeyboardButton(button.text, callback_data=button.callback_data))
            keyboard_list.append(keyboard_row)
        keyboard_markup = InlineKeyboardMarkup(keyboard_list)

    return keyboard_markup


def get_reply_message_id(update: Update = None, quote: bool = False, reply_message_id: int = None) -> int | None:
    """
    Get reply message id
    :param update: Update object. Required if reply_message_id is None
    :param quote: Quote message. Default: False
    :param reply_message_id: Reply message id. Default: None
    :return: Reply message id
    """

    if reply_message_id is not None:
        return reply_message_id

    if not quote:
        return None

    if update.message is None:
        raise Exception("No message to quote")
    else:
        return update.message.message_id


def full_message_send(context: CallbackContext, text: str, update: Update = None, chat_id: int | str = None,
                      keyboard: list[list[Keyboard]] = None, answer_callback: bool = False, show_alert: bool = False,
                      new_message: bool = False, disable_notification: bool = True, reply_message_id: bool = None,
                      parse_mode: str = c.TG_DEFAULT_PARSE_MODE, quote: bool = False, protect_content: bool = False,
                      disable_web_page_preview: bool = True, allow_sending_without_reply: bool = True) -> Message:
    """
    Send a message
    :param context: CallbackContext object
    :param text: Text to send
    :param update: Update object. Required if chat_id is None
    :param chat_id: Chat id. Required if update is None
    :param keyboard: Keyboard object
    :param answer_callback: If it is an answer callback
    :param show_alert: If to show an alert in the callback answer
    :param new_message: True if the message is a new message
    :param disable_notification: True if the message should not be displayed in the chat
    :param reply_message_id: Message ID to reply to
    :param parse_mode: Parse mode
    :param quote: True if the message should be quoted
    :param protect_content: True if the message should be protected from saving and forwarding
    :param disable_web_page_preview: True if the web page preview should be disabled
    :param allow_sending_without_reply: True if the message should be sent if message to be replied to is not found
    :return: Message
    """

    if text is not None and parse_mode == c.TG_PARSE_MODE_MARKDOWN and not answer_callback:
        text = escape_invalid_markdown_chars(text)

    chat_id = get_chat_id(update=update, chat_id=chat_id)
    keyboard_markup = get_keyboard(keyboard)

    # New message
    if new_message or update is None or update.callback_query is None:
        # Message in reply to
        reply_message_id = get_reply_message_id(update=update, quote=quote, reply_message_id=reply_message_id)

        return context.bot.send_message(text=text,
                                        chat_id=chat_id,
                                        reply_markup=keyboard_markup,
                                        disable_web_page_preview=disable_web_page_preview,
                                        parse_mode=parse_mode,
                                        disable_notification=disable_notification,
                                        reply_to_message_id=reply_message_id,
                                        allow_sending_without_reply=allow_sending_without_reply,
                                        protect_content=protect_content)

    # No message to edit or answer callback
    if update.callback_query is None:
        raise Exception(phrases.EXCEPTION_NO_EDIT_MESSAGE)

    # Answer callback
    if answer_callback:
        return context.bot.answer_callback_query(update.callback_query.id, text=text, show_alert=show_alert)

    # Edit message
    return context.bot.edit_message_text(text=text,
                                         chat_id=chat_id,
                                         reply_markup=keyboard_markup,
                                         parse_mode=parse_mode,
                                         disable_web_page_preview=disable_web_page_preview,
                                         message_id=update.callback_query.message.message_id)


def get_input_media_from_saved_media(saved_media: SavedMedia, caption: str = None,
                                     parse_mode: str = c.TG_DEFAULT_PARSE_MODE) -> InputMedia:
    """
    Get InputMedia object from SavedMedia object
    :param saved_media: SavedMedia object
    :param caption: Caption
    :param parse_mode: Parse mode
    :return: InputMedia object
    """

    match saved_media.type:
        case SavedMediaType.PHOTO:
            return InputMediaPhoto(media=saved_media.file_id, caption=caption, parse_mode=parse_mode)
        case SavedMediaType.VIDEO:
            return InputMediaVideo(media=saved_media.file_id, caption=caption, parse_mode=parse_mode)
        case SavedMediaType.ANIMATION:
            return InputMediaAnimation(media=saved_media.file_id, caption=caption, parse_mode=parse_mode)
        case _:
            raise Exception(phrases.EXCEPTION_SAVED_MEDIA_UNKNOWN_TYPE)


def full_media_send(context: CallbackContext, saved_media: SavedMedia = None, update: Update = None,
                    chat_id: int | str = None,  caption: str = None, keyboard: list[list[Keyboard]] = None,
                    answer_callback: bool = False, show_alert: bool = False, new_message: bool = False,
                    disable_notification: bool = True, reply_message_id: bool = None, protect_content: bool = False,
                    parse_mode: str = c.TG_DEFAULT_PARSE_MODE, quote: bool = False,
                    allow_sending_without_reply: bool = True, edit_only_keyboard: bool = False,
                    edit_only_caption_and_keyboard: bool = False) -> Message:
    """
    Send a media
    :param context: CallbackContext object
    :param saved_media: SavedMedia object
    :param update: Update object. Required if chat_id is None
    :param chat_id: Chat id. Required if update is None
    :param caption: Caption
    :param keyboard: Keyboard object
    :param answer_callback: If it is an answer callback
    :param show_alert: If to show an alert in the callback answer
    :param new_message: True if the message is a new message
    :param disable_notification: True if the message should not be displayed in the chat
    :param reply_message_id: Message ID to reply to
    :param protect_content: True if the message should be protected from saving and forwarding
    :param parse_mode: Parse mode
    :param quote: True if the message should be quoted
    :param allow_sending_without_reply: True if the message should be sent if message to be replied to is not found
    :param edit_only_keyboard: If only the keyboard should be edited
    :param edit_only_caption_and_keyboard: If only the caption and keyboard should be edited. If keyboard is None,
            it will be removed
    :return: Message
    """

    if caption is not None and parse_mode == c.TG_PARSE_MODE_MARKDOWN and not answer_callback:
        caption = escape_invalid_markdown_chars(caption)

    chat_id = get_chat_id(update=update, chat_id=chat_id)
    keyboard_markup = get_keyboard(keyboard)

    # New message
    if new_message or update is None or update.callback_query is None:
        reply_message_id = get_reply_message_id(update=update, quote=quote, reply_message_id=reply_message_id)

        match saved_media.type:
            # Photo
            case SavedMediaType.PHOTO.value:  # Photo
                return context.bot.send_photo(chat_id=chat_id,
                                              photo=saved_media.media_id,
                                              caption=caption,
                                              reply_markup=keyboard_markup,
                                              parse_mode=parse_mode,
                                              disable_notification=disable_notification,
                                              reply_to_message_id=reply_message_id,
                                              allow_sending_without_reply=allow_sending_without_reply,
                                              protect_content=protect_content)
            case SavedMediaType.VIDEO.value:  # Video
                return context.bot.send_video(chat_id=chat_id,
                                              video=saved_media.media_id,
                                              caption=caption,
                                              reply_markup=keyboard_markup,
                                              parse_mode=parse_mode,
                                              disable_notification=disable_notification,
                                              reply_to_message_id=reply_message_id,
                                              allow_sending_without_reply=allow_sending_without_reply,
                                              protect_content=protect_content)
            case SavedMediaType.ANIMATION.value:  # Animation
                return context.bot.send_animation(chat_id=chat_id,
                                                  animation=saved_media.media_id,
                                                  caption=caption,
                                                  reply_markup=keyboard_markup,
                                                  parse_mode=parse_mode,
                                                  disable_notification=disable_notification,
                                                  reply_to_message_id=reply_message_id,
                                                  allow_sending_without_reply=allow_sending_without_reply,
                                                  protect_content=protect_content)
            case _:
                raise ValueError(phrases.EXCEPTION_SAVED_MEDIA_UNKNOWN_TYPE.format(saved_media.type.name))

    # No message to edit or answer callback
    if update.callback_query is None:
        raise Exception(phrases.EXCEPTION_NO_EDIT_MESSAGE)

    # Answer callback
    if answer_callback:
        return context.bot.answer_callback_query(update.callback_query.id, text=caption, show_alert=show_alert)

    # Edit only keyboard
    if edit_only_keyboard:
        return context.bot.edit_message_reply_markup(chat_id=chat_id,
                                                     message_id=update.callback_query.message.message_id,
                                                     reply_markup=keyboard_markup)

    # Edit only caption and keyboard
    if edit_only_caption_and_keyboard:
        return context.bot.edit_message_caption(chat_id=chat_id,
                                                message_id=update.callback_query.message.message_id,
                                                caption=caption,
                                                reply_markup=keyboard_markup)

    # Edit full media
    input_media: InputMedia = get_input_media_from_saved_media(saved_media=saved_media, caption=caption)
    return context.bot.edit_message_media(chat_id=chat_id,
                                          message_id=update.callback_query.message.message_id,
                                          media=input_media,
                                          reply_markup=keyboard_markup)
