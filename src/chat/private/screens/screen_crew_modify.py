from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.chat.private.screens.screen_crew_create import Step
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew
from src.service.message_service import full_message_send
from src.service.settings_service import get_current_setting_text, get_enabled_emoji


class CrewModifyReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    TOGGLE_ALLOW_VIEW_IN_SEARCH = "b"
    TOGGLE_ALLOW_JOIN_FROM_SEARCH = "c"


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage this screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    crew = get_crew(user=user)
    inline_keyboard: list[list[Keyboard]] = []

    # Manage toggle
    if CrewModifyReservedKeys.TOGGLE_ALLOW_VIEW_IN_SEARCH in inbound_keyboard.info:
        crew.allow_view_in_search = not crew.allow_view_in_search
        inbound_keyboard.info.pop(CrewModifyReservedKeys.TOGGLE_ALLOW_VIEW_IN_SEARCH)
    elif CrewModifyReservedKeys.TOGGLE_ALLOW_JOIN_FROM_SEARCH in inbound_keyboard.info:
        crew.allow_join_from_search = not crew.allow_join_from_search
        inbound_keyboard.info.pop(CrewModifyReservedKeys.TOGGLE_ALLOW_JOIN_FROM_SEARCH)
    crew.save()

    # Name edit button
    button_info = {
        ReservedKeyboardKeys.IN_EDIT_ID: crew.id,
        ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_NAME,
    }
    inline_keyboard.append([
        Keyboard(
            phrases.PVT_KEY_CREW_EDIT_NAME, screen=Screen.PVT_CREW_CREATE_OR_EDIT, info=button_info
        )
    ])

    # Description edit button
    button_info = {
        ReservedKeyboardKeys.IN_EDIT_ID: crew.id,
        ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_DESCRIPTION,
    }
    inline_keyboard.append([
        Keyboard(
            phrases.PVT_KEY_CREW_EDIT_DESCRIPTION,
            screen=Screen.PVT_CREW_CREATE_OR_EDIT,
            info=button_info,
        )
    ])

    # Required bounty edit button
    button_info = {
        ReservedKeyboardKeys.IN_EDIT_ID: crew.id,
        ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_REQUIRED_BOUNTY,
    }
    inline_keyboard.append([
        Keyboard(
            phrases.PVT_KEY_CREW_EDIT_REQUIRED_BOUNTY,
            screen=Screen.PVT_CREW_CREATE_OR_EDIT,
            info=button_info,
        )
    ])

    # Allow view in search edit button
    inline_keyboard.append([
        Keyboard(
            phrases.PVT_KEY_CREW_ALLOW_VIEW_IN_SEARCH.format(
                get_enabled_emoji(not crew.allow_view_in_search)
            ),
            screen=inbound_keyboard.screen,
            info={CrewModifyReservedKeys.TOGGLE_ALLOW_VIEW_IN_SEARCH: True},
        )
    ])

    # Allow join from search edit button
    inline_keyboard.append([
        Keyboard(
            phrases.PVT_KEY_CREW_ALLOW_JOIN_FROM_SEARCH.format(
                get_enabled_emoji(not crew.allow_join_from_search)
            ),
            screen=inbound_keyboard.screen,
            info={CrewModifyReservedKeys.TOGGLE_ALLOW_JOIN_FROM_SEARCH: True},
        )
    ])

    # Disband button
    inline_keyboard.append(
        [Keyboard(phrases.PVT_KEY_CREW_DISBAND, screen=Screen.PVT_CREW_DISBAND, info=button_info)]
    )

    ot_text = phrases.CREW_MODIFY.format(
        crew.get_name_escaped(),
        (crew.get_description_escaped() if crew.description is not None else phrases.TEXT_NOT_SET),
        crew.get_required_bounty_formatted(),
        get_current_setting_text(crew.allow_view_in_search),
        get_current_setting_text(crew.allow_join_from_search),
    )

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )
