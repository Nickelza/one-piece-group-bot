from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import constants as c
import resources.phrases as phrases
import src.model.enums.CrewRole as CrewRole
from src.chat.private.screens.screen_crew_create import Step
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CustomException import NavigationLimitReachedException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_belly_formatted
from src.service.crew_service import get_crew
from src.service.list_service import get_navigation_buttons
from src.service.message_service import full_message_send, mention_markdown_user, escape_valid_markdown_chars


class CrewReservedKeys(StrEnum):
    """
    The reserved keys for the Crew disband screen
    """
    MEMBER_ID = 'a'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the crew screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    inline_keyboard: list[list[Keyboard]] = []
    if not user.is_crew_member():
        ot_text = phrases.CREW_USER_NOT_IN_CREW

        # Create crew button
        inline_keyboard.append([Keyboard(phrases.KEY_CREATE, screen=Screen.PVT_CREW_CREATE_OR_EDIT)])
    else:
        crew: Crew = get_crew(user=user)

        crew_members_text, crew_members_keyboard = get_crew_members_text_keyboard(inbound_keyboard, crew)

        ot_text = phrases.CREW_OVERVIEW.format(
            escape_valid_markdown_chars(crew.name),
            get_belly_formatted(crew.chest_amount),
            crew_members_text)
        inline_keyboard = crew_members_keyboard

        if user.is_crew_captain():
            # Name edit button
            button_info = {ReservedKeyboardKeys.IN_EDIT_ID: crew.id,
                           ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_NAME}
            inline_keyboard.append([Keyboard(phrases.PVT_KEY_CREW_EDIT_NAME, screen=Screen.PVT_CREW_CREATE_OR_EDIT,
                                             info=button_info)])

            # Disband button
            inline_keyboard.append([Keyboard(phrases.PVT_KEY_CREW_DISBAND, screen=Screen.PVT_CREW_DISBAND,
                                             info=button_info)])
        else:
            # Leave crew button
            inline_keyboard.append([Keyboard(phrases.PVT_KEY_CREW_LEAVE, screen=Screen.PVT_CREW_LEAVE)])

    await full_message_send(context, ot_text, update=update, keyboard=inline_keyboard,
                            inbound_keyboard=inbound_keyboard,
                            excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE])


def get_crew_members_paginate(inbound_keyboard: Keyboard, crew: Crew) -> [list[User], int, int, int, int]:
    """
    Get the crew members, page, start number, end number and the total number of items

    :param inbound_keyboard: The inbound keyboard
    :param crew: The crew
    :return: The crew members, start number, end number and the total number of items
    """

    # Get the page number
    if ReservedKeyboardKeys.PAGE in inbound_keyboard.info:
        page = inbound_keyboard.info[ReservedKeyboardKeys.PAGE]
    else:
        page = 1

    # Page less than 1, raise limit error
    if page < 1:
        raise NavigationLimitReachedException()

    # Get the crew members
    crew_members: list[User] = crew.get_members(limit=c.STANDARD_LIST_SIZE, page=page)

    # Items 0 and page > 1, raise limit error
    if len(crew_members) == 0 and page > 1:
        raise NavigationLimitReachedException()

    # Get the start index
    start_number: int = (page - 1) * c.STANDARD_LIST_SIZE + 1
    # Get the end index
    end_number: int = start_number + len(crew_members) - 1

    # Get the total number of crew members
    total_crew_members: int = crew.get_member_count()

    return crew_members, page, start_number, end_number, total_crew_members


def get_crew_members_text_keyboard(inbound_keyboard: Keyboard, crew: Crew) -> tuple[str, list[list[Keyboard]]]:
    """
    Get the crew members text and keyboard

    :param inbound_keyboard: The inbound keyboard
    :param crew: The crew
    :return: The crew members text and keyboard
    """

    # Get the crew members
    crew_members, page, start_number, end_number, total_count = get_crew_members_paginate(inbound_keyboard, crew)

    # Get the crew members text
    crew_members_text = ''
    inline_keyboard: list[list[Keyboard]] = []
    keyboard_line: list[Keyboard] = []

    for index, crew_member in enumerate(crew_members):
        current_number = start_number + index
        if crew_member.crew_role is None:
            crew_members_text += phrases.CREW_OVERVIEW_MEMBER.format(current_number, mention_markdown_user(crew_member))
        else:
            crew_role = CrewRole.CREW_ROLE_NAME_MAP[CrewRole.CrewRole(crew_member.crew_role)]
            crew_members_text += phrases.CREW_OVERVIEW_MEMBER_ROLE.format(current_number,
                                                                          crew_member.get_markdown_mention(), crew_role)

        button_info = {CrewReservedKeys.MEMBER_ID: crew_member.id}
        button = Keyboard(str(current_number), screen=Screen.PVT_CREW_MEMBER, info=button_info,
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
        crew_members_text += phrases.LIST_FOOTER.format(start_number, end_number, total_count)
        inline_keyboard.append(get_navigation_buttons(inbound_keyboard, page))

    return crew_members_text, inline_keyboard
