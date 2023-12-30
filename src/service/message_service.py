import base64
import json
import logging
import re
from uuid import uuid4

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    InputMedia,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaAnimation,
    Chat,
    InlineQueryResult,
    InlineQueryResultArticle,
    InputTextMessageContent,
)
from telegram.error import BadRequest, TelegramError, Forbidden
from telegram.ext import ContextTypes
from telegram.helpers import mention_markdown

import constants as c
import resources.Environment as Env
import resources.phrases as phrases
from src.model.Group import Group
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.ContextDataKey import ContextDataKey
from src.model.enums.MessageSource import MessageSource
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.SavedMedia import SavedMedia
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.SavedMediaType import SavedMediaType
from src.model.enums.Screen import Screen
from src.model.pojo.ContextDataValue import ContextDataValue
from src.model.pojo.Keyboard import Keyboard
from src.service.bot_service import set_bot_context_data, get_bot_context_data


def escape_invalid_markdown_chars(text: str) -> str:
    """
    Escape invalid markdown chars
    :param text: Text
    :return: Escaped text
    """

    escape_chars = r"~>#+-=|{}.!"

    text = re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

    # Escape eventual quadruple backslashes with a double backslash
    text = text.replace("\\\\", "\\")

    return text


def escape_valid_markdown_chars(text: str) -> str:
    """
    Escape valid markdown chars
    :param text: Text
    :return: Escaped text
    """

    escape_chars = r"_*[]()"

    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)


def get_chat_id(
    update: Update = None, chat_id: int = None, send_in_private_chat: bool = False
) -> int:
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


