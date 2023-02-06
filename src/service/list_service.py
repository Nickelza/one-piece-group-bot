from enum import StrEnum

import constants as c
import resources.phrases as phrases
from src.model.BaseModel import BaseModel
from src.model.enums.ListPage import ListPage
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CustomException import NavigationLimitReachedException
from src.model.pojo.Keyboard import Keyboard


def get_navigation_buttons(inbound_keyboard: Keyboard, current_page: int) -> list[Keyboard]:
    """
    Returns the navigation buttons for the crew member list
    :param inbound_keyboard: The inbound keyboard
    :param current_page: The current page
    :return: The navigation buttons
    """

    keyboard_line: list[Keyboard] = []

    # Previous page
    previous_page_button_info = {ReservedKeyboardKeys.PAGE: current_page - 1}
    keyboard_line.append(Keyboard(phrases.PVT_KEY_PREVIOUS_PAGE, info=previous_page_button_info,
                                  inbound_info=inbound_keyboard.info))

    # Next page
    next_page_button_info = {ReservedKeyboardKeys.PAGE: current_page + 1}
    keyboard_line.append(Keyboard(phrases.PVT_KEY_NEXT_PAGE, info=next_page_button_info,
                                  inbound_info=inbound_keyboard.info))

    return keyboard_line


def get_page(inbound_keyboard: Keyboard) -> int:
    """
    Get the page number. Raises a NavigationLimitReachedException if the page is less than 1
    :param inbound_keyboard: The inbound keyboard
    :return: The page number
    """

    # Get the page number
    if ReservedKeyboardKeys.PAGE in inbound_keyboard.info:
        page = inbound_keyboard.info[ReservedKeyboardKeys.PAGE]
        if page < 1:
            raise NavigationLimitReachedException()
        return page

    return 1


def get_items_paginate(inbound_keyboard: Keyboard, list_page: ListPage) -> [list[BaseModel], int, int, int, int]:
    """
    Get the items, page, start number, end number and the total number of items

    :param inbound_keyboard: The inbound keyboard
    :param list_page: The list page object
    :return: The items, start number, end number and the total number of items
    """

    # Get the page number
    page = get_page(inbound_keyboard)

    # Get the items
    items = list_page.get_items(page)

    # Items 0 and page > 1, raise limit error
    if len(items) == 0 and page > 1:
        raise NavigationLimitReachedException()

    # Get the start index
    start_number: int = (page - 1) * c.STANDARD_LIST_SIZE + 1
    # Get the end index
    end_number: int = start_number + len(items) - 1

    # Get the total number of items
    total_items: int = list_page.get_total_items_count()

    return items, page, start_number, end_number, total_items


def get_items_text_keyboard(inbound_keyboard: Keyboard, list_page: ListPage, item_detail_key: StrEnum,
                            item_detail_screen: Screen) -> tuple[str, list[list[Keyboard]]]:
    """
    Get the items text and keyboard

    :param inbound_keyboard: The inbound keyboard
    :param list_page: The list page
    :param item_detail_key: The item detail keyboard key
    :param item_detail_screen: The item detail screen
    :return: The text and keyboard
    """

    # Get the items
    items, page, start_number, end_number, total_count = get_items_paginate(inbound_keyboard, list_page)

    # Get the text
    items_text = ''
    inline_keyboard: list[list[Keyboard]] = []
    keyboard_line: list[Keyboard] = []

    for index, item in enumerate(items):
        current_number = start_number + index
        list_page.set_object(item.id)
        items_text += phrases.LIST_ITEM_TEXT.format(current_number, list_page.get_item_text())

        button_info = {item_detail_key: item.id}
        button = Keyboard(str(current_number), screen=item_detail_screen, info=button_info,
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
