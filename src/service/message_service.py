import json
import logging
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message, InputMedia, InputMediaPhoto, \
    InputMediaVideo, InputMediaAnimation, Chat
from telegram.error import BadRequest, TelegramError
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_markdown

import constants as c
import resources.Environment as Env
import resources.phrases as phrases
from src.model.SavedMedia import SavedMedia
from src.model.User import User
from src.model.enums.MessageSource import MessageSource
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.SavedMediaType import SavedMediaType
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard


def escape_invalid_markdown_chars(text: str) -> str:
    """
    Escape invalid markdown chars
    :param text: Text
    :return: Escaped text
    """

    escape_chars = r'~>#+-=|{}.!'

    text = re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)

    # Escape eventual quadruple backslashes with a double backslash
    text = text.replace('\\\\', '\\')

    return text


def escape_valid_markdown_chars(text: str) -> str:
    """
    Escape valid markdown chars
    :param text: Text
    :return: Escaped text
    """

    escape_chars = r'_*[]()'

    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)


def get_chat_id(update: Update = None, chat_id: int = None, send_in_private_chat: bool = False) -> int:
    """
    Get chat id
    :param update: Update object. Required if chat_id is None
    :param chat_id: Chat id. Required if update is None
    :param send_in_private_chat: Send in private chat. Default: False
    :return: Chat id
    """

    if chat_id is not None:
        return chat_id

    if update is None or update.effective_chat is None or update.effective_chat.id is None:
        raise Exception(phrases.EXCEPTION_CHAT_ID_NOT_PROVIDED)

    if send_in_private_chat:
        return update.effective_user.id

    return update.effective_chat.id


def get_keyboard(keyboard: list[list[Keyboard]], update: Update = None, add_delete_button: bool = False,
                 authorized_users_tg_ids: list = None, inbound_keyboard: Keyboard = None,
                 only_authorized_users_can_interact: bool = True, excluded_keys_from_back_button: list[str] = None
                 ) -> InlineKeyboardMarkup | None:
    """
    Get keyboard markup
    :param keyboard: Keyboard object
    :param update: Update object
    :param add_delete_button: True if the delete button should be added
    :param authorized_users_tg_ids: List of user ids that are allowed to delete the message
    :param inbound_keyboard: Inbound Keyboard object
    :param only_authorized_users_can_interact: True if only authorized users can interact with the keyboard
    :param excluded_keys_from_back_button: List of keys that should not be added to the back button info
    :return: Keyboard markup
    """

    # Do not validate user interaction for private chats
    if update is not None:
        message_source = get_message_source(update)
        if message_source is MessageSource.ND:
            only_authorized_users_can_interact = False

    if authorized_users_tg_ids is None:
        authorized_users_tg_ids = []
    try:
        if update.effective_user.id not in authorized_users_tg_ids:
            authorized_users_tg_ids.append(update.effective_user.id)
    except AttributeError:
        pass

    authorized_users_ids: list[int] = []
    for tg_user_id in authorized_users_tg_ids:
        user = User.get_or_none(User.tg_user_id == tg_user_id)
        if user is not None:
            authorized_users_ids.append(user.id)

    keyboard_markup = None
    if keyboard is not None or add_delete_button is True or inbound_keyboard is not None:
        keyboard_list: list[list[InlineKeyboardButton]] = []
        if keyboard is not None:
            for row in keyboard:
                keyboard_row: list[InlineKeyboardButton] = []
                for button in row:
                    if button.url is not None:
                        keyboard_row.append(InlineKeyboardButton(button.text, url=button.url))
                    else:
                        # Already has some callback_data. If it has no data, nothing should be added
                        # callback_data is a string initialized for an empty dict, so even if empty the string will have
                        # value '{}'. So, to confirm that it is empty, we first revert to a dictionary and check if the
                        # dict is empty.
                        if json.loads(button.callback_data):
                            # Add information about previous screen
                            if inbound_keyboard is not None and inbound_keyboard.screen is not None:
                                button.previous_screen_list = inbound_keyboard.previous_screen_list.copy()
                                if button.previous_screen_list[-1] != inbound_keyboard.screen != button.screen:
                                    button.previous_screen_list.append(inbound_keyboard.screen)

                            # Add list of authorized users
                            if only_authorized_users_can_interact and button.inherit_authorized_users:
                                if update is not None and update.effective_chat.type != Chat.PRIVATE:
                                    button.info['u'] = authorized_users_ids
                            elif not button.inherit_authorized_users:
                                button.info['u'] = [u.id for u in button.authorized_users]

                            button.refresh_callback_data()

                        try:
                            keyboard_row.append(InlineKeyboardButton(button.text, callback_data=button.callback_data))
                        except AttributeError:
                            logging.error(f'Button {button} does not have a callback_data')
                            pass

                keyboard_list.append(keyboard_row)

        if add_delete_button is True:
            if not len(authorized_users_ids) > 0:
                raise Exception("No authorized users provided for delete button")

            delete_button = get_delete_button(authorized_users_ids)
            keyboard_list.append([InlineKeyboardButton(delete_button.text, callback_data=delete_button.callback_data)])

        if inbound_keyboard is not None:
            back_button = get_back_button(inbound_keyboard, excluded_keys=excluded_keys_from_back_button)
            back_button.refresh_callback_data()
            keyboard_list.append([InlineKeyboardButton(back_button.text, callback_data=back_button.callback_data)])

        keyboard_markup = InlineKeyboardMarkup(keyboard_list)

    return keyboard_markup