def get_keyboard(
    keyboard: list[list[Keyboard]],
    update: Update = None,
    add_delete_button: bool = False,
    authorized_users_tg_ids: list = None,
    inbound_keyboard: Keyboard = None,
    only_authorized_users_can_interact: bool = True,
    excluded_keys_from_back_button: list[str] = None,
    back_screen_index: int = 0,
    use_close_delete: bool = False,
    should_add_current_user_to_authorized: bool = True,
    user: User = None,
    add_back_button: bool = True,
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
    :param back_screen_index: Index of the screen to go back to from previous_screens. Default: 0
    :param use_close_delete: True if the close button should be used instead of the delete button
    :param should_add_current_user_to_authorized: True if the current user should be added to the authorized users list
    :param user: User object
    :param add_back_button: True if the back button should be added to the keyboard if possible
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
        if (
            update.effective_user.id not in authorized_users_tg_ids
            and should_add_current_user_to_authorized
        ):
            authorized_users_tg_ids.append(update.effective_user.id)
    except AttributeError:
        pass

    authorized_users_ids: list[int] = []
    for tg_user_id in authorized_users_tg_ids:
        _user: User = User.get_or_none(User.tg_user_id == tg_user_id)
        if _user is not None:
            authorized_users_ids.append(_user.id)

    keyboard_markup = None
    if keyboard is not None or add_delete_button is True or inbound_keyboard is not None:
        keyboard_list: list[list[InlineKeyboardButton]] = []
        if keyboard is not None:
            for row in keyboard:
                keyboard_row: list[InlineKeyboardButton] = []
                for button in row:
                    if button.url is not None:
                        keyboard_row.append(InlineKeyboardButton(button.text, url=button.url))
                    elif button.switch_inline_query is not None:
                        keyboard_row.append(
                            InlineKeyboardButton(
                                button.text, switch_inline_query=button.switch_inline_query
                            )
                        )
                    else:
                        # Already has some callback_data. If it has no data, nothing should be added
                        # callback_data is a string initialized for an empty dict, so even if empty the string will have
                        # value '{}'. So, to confirm that it is empty, we first revert to a dictionary and check if the
                        # dict is empty.
                        if json.loads(button.callback_data):
                            # Add information about previous screen
                            if (
                                len(button.previous_screen_list) == 0
                            ):  # Do not alter if already set
                                if (
                                    inbound_keyboard is not None
                                    and inbound_keyboard.screen is not None
                                ):
                                    button.previous_screen_list = (
                                        inbound_keyboard.previous_screen_list.copy()
                                    )
                                    if (
                                        len(button.previous_screen_list) > 0
                                        and button.previous_screen_list[-1]
                                        != inbound_keyboard.screen
                                        != button.screen
                                    ):
                                        button.previous_screen_list.append(inbound_keyboard.screen)

                            # Add list of authorized users
                            if button.only_authorized_users_can_interact:
                                if (
                                    only_authorized_users_can_interact
                                    and button.inherit_authorized_users
                                ):
                                    if (
                                        update is not None
                                        and update.effective_chat.type != Chat.PRIVATE
                                    ):
                                        button.info[ReservedKeyboardKeys.AUTHORIZED_USER] = (
                                            authorized_users_ids
                                        )
                                elif (
                                    not button.inherit_authorized_users
                                    and len(button.authorized_users) > 0
                                ):
                                    button.info[ReservedKeyboardKeys.AUTHORIZED_USER] = [
                                        u.id for u in button.authorized_users if u is not None
                                    ]

                            if (
                                ReservedKeyboardKeys.AUTHORIZED_USER in button.info
                                and len(button.info[ReservedKeyboardKeys.AUTHORIZED_USER]) == 0
                            ):
                                del button.info[ReservedKeyboardKeys.AUTHORIZED_USER]

                            button.refresh_callback_data()

                        try:
                            keyboard_row.append(
                                InlineKeyboardButton(
                                    button.text, callback_data=button.callback_data
                                )
                            )
                        except AttributeError:
                            logging.error(f"Button {button} does not have a callback_data")
                            pass

                keyboard_list.append(keyboard_row)

        if add_delete_button is True:
            if not len(authorized_users_ids) > 0:
                raise Exception("No authorized users provided for delete button")

            delete_button = get_delete_button(
                authorized_users_ids, use_close_delete=use_close_delete
            )
            keyboard_list.append([
                InlineKeyboardButton(delete_button.text, callback_data=delete_button.callback_data)
            ])

        if inbound_keyboard is not None and add_back_button:
            back_button = get_back_button(
                inbound_keyboard,
                excluded_keys=excluded_keys_from_back_button,
                back_screen_index=back_screen_index,
                user=user,
            )
            back_button.refresh_callback_data()
            keyboard_list.append(
                [InlineKeyboardButton(back_button.text, callback_data=back_button.callback_data)]
            )

        keyboard_markup = InlineKeyboardMarkup(keyboard_list)

    return keyboard_markup


def get_reply_to_message_id(
    update: Update = None,
    quote: bool = False,
    reply_to_message_id: int = None,
    quote_if_group: bool = True,
) -> int | None:
    """
    Get reply message id
    :param update: Update object. Required if reply_to_message_id is None
    :param quote: Quote message. Default: False
    :param reply_to_message_id: Reply message id. Default: None
    :param quote_if_group: If the message should be quoted if it is in a filter_by_groups and update is not None.
                           Default: True
    :return: Reply message id
    """

    if reply_to_message_id is not None:
        return reply_to_message_id

    # Group message quote
    try:
        if quote_if_group:
            if (
                update.effective_chat.type == Chat.GROUP
                or update.effective_chat.type == Chat.SUPERGROUP
            ):
                return update.effective_message.message_id
    except AttributeError:
        pass

    if not quote:
        return None

    if update.effective_message is None:
        raise Exception("No message to quote")
    else:
        return update.effective_message.message_id


async def full_message_send(
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    update: Update = None,
    chat_id: int | str = None,
    keyboard: list[list[Keyboard]] = None,
    answer_callback: bool = False,
    show_alert: bool = False,
    new_message: bool = False,
    disable_notification: bool = True,
    reply_to_message_id: int = None,
    parse_mode: str = c.TG_DEFAULT_PARSE_MODE,
    quote: bool = False,
    quote_if_group: bool = True,
    protect_content: bool = False,
    disable_web_page_preview: bool = True,
    allow_sending_without_reply: bool = True,
    add_delete_button: bool = False,
    authorized_users: list = None,
    inbound_keyboard: Keyboard = None,
    send_in_private_chat: bool = False,
    only_authorized_users_can_interact: bool = True,
    edit_message_id: int = None,
    previous_screens: list[Screen] = None,
    excluded_keys_from_back_button: list[str] = None,
    back_screen_index: int = 0,
    previous_screen_list_keyboard_info: dict = None,
    use_close_delete: bool = False,
    group_chat: GroupChat = None,
    ignore_exception: bool = False,
    user: User = None,
    from_exception: bool = False,
    add_back_button: bool = True,
) -> Message | bool:
    """
    Send a message

    :param context: ContextTypes.DEFAULT_TYPE object
    :param text: Text to send
    :param update: Update object. Required if chat_id is None
    :param chat_id: Chat id. Required if update is None
    :param keyboard: Keyboard object
    :param answer_callback: If it is an answer callback
    :param show_alert: If to show an alert in the callback answer
    :param new_message: True if the message is a new message
    :param disable_notification: True if a notification should not be sent
    :param reply_to_message_id: Message ID to reply to
    :param parse_mode: Parse mode
    :param quote: True if the message should be quoted
    :param quote_if_group: True if the message should be quoted if it is in a filter_by_groups and update is not None
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
    :param back_screen_index: Index of the screen to go back to from previous_screens. Default: 0
    :param previous_screen_list_keyboard_info: In case inbound keyboard is inferred from previous_screens, this is the
            keyboard info to add to the back button
    :param use_close_delete: True if the close button should be used instead of the delete button
    :param group_chat: The group chat, used to get the group chat id
    :param ignore_exception: True if the TelegramError should be ignored
    :param user: User object
    :param from_exception: True if the message is sent from an exception
    :param add_back_button: True if the back button should be added to the keyboard if possible
    :return: Message
    """

    if text is not None and parse_mode == c.TG_PARSE_MODE_MARKDOWN and not answer_callback:
        text = escape_invalid_markdown_chars(text)

    if send_in_private_chat:
        new_message = True

    if show_alert:
        answer_callback = True

    topic_id = None
    if group_chat is not None:
        topic_id = group_chat.tg_topic_id
        group: Group = group_chat.group
        chat_id = group.tg_group_id

    if previous_screens is not None and (inbound_keyboard is None or from_exception):
        inbound_keyboard = Keyboard(
            "",
            previous_screen_list=previous_screens,
            screen=previous_screens[-1],
            info=previous_screen_list_keyboard_info,
        )

    chat_id = get_chat_id(
        update=update, chat_id=chat_id, send_in_private_chat=send_in_private_chat
    )
    keyboard_markup = get_keyboard(
        keyboard,
        update=update,
        add_delete_button=add_delete_button,
        authorized_users_tg_ids=authorized_users,
        inbound_keyboard=inbound_keyboard,
        only_authorized_users_can_interact=only_authorized_users_can_interact,
        excluded_keys_from_back_button=excluded_keys_from_back_button,
        back_screen_index=back_screen_index,
        use_close_delete=use_close_delete,
        user=user,
        add_back_button=add_back_button,
    )

    # New message
    if (
        new_message or update is None or update.callback_query is None
    ) and edit_message_id is None:
        # Message in reply to
        reply_to_message_id = get_reply_to_message_id(
            update=update,
            quote=quote,
            reply_to_message_id=reply_to_message_id,
            quote_if_group=quote_if_group,
        )

        try:
            message: Message = await context.bot.send_message(
                text=text,
                chat_id=chat_id,
                reply_markup=keyboard_markup,
                disable_web_page_preview=disable_web_page_preview,
                parse_mode=parse_mode,
                disable_notification=disable_notification,
                reply_to_message_id=reply_to_message_id,
                allow_sending_without_reply=allow_sending_without_reply,
                protect_content=protect_content,
                message_thread_id=topic_id,
            )
            return message
        except TelegramError as e:
            if ignore_exception:
                logging.error(f"Error while sending message: {e}")
                return False
            raise e

    # No message to edit or answer callback
    if (update is None or update.callback_query is None) and edit_message_id is None:
        raise AttributeError(phrases.EXCEPTION_NO_EDIT_MESSAGE)

    # Answer callback
    if answer_callback:
        return await context.bot.answer_callback_query(
            update.callback_query.id, text=text, show_alert=show_alert
        )

    # Edit message
    edit_message_id = (
        edit_message_id
        if edit_message_id is not None
        else update.callback_query.message.message_id
    )
    return await context.bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        reply_markup=keyboard_markup,
        parse_mode=parse_mode,
        disable_web_page_preview=disable_web_page_preview,
        message_id=edit_message_id,
    )


