from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import constants as c
import resources.phrases as phrases
from src.model.BaseModel import BaseModel
from src.model.User import User
from src.model.enums.ContextDataKey import ContextDataKey
from src.model.enums.ListPage import ListPage, ListFilter, ListFilterType
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CustomException import NavigationLimitReachedException
from src.model.pojo.Keyboard import Keyboard
from src.service.english_phrase_service import determine_article


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
    keyboard_line.append(
        Keyboard(
            phrases.PVT_KEY_PREVIOUS_PAGE,
            info=previous_page_button_info,
            inbound_info=inbound_keyboard.info,
        )
    )

    # Next page
    next_page_button_info = {ReservedKeyboardKeys.PAGE: current_page + 1}
    keyboard_line.append(
        Keyboard(
            phrases.PVT_KEY_NEXT_PAGE,
            info=next_page_button_info,
            inbound_info=inbound_keyboard.info,
        )
    )

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


def get_items_paginate(
    inbound_keyboard: Keyboard, list_page: ListPage
) -> [list[BaseModel], int, int, int, int, int]:
    """
    Get the items, page, start number, end number, total number of items
    and all items without filter count

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

    # Get all items count, without any filter
    all_items_count: int = list_page.get_total_items_no_filter_count()

    return items, page, start_number, end_number, total_items, all_items_count


def get_items_text_keyboard(
    inbound_keyboard: Keyboard,
    list_page: ListPage,
    item_detail_key: StrEnum,  # TODO default PRIMARY_KEY, switch with screen
    item_detail_screen: Screen,
    text_fill_in: str = None,
    text_overview: str = None,
    context: ContextTypes.DEFAULT_TYPE = None,
    user: User = None,
    update: Update = None,
    allow_string_filter: bool = False,
    empty_list_text: str = None,
) -> tuple[str, list[list[Keyboard]]]:
    """
    Get the items text and keyboard

    :param inbound_keyboard: The inbound keyboard
    :param list_page: The list page
    :param item_detail_key: The item detail keyboard key
    :param item_detail_screen: The item detail screen
    :param text_fill_in: The text fill in
    :param text_overview: The text overview
    :param context: The context
    :param user: The user
    :param update: The update
    :param allow_string_filter: Whether to allow string filter
    :param empty_list_text: The empty list text
    :return: The text and keyboard
    """
    list_page.init_legend_filter_results()

    # Add string filter to context data
    if allow_string_filter:

        # Simulate always having an inbound keyboard
        if inbound_keyboard is not None:
            user.set_context_data(context, ContextDataKey.INBOUND_KEYBOARD, inbound_keyboard)
        else:
            inbound_keyboard = user.get_context_data(context, ContextDataKey.INBOUND_KEYBOARD)
            inbound_keyboard.is_simulated = True

        try:
            if not inbound_keyboard.is_simulated:
                raise AttributeError

            list_page.string_filter = update.effective_message.text
            user.set_context_data(
                context,
                ContextDataKey.FILTER,
                list_page.string_filter,
                list_page.get_string_filter_key(),
            )
        except AttributeError:
            list_page.string_filter = user.get_context_data_or_none(
                context, ContextDataKey.FILTER, list_page.get_string_filter_key()
            )

    # Set active filters
    active_filters = get_active_filter_list(inbound_keyboard, list_page, context, user)
    list_page.filter_list_active = active_filters

    # Get the items
    items, page, start_number, end_number, total_count, all_items_no_filter_count = (
        get_items_paginate(inbound_keyboard, list_page)
    )

    # Get the text
    inline_keyboard: list[list[Keyboard]] = []
    items_text = ""

    # No items
    if total_count == 0:
        items_text = (
            phrases.LIST_OVERVIEW_NO_ITEMS.format(text_fill_in)
            if empty_list_text is None
            else empty_list_text
        )

        if all_items_no_filter_count == 0:
            return items_text, inline_keyboard

    keyboard_line: list[Keyboard] = []

    for index, item in enumerate(items):
        current_number = start_number + index
        list_page.set_object(item.id)
        items_text += phrases.LIST_ITEM_TEXT.format(current_number, list_page.get_item_text())

        button_info = {item_detail_key: item.id}
        button = Keyboard(
            str(current_number),
            screen=item_detail_screen,
            info=button_info,
            inbound_info=inbound_keyboard.info,
        )
        keyboard_line.append(button)

        # Add new keyboard line if needed
        if (index + 1) % c.STANDARD_LIST_KEYBOARD_ROW_SIZE == 0 and index != 0:
            inline_keyboard.append(keyboard_line)
            keyboard_line = []

    # Add the last keyboard line if needed
    if len(keyboard_line) > 0:
        inline_keyboard.append(keyboard_line)

    # Add navigation buttons if needed
    if total_count > c.STANDARD_LIST_SIZE:
        inline_keyboard.append(get_navigation_buttons(inbound_keyboard, page))

    # Add filters button
    string_filter: ListFilter | None = None
    add_legend_filter = False
    has_added_legend_filter = False

    filters = list_page.get_filter_list()

    legend_filters = [f for f in filters if f.filter_type is ListFilterType.LEGEND]
    legend_filters_with_items = [
        f for f in legend_filters if len(list_page.legend_filter_results[f.legend]) > 0
    ]
    active_legend_filters = [f for f in active_filters if f.filter_type is ListFilterType.LEGEND]

    for index, list_filter in enumerate(list_page.get_filter_list()):
        key = list_page.get_filter_key(index)
        if list_filter.filter_type is ListFilterType.LEGEND:
            if has_added_legend_filter:
                continue

            # In case no active legend filters, first one will be added
            if len(active_legend_filters) > 0:
                # Legend filter but not current one
                filter_value = get_legend_filter_value(inbound_keyboard, key)
                if not filter_value and not add_legend_filter:
                    continue

                # Current active legend filter, should add button of next filter
                if filter_value:
                    inbound_keyboard.info.pop(key)  # Else it will stack
                    user.remove_context_data(context, ContextDataKey.FILTER, inner_key=key)
                    add_legend_filter = True

                    # No next filter, add remove button
                    if list_filter.description == legend_filters_with_items[-1].description:
                        inline_keyboard.append([
                            Keyboard(
                                phrases.PVT_KEY_STRING_FILTER_REMOVE.format(phrases.LEGEND),
                                screen=inbound_keyboard.screen,
                                info={key: False, ReservedKeyboardKeys.PAGE: 1},
                                inbound_info=inbound_keyboard.info,
                            )
                        ])

                    continue

            # Doesn't have items, don't add button
            if len(list_page.legend_filter_results[list_filter.legend]) == 0:
                continue

            # Is the filter of which to add the button
            inline_keyboard.append([
                Keyboard(
                    list_filter.legend.get_formatted()
                    + phrases.TEXT_ONLY.format(list_filter.description),
                    screen=inbound_keyboard.screen,
                    info={key: True, ReservedKeyboardKeys.PAGE: 1},
                    inbound_info=inbound_keyboard.info,
                )
            ])
            has_added_legend_filter = True

        elif list_filter.filter_type is ListFilterType.STRING:
            string_filter = list_filter
            current_value: str = get_string_filter_value(context, key, user)
            if current_value is not None:
                # Add remove filter button
                inline_keyboard.append([
                    Keyboard(
                        phrases.PVT_KEY_STRING_FILTER_REMOVE.format(list_filter.description),
                        screen=inbound_keyboard.screen,
                        info={key: False, ReservedKeyboardKeys.PAGE: 1},
                        inbound_info=inbound_keyboard.info,
                    )
                ])

    if len(list_page.emoji_legend_list) > 0 and list_page.show_legend_list:
        items_text += list_page.get_emoji_legend_list_text()

    # Add string filter suggestion
    if string_filter is not None:
        items_text += phrases.LIST_FILTER_SEND_PART_OF_STRING.format(string_filter.description)

    # Add active filters recap
    if len(active_filters) > 0:
        active_filters_text = ""
        for active_filter in active_filters:

            if active_filter.filter_type is ListFilterType.STRING:
                inner_text = phrases.LIST_FILTER_ITEM_CONTAINS.format(
                    active_filter.description, active_filter.value
                )
            else:
                inner_text = phrases.LIST_FILTER_ONLY.format(active_filter.description)

            active_filters_text += phrases.LIST_FILTER_ITEM.format(inner_text)

        items_text += phrases.LIST_FILTER_ACTIVE_FILTERS.format(active_filters_text)

    if total_count > 0:
        # Add list text footer if needed
        if total_count > c.STANDARD_LIST_SIZE:
            items_text += phrases.LIST_FOOTER.format(start_number, end_number, total_count)

        list_overview = text_overview if text_overview is not None else phrases.LIST_OVERVIEW
        if text_fill_in is None:
            items_text = list_overview.format(items_text)
        else:
            items_text = list_overview.format(
                determine_article(text_fill_in), text_fill_in, items_text
            )

    return items_text, inline_keyboard


def get_legend_filter_value(inbound_keyboard: Keyboard, key: str) -> bool:
    """
    Get the legend filter value from the inbound keyboard
    :param inbound_keyboard: The inbound keyboard
    :param key: The key
    :return: The list filter value
    """

    if key in inbound_keyboard.info:
        return inbound_keyboard.info[key]

    return False


def get_string_filter_value(context: ContextTypes.DEFAULT_TYPE, key: str, user: User) -> str:
    """
    Get the string filter value from the context
    :param context: The context
    :param key: The key
    :param user: The user
    :return: The string filter value
    """

    # Get value from context
    return user.get_context_data_or_none(context, ContextDataKey.FILTER, inner_key=key)


def get_active_filter_list(
    inbound_keyboard: Keyboard, list_page: ListPage, context: ContextTypes.DEFAULT_TYPE, user: User
) -> list[ListFilter]:
    """
    Get the active filter list
    :param inbound_keyboard: The inbound keyboard
    :param list_page: The list page
    :param context: The context
    :param user: The user
    :return: The active filter list
    """

    active_filter_list: list[ListFilter] = []

    if inbound_keyboard is not None and not inbound_keyboard.is_simulated:
        for index, list_filter in enumerate(list_page.get_filter_list()):
            key = list_page.get_filter_key(index)
            if key in inbound_keyboard.info:
                value = inbound_keyboard.info[key]
                if value:
                    # Add to context
                    user.set_context_data(context, ContextDataKey.FILTER, value, inner_key=key)
                else:
                    # Remove from context and inbound keyboard
                    user.remove_context_data(context, ContextDataKey.FILTER, inner_key=key)
                    inbound_keyboard.info.pop(key)
                    continue

    # Get active filters from context
    for index, list_filter in enumerate(list_page.get_filter_list()):
        key = list_page.get_filter_key(index)
        value = user.get_context_data_or_none(context, ContextDataKey.FILTER, inner_key=key)

        if not value:
            continue

        list_filter.value = value
        active_filter_list.append(list_filter)

    return active_filter_list


def get_show_list_button(inbound_keyboard: Keyboard) -> Keyboard:
    """
    Get the show list button
    :param inbound_keyboard: The inbound keyboard
    :return: The show list button
    """

    inbound_keyboard.info[ReservedKeyboardKeys.DIRECT_ITEM] = False
    return Keyboard(
        phrases.PVT_KEY_SHOW_ALL,
        inbound_info=inbound_keyboard.info,
    )