def get_reply_to_message_id(update: Update = None, quote: bool = False, reply_to_message_id: int = None,
                            quote_if_group: bool = True) -> int | None:
    """
    Get reply message id
    :param update: Update object. Required if reply_to_message_id is None
    :param quote: Quote message. Default: False
    :param reply_to_message_id: Reply message id. Default: None
    :param quote_if_group: If the message should be quoted if it is in a group and update is not None. Default: True
    :return: Reply message id
    """

    if reply_to_message_id is not None:
        return reply_to_message_id

    # Group message quote
    try:
        if quote_if_group:
            if update.effective_chat.type == Chat.GROUP or update.effective_chat.type == Chat.SUPERGROUP:
                return update.effective_message.message_id
    except AttributeError:
        pass

    if not quote:
        return None

    if update.effective_message is None:
        raise Exception("No message to quote")
    else:
        return update.effective_message.message_id


def full_message_send(context: CallbackContext, text: str, update: Update = None, chat_id: int | str = None,
                      keyboard: list[list[Keyboard]] = None, answer_callback: bool = False, show_alert: bool = False,
                      new_message: bool = False, disable_notification: bool = True, reply_to_message_id: int = None,
                      parse_mode: str = c.TG_DEFAULT_PARSE_MODE, quote: bool = False, quote_if_group: bool = True,
                      protect_content: bool = False, disable_web_page_preview: bool = True,
                      allow_sending_without_reply: bool = True, add_delete_button: bool = False,
                      authorized_users: list = None, inbound_keyboard: Keyboard = None,
                      send_in_private_chat: bool = False, only_authorized_users_can_interact: bool = True,
                      edit_message_id: int = None, previous_screens: list[Screen] = None,
                      excluded_keys_from_back_button: list[str] = None) -> Message:
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
    :param reply_to_message_id: Message ID to reply to
    :param parse_mode: Parse mode
    :param quote: True if the message should be quoted
    :param quote_if_group: True if the message should be quoted if it is in a group and update is not None
    :param protect_content: True if the message should be protected from saving and forwarding
    :param disable_web_page_preview: True if the web page preview should be disabled
    :param allow_sending_without_reply: True if the message should be sent if message to be replied to is not found
    :param add_delete_button: True if the delete button should be added
    :param authorized_users: List of user ids that are allowed to delete the message
    :param inbound_keyboard: Inbound Keyboard object. If not None, a back button will be added to the keyboard
    :param send_in_private_chat: True if the message should be sent in private chat. Not necessary if update is not None
    :param only_authorized_users_can_interact: True if only authorized users can interact with the message keyboard
    :param edit_message_id: ID of the message to edit
    :param previous_screens: List of previous screens. Ignored if inbound_keyboard is not None
    :param excluded_keys_from_back_button: List of keys that should not be added to the back button info
    :return: Message
    """

    if text is not None and parse_mode == c.TG_PARSE_MODE_MARKDOWN and not answer_callback:
        text = escape_invalid_markdown_chars(text)

    if send_in_private_chat:
        new_message = True

    if previous_screens is not None and inbound_keyboard is None:
        inbound_keyboard = Keyboard('', previous_screen_list=previous_screens, screen=previous_screens[-1])

    chat_id = get_chat_id(update=update, chat_id=chat_id, send_in_private_chat=send_in_private_chat)
    keyboard_markup = get_keyboard(keyboard, update=update, add_delete_button=add_delete_button,
                                   authorized_users_tg_ids=authorized_users, inbound_keyboard=inbound_keyboard,
                                   only_authorized_users_can_interact=only_authorized_users_can_interact,
                                   excluded_keys_from_back_button=excluded_keys_from_back_button)

    # New message
    if (new_message or update is None or update.callback_query is None) and edit_message_id is None:
        # Message in reply to
        reply_to_message_id = get_reply_to_message_id(update=update, quote=quote,
                                                      reply_to_message_id=reply_to_message_id,
                                                      quote_if_group=quote_if_group)

        return context.bot.send_message(text=text,
                                        chat_id=chat_id,
                                        reply_markup=keyboard_markup,
                                        disable_web_page_preview=disable_web_page_preview,
                                        parse_mode=parse_mode,
                                        disable_notification=disable_notification,
                                        reply_to_message_id=reply_to_message_id,
                                        allow_sending_without_reply=allow_sending_without_reply,
                                        protect_content=protect_content)

    # No message to edit or answer callback
    if (update is None or update.callback_query is None) and edit_message_id is None:
        raise Exception(phrases.EXCEPTION_NO_EDIT_MESSAGE)

    # Answer callback
    if answer_callback:
        return context.bot.answer_callback_query(update.callback_query.id, text=text, show_alert=show_alert)

    # Edit message
    edit_message_id = edit_message_id if edit_message_id is not None else update.callback_query.message.message_id
    return context.bot.edit_message_text(text=text,
                                         chat_id=chat_id,
                                         reply_markup=keyboard_markup,
                                         parse_mode=parse_mode,
                                         disable_web_page_preview=disable_web_page_preview,
                                         message_id=edit_message_id)


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
            return InputMediaPhoto(media=saved_media.media_id, caption=caption, parse_mode=parse_mode)
        case SavedMediaType.VIDEO:
            return InputMediaVideo(media=saved_media.media_id, caption=caption, parse_mode=parse_mode)
        case SavedMediaType.ANIMATION:
            return InputMediaAnimation(media=saved_media.media_id, caption=caption, parse_mode=parse_mode)
        case _:
            raise Exception(phrases.EXCEPTION_SAVED_MEDIA_UNKNOWN_TYPE)


def full_media_send(context: CallbackContext, saved_media: SavedMedia = None, update: Update = None,
                    chat_id: int | str = None, caption: str = None, keyboard: list[list[Keyboard]] = None,
                    answer_callback: bool = False, show_alert: bool = False, new_message: bool = False,
                    disable_notification: bool = True, reply_to_message_id: int = None, protect_content: bool = False,
                    parse_mode: str = c.TG_DEFAULT_PARSE_MODE, quote: bool = False, quote_if_group: bool = True,
                    allow_sending_without_reply: bool = True, edit_only_keyboard: bool = False,
                    edit_only_caption_and_keyboard: bool = False, add_delete_button: bool = False,
                    authorized_users: list = None, inbound_keyboard: Keyboard = None,
                    send_in_private_chat: bool = False, only_authorized_users_can_interact: bool = True) -> Message:
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
    :param reply_to_message_id: Message ID to reply to
    :param protect_content: True if the message should be protected from saving and forwarding
    :param parse_mode: Parse mode
    :param quote: True if the message should be quoted
    :param quote_if_group: True if the message should be quoted if it is a group message
    :param allow_sending_without_reply: True if the message should be sent if message to be replied to is not found
    :param edit_only_keyboard: If only the keyboard should be edited
    :param edit_only_caption_and_keyboard: If only the caption and keyboard should be edited. If keyboard is None,
            it will be removed
    :param add_delete_button: True if the delete button should be added
    :param authorized_users: List of user ids that are allowed to delete the message
        :param inbound_keyboard: Inbound Keyboard object. If not None, a back button will be added to the keyboard
    :param send_in_private_chat: True if the message should be sent in private chat
    :param only_authorized_users_can_interact: True if only authorized users can interact with the message keyboard
    :return: Message
    """

    if caption is not None and parse_mode == c.TG_PARSE_MODE_MARKDOWN and not answer_callback:
        caption = escape_invalid_markdown_chars(caption)

    chat_id = get_chat_id(update=update, chat_id=chat_id, send_in_private_chat=send_in_private_chat)
    keyboard_markup = get_keyboard(keyboard, update=update, add_delete_button=add_delete_button,
                                   authorized_users_tg_ids=authorized_users, inbound_keyboard=inbound_keyboard,
                                   only_authorized_users_can_interact=only_authorized_users_can_interact)

    # New message
    if new_message or update is None or update.callback_query is None:
        reply_to_message_id = get_reply_to_message_id(update=update, quote=quote,
                                                      reply_to_message_id=reply_to_message_id,
                                                      quote_if_group=quote_if_group)

        match saved_media.type:
            # Photo
            case SavedMediaType.PHOTO:  # Photo
                return context.bot.send_photo(chat_id=chat_id,
                                              photo=saved_media.media_id,
                                              caption=caption,
                                              reply_markup=keyboard_markup,
                                              parse_mode=parse_mode,
                                              disable_notification=disable_notification,
                                              reply_to_message_id=reply_to_message_id,
                                              allow_sending_without_reply=allow_sending_without_reply,
                                              protect_content=protect_content)
            case SavedMediaType.VIDEO:  # Video
                return context.bot.send_video(chat_id=chat_id,
                                              video=saved_media.media_id,
                                              caption=caption,
                                              reply_markup=keyboard_markup,
                                              parse_mode=parse_mode,
                                              disable_notification=disable_notification,
                                              reply_to_message_id=reply_to_message_id,
                                              allow_sending_without_reply=allow_sending_without_reply,
                                              protect_content=protect_content)
            case SavedMediaType.ANIMATION:  # Animation
                return context.bot.send_animation(chat_id=chat_id,
                                                  animation=saved_media.media_id,
                                                  caption=caption,
                                                  reply_markup=keyboard_markup,
                                                  parse_mode=parse_mode,
                                                  disable_notification=disable_notification,
                                                  reply_to_message_id=reply_to_message_id,
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


def full_message_or_media_send_or_edit(context: CallbackContext, text: str, update: Update = None,
                                       chat_id: int | str = None, keyboard: list[list[Keyboard]] = None,
                                       parse_mode: str = c.TG_DEFAULT_PARSE_MODE, protect_content: bool = False,
                                       disable_web_page_preview: bool = True, edit_only_keyboard: bool = False,
                                       edit_only_caption_and_keyboard: bool = True, add_delete_button: bool = False,
                                       authorized_users: list = None) -> Message:
    """
    Edit a message or media, in case the type of message being edited is unknown
    :param context: CallbackContext object
    :param text: Text to send
    :param update: Update object. Required if chat_id is None
    :param chat_id: Chat id. Required if update is None
    :param keyboard: Keyboard object
    :param parse_mode: Parse mode
    :param protect_content: True if the message should be protected from saving and forwarding
    :param disable_web_page_preview: Only for text; True if the web page preview should be disabled
    :param edit_only_keyboard: Only for Media; if only the keyboard should be edited
    :param edit_only_caption_and_keyboard: Only for Media; If only the caption and keyboard should be edited.
            If keyboard is None, it will be removed
    :param add_delete_button: True if the delete button should be added
    :param authorized_users: List of user ids that are allowed to delete the message
    :return: Message
    """

    try:
        return full_message_send(context, text, update=update, chat_id=chat_id, keyboard=keyboard,
                                 parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview,
                                 add_delete_button=add_delete_button, authorized_users=authorized_users,
                                 protect_content=protect_content)
    except BadRequest:
        return full_media_send(context, caption=text, update=update, chat_id=chat_id, keyboard=keyboard,
                               parse_mode=parse_mode, add_delete_button=add_delete_button,
                               edit_only_keyboard=edit_only_keyboard,
                               edit_only_caption_and_keyboard=edit_only_caption_and_keyboard,
                               authorized_users=authorized_users, protect_content=protect_content)


def is_command(text: str) -> bool:
    """
    Check if the message is a command
    """
    try:
        return text[0] in c.COMMAND_PREFIX_ALIASES
    except TypeError:
        return False


def mention_markdown_v2(user_id: int | str, name: str) -> str:
    """
    Create a mention markdown v2
    """
    return mention_markdown(user_id, name, 2)


def mention_markdown_user(user: User) -> str:
    """
    Create a mention markdown given a user
    """
    return mention_markdown_v2(user.tg_user_id, user.tg_first_name)


def get_image_preview(image_url: str) -> str:
    """
    Create an image preview
    """
    return f'[​]({image_url})'


def get_delete_button(user_ids: list[int]) -> Keyboard:
    """
    Create a delete button
    :param user_ids: List of users ids that can operate the delete button
    """
    keyboard_data: dict = {'u': user_ids, 'del': 1}

    return Keyboard(phrases.KEYBOARD_OPTION_DELETE, keyboard_data)


def get_yes_no_keyboard(user: User, screen: Screen = None, yes_text: str = phrases.KEYBOARD_OPTION_YES,
                        no_text: str = phrases.KEYBOARD_OPTION_NO, primary_key: int = None,
                        extra_keys: list[dict] = None, yes_screen: Screen = None, no_screen: Screen = None,
                        yes_extra_keys: list[dict] = None, no_extra_keys: list[dict] = None) -> list[Keyboard]:
    """
    Create a yes/no keyboard
    :param user: User that can operate the keyboard
    :param primary_key: Primary key
    :param yes_text: Text for the yes button
    :param no_text: Text for the no button
    :param screen: The default screen that will be called when the user clicks on the yes/no button
    :param extra_keys: List of extra keys to add to the keyboard
    :param yes_screen: Screen to call when the user clicks on the yes button. If None, the default screen will be called
    :param no_screen: Screen to call when the user clicks on the no button. If None, the default screen will be called
    :param yes_extra_keys: List of extra keys for the yes button, in a dict of key and value
    :param no_extra_keys: List of extra keys for the no button, in a dict of key and value
    :return: The yes and no keyboard
    """

    if screen is None and (yes_screen is None or no_screen is None):
        raise ValueError('screen or yes_screen and no_screen must be specified')

    keyboard_line: list[Keyboard] = []

    default_keyboard_data = {}

    # Add primary key
    if primary_key is not None:
        default_keyboard_data['a'] = primary_key

    # Add extra keys
    if extra_keys is not None:
        for extra_key in extra_keys:
            for key, value in extra_key.items():
                default_keyboard_data[key] = value

    # Yes
    # If screen is being changed, discard yes key value
    keyboard_data_yes: dict = default_keyboard_data | ({'b': True} if screen != yes_screen else {})
    if yes_extra_keys is not None:
        for extra_key in yes_extra_keys:
            for key, value in extra_key.items():
                keyboard_data_yes[key] = value

    yes_screen = screen if yes_screen is None else yes_screen
    keyboard_line.append(Keyboard(yes_text, info=keyboard_data_yes, screen=yes_screen, authorized_users=[user],
                                  inherit_authorized_users=False))

    # No
    # If screen is being changed, discard no key value
    keyboard_data_no: dict = default_keyboard_data | ({'b': False} if screen != no_screen else {})
    if no_extra_keys is not None:
        for extra_key in no_extra_keys:
            for key, value in extra_key.items():
                keyboard_data_no[key] = value
    no_screen = screen if no_screen is None else no_screen
    keyboard_line.append(Keyboard(no_text, info=keyboard_data_no, screen=no_screen, authorized_users=[user],
                                  inherit_authorized_users=False))

    return keyboard_line


def get_back_button(inbound_keyboard: Keyboard, excluded_keys: list[str] = None) -> Keyboard:
    """
    Create a back button
    :param inbound_keyboard: Keyboard object
    :param excluded_keys: List of keys to exclude from the copy of info dict
    """

    info_copy = inbound_keyboard.info.copy()
    if excluded_keys is not None:
        for key in excluded_keys:
            info_copy.pop(key, None)

    # Always remove toggle key
    info_copy.pop(ReservedKeyboardKeys.TOGGLE, None)

    return Keyboard(phrases.KEYBOARD_OPTION_BACK, screen=inbound_keyboard.previous_screen_list[-1],
                    previous_screen_list=inbound_keyboard.previous_screen_list[:-1], inbound_info=info_copy)


def delete_message(update: Update):
    """
    Delete a message with best effort
    :param update: Update object
    """
    try:
        update.effective_message.delete()
    except TelegramError:
        pass


def get_message_source(update: Update) -> MessageSource:
    """
    Get the message source
    :param update: Update object
    :return: MessageSource object
    """

    if update.effective_chat.type == Chat.PRIVATE:
        return MessageSource.PRIVATE

    if update.effective_chat.id == Env.OPD_GROUP_ID.get_int():
        return MessageSource.GROUP

    if update.effective_chat.id == Env.ADMIN_GROUP_ID.get_int():
        return MessageSource.ADMIN

    if update.effective_chat.id == Env.TG_REST_CHANNEL_ID.get_int():
        return MessageSource.TG_REST

    logging.error(f'Unknown message source for {update.effective_chat.id}')
    return MessageSource.ND


def get_message_url(chat_id: int, message_id: int) -> str:
    """
    Get the message url
    :param chat_id: Chat id
    :param message_id: Message id
    :return: Message url
    """

    chat_id_cleaned = str(chat_id).replace('-100', '')
    return f'https://t.me/c/{chat_id_cleaned}/{message_id}'


def get_start_with_command_url(command: str) -> str:
    """
    Get the start with command url
    :param command: Command
    :return: Start with command url
    """
    return f'https://t.me/{Env.BOT_USERNAME.get()}?start={command}'


def get_create_or_edit_status(user: User, inbound_keyboard: Keyboard) -> tuple[bool, bool, bool]:
    """
    Get the item creation/edit status
    :param user: User object
    :param inbound_keyboard: Keyboard object
    :return: Tuple with should ignore input, should create item and should validate input
    """

    should_create_item = True
    should_validate_input = True
    should_ignore_input = False

    if inbound_keyboard is None and user.private_screen_step is None and user.private_screen_in_edit_id is None:
        should_ignore_input = True
    else:
        if user.private_screen_in_edit_id is not None:
            should_create_item = False
            if inbound_keyboard is not None:  # Keyboard interaction
                should_validate_input = False

    return should_ignore_input, should_create_item, should_validate_input