def get_input_media_from_saved_media(
    saved_media: SavedMedia, caption: str = None, parse_mode: str = c.TG_DEFAULT_PARSE_MODE
) -> InputMedia:
    """
    Get InputMedia object from SavedMedia object
    :param saved_media: SavedMedia object
    :param caption: Caption
    :param parse_mode: Parse mode
    :return: InputMedia object
    """

    match saved_media.type:
        case SavedMediaType.PHOTO:
            return InputMediaPhoto(
                media=saved_media.media_id, caption=caption, parse_mode=parse_mode
            )
        case SavedMediaType.VIDEO:
            return InputMediaVideo(
                media=saved_media.media_id, caption=caption, parse_mode=parse_mode
            )
        case SavedMediaType.ANIMATION:
            return InputMediaAnimation(
                media=saved_media.media_id, caption=caption, parse_mode=parse_mode
            )
        case _:
            raise ValueError(f"Invalid media type: {saved_media.type}")


async def full_media_send(
    context: ContextTypes.DEFAULT_TYPE,
    saved_media: SavedMedia = None,
    update: Update = None,
    chat_id: int | str = None,
    caption: str = None,
    keyboard: list[list[Keyboard]] = None,
    answer_callback: bool = False,
    show_alert: bool = False,
    new_message: bool = False,
    disable_notification: bool = True,
    reply_to_message_id: int = None,
    protect_content: bool = False,
    parse_mode: str = c.TG_DEFAULT_PARSE_MODE,
    quote: bool = False,
    quote_if_group: bool = True,
    allow_sending_without_reply: bool = True,
    edit_only_keyboard: bool = False,
    edit_only_caption_and_keyboard: bool = False,
    add_delete_button: bool = False,
    authorized_users: list = None,
    inbound_keyboard: Keyboard = None,
    send_in_private_chat: bool = False,
    only_authorized_users_can_interact: bool = True,
    saved_media_name: SavedMediaName = None,
    group_chat: GroupChat = None,
    exceptions_to_ignore: list[Exception] = None,
    ignore_forbidden_exception: bool = False,
    edit_message_id: int = None,
    ignore_bad_request_exception: bool = False,
) -> Message | bool:
    """
    Send a media
    :param context: ContextTypes.DEFAULT_TYPE object
    :param saved_media: SavedMedia object
    :param update: Update object. Required if chat_id is None
    :param chat_id: Chat id. Required if update is None
    :param caption: Caption
    :param keyboard: Keyboard object
    :param answer_callback: If it is an answer callback
    :param show_alert: If to show an alert in the callback answer
    :param new_message: True if the message is a new message
    :param disable_notification: True if a notification should not be sent
    :param reply_to_message_id: Message ID to reply to
    :param protect_content: True if the message should be protected from saving and forwarding
    :param parse_mode: Parse mode
    :param quote: True if the message should be quoted
    :param quote_if_group: True if the message should be quoted if it is a group_chat message
    :param allow_sending_without_reply: True if the message should be sent if message to be replied to is not found
    :param edit_only_keyboard: If only the keyboard should be edited
    :param edit_only_caption_and_keyboard: If only the caption and keyboard should be edited. If keyboard is None,
            it will be removed
    :param add_delete_button: True if the delete button should be added
    :param authorized_users: List of user ids that are allowed to delete the message
        :param inbound_keyboard: Inbound Keyboard object. If not None, a back button will be added to the keyboard
    :param send_in_private_chat: True if the message should be sent in private chat
    :param only_authorized_users_can_interact: True if only authorized users can interact with the message keyboard
    :param saved_media_name: Saved media name
    :param group_chat: The group chat, used to get the group chat id
    :param exceptions_to_ignore: List of exceptions to ignore
    :param ignore_forbidden_exception: True if the forbidden exception should be ignored
    :param ignore_bad_request_exception: True if the bad request exception should be ignored
    :param edit_message_id: Message id to edit
    :return: Message
    """

    if exceptions_to_ignore is None:
        exceptions_to_ignore = []

    if ignore_forbidden_exception:
        exceptions_to_ignore.append(Forbidden)

    if ignore_bad_request_exception:
        exceptions_to_ignore.append(BadRequest)

    if caption is not None and parse_mode == c.TG_PARSE_MODE_MARKDOWN and not answer_callback:
        caption = escape_invalid_markdown_chars(caption)

    if saved_media is None and saved_media_name is not None:
        saved_media: SavedMedia = SavedMedia.get_by_name(saved_media_name)

    # Media id should be saved to avoid re-uploading each time
    should_save_media_id = False
    if (
        saved_media is not None
        and saved_media.file_name is not None
        and not isinstance(saved_media.media_id, str)
    ):
        # Try to load media id from context bot data
        try:
            if saved_media.name is not None:
                saved_media.media_id = get_bot_context_data(
                    context,
                    ContextDataKey.SAVED_MEDIA,
                    inner_key=saved_media.name,
                    tolerate_key_exception=False,
                )
            else:
                raise KeyError
        except KeyError:
            # Load media id from file
            saved_media.media_id = open(saved_media.file_name, "rb")
            should_save_media_id = saved_media.name is not None

    topic_id = None
    if group_chat is not None:
        topic_id = group_chat.tg_topic_id
        group: Group = group_chat.group
        chat_id = group.tg_group_id

    chat_id = get_chat_id(
        update=update, chat_id=chat_id, send_in_private_chat=send_in_private_chat
    )
    keyboard_markup = get_keyboard(
        keyboard,
        update=update,
        add_delete_button=add_delete_button,
        authorized_users_tg_ids=authorized_users,
        inbound_keyboard=inbound_keyboard,
        only_authorized_users_can_interact=only_authorized_users_can_interact,
    )

    is_edit = edit_message_id is not None or edit_only_keyboard or edit_only_caption_and_keyboard
    try:
        # New message
        if (new_message or update is None or update.callback_query is None) and not is_edit:
            reply_to_message_id = get_reply_to_message_id(
                update=update,
                quote=quote,
                reply_to_message_id=reply_to_message_id,
                quote_if_group=quote_if_group,
            )

            match saved_media.type:
                # Photo
                case SavedMediaType.PHOTO:  # Photo
                    message: Message = await context.bot.send_photo(
                        chat_id=chat_id,
                        photo=saved_media.media_id,
                        caption=caption,
                        reply_markup=keyboard_markup,
                        parse_mode=parse_mode,
                        disable_notification=disable_notification,
                        reply_to_message_id=reply_to_message_id,
                        allow_sending_without_reply=allow_sending_without_reply,
                        protect_content=protect_content,
                        message_thread_id=topic_id,
                    )

                case SavedMediaType.VIDEO:  # Video
                    message: Message = await context.bot.send_video(
                        chat_id=chat_id,
                        video=saved_media.media_id,
                        caption=caption,
                        reply_markup=keyboard_markup,
                        parse_mode=parse_mode,
                        disable_notification=disable_notification,
                        reply_to_message_id=reply_to_message_id,
                        allow_sending_without_reply=allow_sending_without_reply,
                        protect_content=protect_content,
                        message_thread_id=topic_id,
                    )

                case SavedMediaType.ANIMATION:  # Animation
                    message: Message = await context.bot.send_animation(
                        chat_id=chat_id,
                        animation=saved_media.media_id,
                        caption=caption,
                        reply_markup=keyboard_markup,
                        parse_mode=parse_mode,
                        disable_notification=disable_notification,
                        reply_to_message_id=reply_to_message_id,
                        allow_sending_without_reply=allow_sending_without_reply,
                        protect_content=protect_content,
                        message_thread_id=topic_id,
                    )
                case _:
                    raise ValueError(f"Invalid saved media type: {saved_media.type}")

            if should_save_media_id:
                saved_media.media_id = message.photo[-1].file_id
                set_bot_context_data(
                    context,
                    ContextDataKey.SAVED_MEDIA,
                    saved_media.media_id,
                    inner_key=saved_media.name,
                )

            return message

        # No message to edit or answer callback
        if (update is None or update.callback_query is None) and edit_message_id is None:
            raise Exception(phrases.EXCEPTION_NO_EDIT_MESSAGE)

        # Answer callback
        if answer_callback:
            return await context.bot.answer_callback_query(
                update.callback_query.id, text=caption, show_alert=show_alert
            )

        edit_message_id = (
            edit_message_id
            if edit_message_id is not None
            else update.callback_query.message.message_id
        )

        # Edit only keyboard
        if edit_only_keyboard:
            return await context.bot.edit_message_reply_markup(
                chat_id=chat_id, message_id=edit_message_id, reply_markup=keyboard_markup
            )

        # Edit only caption and keyboard
        if edit_only_caption_and_keyboard:
            return await context.bot.edit_message_caption(
                chat_id=chat_id,
                message_id=edit_message_id,
                caption=caption,
                reply_markup=keyboard_markup,
            )

        # Edit full media
        input_media: InputMedia = get_input_media_from_saved_media(
            saved_media=saved_media, caption=caption
        )
        return await context.bot.edit_message_media(
            chat_id=chat_id,
            message_id=edit_message_id,
            media=input_media,
            reply_markup=keyboard_markup,
        )
    except Exception as e:
        for e_to_ignore in exceptions_to_ignore:
            if isinstance(e, e_to_ignore):
                logging.error(f"Error while sending message: {e}")
                return False

        raise e


