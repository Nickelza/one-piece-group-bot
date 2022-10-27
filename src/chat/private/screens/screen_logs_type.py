from strenum import StrEnum
from telegram import Update
from telegram.ext import CallbackContext

import constants as c
import resources.phrases as phrases
from src.model.User import User
from src.model.enums.Log import Log, LogType, get_log_by_type
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CustomException import NavigationLimitReachedException
from src.model.pojo.Keyboard import Keyboard
from src.service.list_service import get_page, get_navigation_buttons
from src.service.message_service import full_message_send


class LogTypeReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    TYPE = 'a'
    ITEM_ID = 'b'


def manage(update: Update, context: CallbackContext, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the log type screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    log: Log = get_log_by_type(LogType(inbound_keyboard.info[LogTypeReservedKeys.TYPE]))
    log.user = user
    items_text, items_keyboard = get_items_text_keyboard(inbound_keyboard, log)

    ot_text = phrases.LIST_OVERVIEW.format(items_text)

    full_message_send(context, ot_text, update=update, keyboard=items_keyboard, inbound_keyboard=inbound_keyboard,
                      excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE])


def get_items_text_keyboard(inbound_keyboard: Keyboard, log: Log) -> tuple[str, list[list[Keyboard]]]:
    """
    Get the items text and keyboard

    :param inbound_keyboard: The inbound keyboard
    :param log: The log
    :return: The text and keyboard
    """

    # Get the items
    items, page, start_number, end_number, total_count = get_items_paginate(inbound_keyboard, log)

    # Get the text
    items_text = ''
    inline_keyboard: list[list[Keyboard]] = []
    keyboard_line: list[Keyboard] = []

    for index, item in enumerate(items):
        current_number = start_number + index
        log.set_object(item.id)
        items_text += phrases.LIST_ITEM_TEXT.format(current_number, log.get_item_text())

        button_info = {LogTypeReservedKeys.ITEM_ID: item.id}
        button = Keyboard(str(current_number), screen=Screen.PVT_LOGS_TYPE_DETAIL, info=button_info,
                          inbound_info=inbound_keyboard.info)
        keyboard_line.append(button)

        # Add new keyboard line if needed
        if (index + 1) % c.STANDARD_LIST_KEYBOARD_ROW_SIZE == 0 and index != 0:
            inline_keyboard.append(keyboard_line)
            keyboard_line = []

    # Add the last keyboard line if needed
    if len(keyboard_line) > 0:
        inline_keyboard.append(keyboard_line)

    # Add list text footer and navigation buttons if needed
    if total_count > c.STANDARD_LIST_SIZE:
        items_text += phrases.LIST_FOOTER.format(start_number, end_number, total_count)
        inline_keyboard.append(get_navigation_buttons(inbound_keyboard, page))

    return items_text, inline_keyboard


def get_items_paginate(inbound_keyboard: Keyboard, log: Log) -> [list[Log], int, int, int, int]:
    """
    Get the items, page, start number, end number and the total number of items

    :param inbound_keyboard: The inbound keyboard
    :param log: The log
    :return: The items, start number, end number and the total number of items
    """

    # Get the page number
    page = get_page(inbound_keyboard)

    # Get the items
    items = log.get_items(page)

    # Items 0 and page > 1, raise limit error
    if len(items) == 0 and page > 1:
        raise NavigationLimitReachedException()

    # Get the start index
    start_number: int = (page - 1) * c.STANDARD_LIST_SIZE + 1
    # Get the end index
    end_number: int = start_number + len(items) - 1

    # Get the total number of items
    total_items: int = log.get_total_items_count()

    return items, page, start_number, end_number, total_items