async def full_message_or_media_send_or_edit(
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    update: Update = None,
    chat_id: int | str = None,
    keyboard: list[list[Keyboard]] = None,
    parse_mode: str = c.TG_DEFAULT_PARSE_MODE,
    protect_content: bool = False,
    disable_web_page_preview: bool = True,
    edit_only_keyboard: bool = False,
    edit_only_caption_and_keyboard: bool = True,
    add_delete_button: bool = False,
    authorized_users: list = None,
    answer_callback: bool = False,
    show_alert: bool = False,
    inbound_keyboard: Keyboard = None,
    previous_screens: list[Screen] = None,
    from_exception: bool = False,
    previous_screen_list_keyboard_info: dict = None,
) -> Message:
    """
    Edit a message or media, in case the type of message being edited is unknown
    :param context: ContextTypes.DEFAULT_TYPE object
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
    :param answer_callback: True if the callback should be answered
    :param show_alert: True if the callback should be answered with an alert
    :param inbound_keyboard: Inbound Keyboard object. If not None, a back button will be added to the keyboard
    :param previous_screens: List of previous screens. Ignored if inbound_keyboard is not None
    :param from_exception: True if the message is sent from an exception
    :param previous_screen_list_keyboard_info: In case inbound keyboard is inferred from previous_screens, this is the
            keyboard info to add to the back button
    :return: Message
    """

    try:
        return await full_message_send(
            context,
            text,
            update=update,
            chat_id=chat_id,
            keyboard=keyboard,
            answer_callback=answer_callback,
            show_alert=show_alert,
            parse_mode=parse_mode,
            protect_content=protect_content,
            disable_web_page_preview=disable_web_page_preview,
            add_delete_button=add_delete_button,
            authorized_users=authorized_users,
            inbound_keyboard=inbound_keyboard,
            previous_screens=previous_screens,
            from_exception=from_exception,
            previous_screen_list_keyboard_info=previous_screen_list_keyboard_info,
        )
    except BadRequest:
        return await full_media_send(
            context,
            caption=text,
            update=update,
            chat_id=chat_id,
            keyboard=keyboard,
            parse_mode=parse_mode,
            add_delete_button=add_delete_button,
            edit_only_keyboard=edit_only_keyboard,
            edit_only_caption_and_keyboard=edit_only_caption_and_keyboard,
            authorized_users=authorized_users,
            protect_content=protect_content,
            answer_callback=answer_callback,
            show_alert=show_alert,
            inbound_keyboard=inbound_keyboard,
        )


async def full_inline_query_answer(update: Update, items: list[ContextDataValue]) -> bool:
    """
    Answer an inline query
    :param update: Update object
    :param items: List of items to display
    :return: True if the answer was sent
    """

    if len(items) == 0:
        return False

    results: list[InlineQueryResult] = []
    for item in items:
        if callable(item.text):
            text = item.text(*item.args)
        else:
            text = item.text

        keyboard_markup = get_keyboard(item.keyboard) if item.keyboard is not None else None
        results.append(
            InlineQueryResultArticle(
                id=str(uuid4()),
                title=item.title,
                description=item.description,
                input_message_content=InputTextMessageContent(escape_invalid_markdown_chars(text)),
                reply_markup=keyboard_markup,
            )
        )

    await update.inline_query.answer(results)


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
    return f"[​]({image_url})"


def get_delete_button(
    user_ids: list[int], use_close_delete=False, button_text: str = None
) -> Keyboard:
    """
    Create a delete button
    :param user_ids: List of users ids that can operate the delete button
    :param use_close_delete: True if the close button should be used instead of the delete button
    :param button_text: Text of the button
    """
    keyboard_data: dict = {
        ReservedKeyboardKeys.AUTHORIZED_USER: user_ids,
        ReservedKeyboardKeys.DELETE: True,
    }

    if button_text is None:
        button_text = (
            phrases.KEYBOARD_OPTION_CLOSE if use_close_delete else phrases.KEYBOARD_OPTION_DELETE
        )

    return Keyboard(button_text, keyboard_data)


def get_yes_no_keyboard(
    user: User = None,
    screen: Screen = None,
    yes_text: str = phrases.KEYBOARD_OPTION_YES,
    no_text: str = phrases.KEYBOARD_OPTION_NO,
    primary_key: int = None,
    extra_keys: dict = None,
    yes_screen: Screen = None,
    no_screen: Screen = None,
    yes_extra_keys: dict = None,
    no_extra_keys: dict = None,
    confirm_key: str = ReservedKeyboardKeys.CONFIRM,
    inbound_keyboard: Keyboard = None,
    yes_is_back_button: bool = False,
    no_is_back_button: bool = False,
    yes_is_delete_button: bool = False,
    no_is_delete_button: bool = False,
    add_inbound_key_info: bool = False,
    keys_to_exclude: list[str] = None,
    exclude_yes_button: bool = False,
    exclude_no_button: bool = False,
    authorized_users: list[User] = None,
) -> list[Keyboard]:
    """
    Create a yes/no keyboard

    :param user: User that can operate the keyboard
    :param primary_key: Primary key
    :param yes_text: Text for the yes button
    :param no_text: Text for the no button
    :param screen: The default screen that will be called when the user clicks on the yes/no button
    :param extra_keys: Dict of extra keys to add to the keyboard
    :param yes_screen: Screen to call when the user clicks on the yes button. If None, the default screen will be called
    :param no_screen: Screen to call when the user clicks on the no button. If None, the default screen will be called
    :param yes_extra_keys: Dict of extra keys for the yes button, in a dict of key and value
    :param no_extra_keys: Dict of extra keys for the no button, in a dict of key and value
    :param confirm_key: Yes or no key. If None, default value will be used
    :param inbound_keyboard: The inbound keyboard
    :param yes_is_back_button: True if the yes button should be a back button
    :param no_is_back_button: True if the no button should be a back button
    :param yes_is_delete_button: True if the yes button should be a delete button
    :param no_is_delete_button: True if the no button should be a delete button
    :param add_inbound_key_info: True if the inbound key info should be added to the yes and no buttons
    :param keys_to_exclude: List of keys to exclude from the copy of info dict
    :param exclude_yes_button: True if the yes button should be excluded
    :param exclude_no_button: True if the no button should be excluded
    :param authorized_users: List of users that can operate the keyboard
    :return: The yes and no keyboard
    """

    if authorized_users is None:
        authorized_users = []
    else:
        # Remove None users
        authorized_users = [u for u in authorized_users if u is not None]

    if user is not None:
        authorized_users.append(user)

    if screen is None and (yes_screen is None or no_screen is None):
        if inbound_keyboard is not None:
            screen = inbound_keyboard.screen
        else:
            raise ValueError("screen or yes_screen and no_screen must be specified")

    keys_to_exclude = keys_to_exclude if keys_to_exclude is not None else []

    keyboard_line: list[Keyboard] = []

    default_keyboard_data = {}

    # Add primary key
    if primary_key is not None:
        default_keyboard_data[ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY] = primary_key

    # Add extra keys
    if extra_keys is not None:
        for key, value in extra_keys.items():
            default_keyboard_data[key] = value

    # Add inbound key info
    if add_inbound_key_info and inbound_keyboard is not None:
        for key, value in inbound_keyboard.info.items():
            default_keyboard_data[key] = value

    for key in keys_to_exclude:
        if key in default_keyboard_data:
            default_keyboard_data.pop(key)

    # Yes
    if not exclude_yes_button:
        if yes_is_back_button:
            keyboard_line.append(
                get_back_button(
                    inbound_keyboard, key_text=yes_text, user=user, info=default_keyboard_data
                )
            )
        elif yes_is_delete_button:
            keyboard_line.append(
                get_delete_button([u.tg_user_id for u in authorized_users], button_text=yes_text)
            )
        else:
            # If screen is being changed, discard yes key value
            keyboard_data_yes: dict = default_keyboard_data | (
                {confirm_key: True}
                if not (yes_screen is not None and screen is not yes_screen)
                else {}
            )
            if yes_extra_keys is not None:
                for key, value in yes_extra_keys.items():
                    keyboard_data_yes[key] = value

            yes_screen = screen if yes_screen is None else yes_screen
            keyboard_line.append(
                Keyboard(
                    yes_text,
                    info=keyboard_data_yes,
                    screen=yes_screen,
                    authorized_users=authorized_users,
                    inherit_authorized_users=False,
                )
            )

    # No
    if not exclude_no_button:
        if no_is_back_button:
            keyboard_line.append(
                get_back_button(
                    inbound_keyboard, key_text=no_text, user=user, info=default_keyboard_data
                )
            )
        elif no_is_delete_button:
            keyboard_line.append(
                get_delete_button([u.tg_user_id for u in authorized_users], button_text=no_text)
            )
        else:
            # If screen is being changed, discard no key value
            keyboard_data_no: dict = default_keyboard_data | (
                {confirm_key: False}
                if not (no_screen is not None and screen is not no_screen)
                else {}
            )
            if no_extra_keys is not None:
                for key, value in no_extra_keys.items():
                    keyboard_data_no[key] = value
            no_screen = screen if no_screen is None else no_screen
            keyboard_line.append(
                Keyboard(
                    no_text,
                    info=keyboard_data_no,
                    screen=no_screen,
                    authorized_users=authorized_users,
                    inherit_authorized_users=False,
                )
            )

    return keyboard_line


def get_back_button(
    inbound_keyboard: Keyboard,
    excluded_keys: list[str] = None,
    back_screen_index: int = 0,
    key_text: str = phrases.KEYBOARD_OPTION_BACK,
    user: User = None,
    info: dict = None,
) -> Keyboard:
    """
    Create a back button

    :param inbound_keyboard: Keyboard object
    :param excluded_keys: List of keys to exclude from the copy of info dict
    :param back_screen_index: Index of the screen to go back to from previous_screens. Default: 0
    :param key_text: Text for the back button
    :param user: The user, used for previous screens if inbound_keyboard is None
    :param info: Info dict to add to the back button
    """

    info_copy = info.copy() if info is not None else {}

    if user is not None and user.private_screen_stay_step is not None:
        user.private_screen_stay = True

    if inbound_keyboard is not None:
        info_copy = inbound_keyboard.info.copy() | info_copy
        if excluded_keys is not None:
            for key in excluded_keys:
                info_copy.pop(key, None)

        # Always excluded keys
        # Toggle
        info_copy.pop(ReservedKeyboardKeys.TOGGLE, None)
        # Confirm
        info_copy.pop(ReservedKeyboardKeys.CONFIRM, None)

        previous_screen_list = inbound_keyboard.previous_screen_list
    else:
        previous_screen_list = [
            Screen(s) for s in user.private_screen_list.split(c.STANDARD_SPLIT_CHAR)
        ]

    if inbound_keyboard is not None and len(inbound_keyboard.previous_screen_list) == 0:
        return Keyboard(key_text, screen=Screen.PVT_START, inbound_info=info_copy)

    private_screen_step = None
    if inbound_keyboard is not None and ReservedKeyboardKeys.SCREEN_STEP in inbound_keyboard.info:
        private_screen_step = inbound_keyboard.info[ReservedKeyboardKeys.SCREEN_STEP]
    elif user is not None:
        private_screen_step = user.private_screen_previous_step

    if user is not None and user.private_screen_stay:
        # Stay on same screen
        previous_screen_end_index = None
        screen: Screen = user.get_private_screen_list()[-1]
        if user.private_screen_stay_step:
            info_copy[ReservedKeyboardKeys.SCREEN_STEP] = user.private_screen_stay_step
    elif private_screen_step is not None and private_screen_step > 0:
        # Go back to previous step on same screen
        previous_screen_end_index = None  # Do not exclude last screen
        screen: Screen = previous_screen_list[-1]
        if inbound_keyboard is not None:
            screen = inbound_keyboard.screen
        if user is not None:
            info_copy[ReservedKeyboardKeys.SCREEN_STEP] = user.private_screen_step - 1
    else:
        # Go back to previous screen
        previous_screen_end_index = -1 - back_screen_index
        screen: Screen = previous_screen_list[previous_screen_end_index]

        # Make sure the screen isn't the same as the next previous screen, don't go back to the same screen
        try:
            if inbound_keyboard is not None and inbound_keyboard.screen is screen:
                screen = previous_screen_list[previous_screen_end_index - 1]
        except (AttributeError, KeyError, TypeError, IndexError):
            pass

    return Keyboard(
        key_text,
        screen=screen,
        previous_screen_list=previous_screen_list[:previous_screen_end_index],
        inbound_info=info_copy,
    )


async def delete_message(
    update: Update = None,
    context: ContextTypes.DEFAULT_TYPE = None,
    chat_id: int = None,
    message_id: int = None,
    group_chat: GroupChat = None,
):
    """
    Delete a message with the best effort method
    :param update: Update object
    :param context: Context object
    :param chat_id: Chat id
    :param message_id: Message id
    :param group_chat: The group chat
    """

    if group_chat is not None:
        group: Group = group_chat.group
        chat_id = group.tg_group_id

    if update is None and (context is None or chat_id is None or message_id is None):
        logging.error(
            "update or context and chat_id and message_id must be specified to delete message"
        )
        return

    try:
        if update is not None:
            await update.effective_message.delete()
        else:
            await context.bot.delete_message(chat_id, message_id)
    except TelegramError:
        logging.error(f"Failed to delete message {message_id} in chat {chat_id}")
        pass


def get_message_source(update: Update) -> MessageSource:
    """
    Get the message source
    :param update: Update object
    :return: MessageSource object
    """

    try:
        if update.effective_chat.type == Chat.PRIVATE:
            return MessageSource.PRIVATE

        if update.effective_chat.type in [Chat.GROUP, Chat.SUPERGROUP]:
            return MessageSource.GROUP

        if update.effective_chat.id == Env.TG_REST_CHANNEL_ID.get_int():
            return MessageSource.TG_REST
    except AttributeError:
        if update.inline_query.query is not None:
            return MessageSource.INLINE_QUERY

    return MessageSource.ND


def get_start_with_command_url(command: str) -> str:
    """
    Get the start with command url
    :param command: Command
    :return: Start with command url
    """
    return f"https://t.me/{Env.BOT_USERNAME.get()}?start={command}"


def get_deeplink(
    info: dict | str = None, screen: Screen = None, previous_screens: list[Screen] = None
) -> str:
    """
    Get the deeplink
    :param info: Info dict
    :param screen: Screen
    :param previous_screens: List of previous screens
    :return: Deeplink
    """

    if info is None:
        info = {}

    if isinstance(info, dict):
        if screen is not None:
            info[ReservedKeyboardKeys.SCREEN] = screen[1:]

        if previous_screens is not None:
            info[ReservedKeyboardKeys.PREVIOUS_SCREEN] = [s[1:] for s in previous_screens]

        info = json.dumps(info, separators=(",", ":"))

    encoded_bytes = info.encode("utf-8")
    encoded_string = base64.b64encode(encoded_bytes).decode("utf-8")

    return get_start_with_command_url(encoded_string)


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

    if (
        inbound_keyboard is None
        and user.private_screen_step is None
        and user.private_screen_in_edit_id is None
    ):
        should_ignore_input = True
    else:
        if user.private_screen_in_edit_id is not None:
            should_create_item = False
            if inbound_keyboard is not None:  # Keyboard interaction
                should_validate_input = False

    return should_ignore_input, should_create_item, should_validate_input


async def log_error(
    context: ContextTypes.DEFAULT_TYPE, text: str, update: Update = None
) -> Message:
    """
    Send an error to the error log chat
    :param context: Context object
    :param text: Text to send
    :param update: Update object
    """

    text = f"Error: {text}".upper()
    return await full_message_send(
        context, text, update=update, chat_id=Env.ERROR_LOG_CHAT_ID.get_int()
    )


def message_is_reply(update: Update) -> bool:
    """
    Check if the message is a reply. Necessary because, due to a Telegram bug, the reply_to_message field is set
    for every message sent in not general topics
    :param update: Update object
    :return: True if the message is a reply
    """

    try:
        return (
            update.effective_message.reply_to_message is not None
            and update.effective_message.reply_to_message.forum_topic_created is None
        )
    except AttributeError:
        return False


def get_message_url(message_id: int, group_chat: GroupChat = None, chat_id: str = None) -> str:
    """
    Gets the message url
    :param group_chat: The group chat
    :param message_id: The message id
    :param chat_id: The chat id
    :return: The message url
    """

    if chat_id is None and group_chat is None:
        raise ValueError("chat_id or group_chat must be specified")

    tg_chat_id = chat_id

    if group_chat is not None:
        group: Group = group_chat.group
        tg_chat_id = str(group.tg_group_id)

    tg_chat_id = tg_chat_id.replace("-100", "")

    url = f"https://t.me/c/{tg_chat_id}/{message_id}"

    # If tg_chat_id is not a number, it is a username so remove the /c/ part
    if not tg_chat_id.isnumeric():
        url = url.replace("/c/", "/")

    return url
