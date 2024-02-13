from enum import StrEnum

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes

import constants as c
from resources import phrases
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew
from src.service.message_service import full_message_send


class ScreenReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    MEMBER_TO_SWAP = "c"


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    crew: Crew = user.crew

    # Crew has at least a member without priority set, refresh
    if User.get_or_none(crew=crew, crew_davy_back_fight_priority=None) is not None:
        crew.set_davy_back_fight_priority()

    # Reset
    if inbound_keyboard.has_key(ReservedKeyboardKeys.RESET):
        crew.set_davy_back_fight_priority(should_reset=True)
        await full_message_send(
            context,
            phrases.RESET_SUCCESSFUL,
            update=update,
            answer_callback=True,
        )
        inbound_keyboard.info.pop(ReservedKeyboardKeys.RESET)

    # Create keyboard and members text
    inline_keyboard: list[list[Keyboard]] = []

    # Reset button
    keyboard_reset = [
        Keyboard(
            phrases.KEYBOARD_OPTION_RESET,
            screen=inbound_keyboard.screen,
            info={ReservedKeyboardKeys.RESET: True},
        )
    ]

    explanation_text = phrases.CREW_EDIT_DAVY_BACK_FIGHT_PRIORITY_EXPLANATION
    if inbound_keyboard.has_key(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY):
        old_swap: User = User.get_by_id(
            inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY)
        )
        get_crew(old_swap, validate_against_crew=crew)

        # Swap priority with other member
        if inbound_keyboard.has_key(ScreenReservedKeys.MEMBER_TO_SWAP):
            new_swap: User = User.get_by_id(
                inbound_keyboard.info[ScreenReservedKeys.MEMBER_TO_SWAP]
            )
            get_crew(new_swap, validate_against_crew=crew)

            # Swap priority
            old_swap.crew_davy_back_fight_priority, new_swap.crew_davy_back_fight_priority = (
                new_swap.crew_davy_back_fight_priority,
                old_swap.crew_davy_back_fight_priority,
            )
            old_swap.save()
            new_swap.save()

            inbound_keyboard.info.pop(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY)
            inbound_keyboard.info.pop(ScreenReservedKeys.MEMBER_TO_SWAP)

            # Swap successful alert
            await full_message_send(
                context,
                phrases.SWAP_SUCCESSFUL,
                update=update,
                answer_callback=True,
            )

            overview_text = phrases.CREW_EDIT_DAVY_BACK_FIGHT_PRIORITY_SELECT_USER
            inline_keyboard.append(keyboard_reset)
        else:
            overview_text = phrases.CREW_EDIT_DAVY_BACK_FIGHT_PRIORITY_SELECT_SWAP.format(
                old_swap.get_markdown_mention()
            )
            explanation_text = ""

            # Cancel button
            info = inbound_keyboard.info.copy()
            info.pop(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY)
            info.pop(ScreenReservedKeys.MEMBER_TO_SWAP, None)
            inline_keyboard.append(
                [
                    Keyboard(
                        phrases.KEYBOARD_OPTION_CANCEL,
                        inbound_info=info,
                    )
                ]
            )
    else:
        overview_text = phrases.CREW_EDIT_DAVY_BACK_FIGHT_PRIORITY_SELECT_USER
        inline_keyboard.append(keyboard_reset)

    # Adding numeric keyboard later so the info won't contain keys that might suppose to have been
    # removed
    members: list[User] = crew.get_members_order_by_davy_back_fight_priority()
    items_text = ""
    keyboard_line: list[Keyboard] = []
    numeric_keyboard: list[list[Keyboard]] = []
    for index, member in enumerate(members):
        current_number = index + 1
        items_text += phrases.LIST_ITEM_TEXT.format(current_number, member.get_markdown_mention())

        key = (
            ScreenReservedKeys.MEMBER_TO_SWAP
            if inbound_keyboard.has_key(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY)
            else ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY
        )

        button = Keyboard(
            str(current_number),
            screen=inbound_keyboard.screen,
            info={key: member.id},
            inbound_info=inbound_keyboard.info,
        )
        keyboard_line.append(button)

        # Add new keyboard line if needed
        if (index + 1) % c.STANDARD_LIST_KEYBOARD_ROW_SIZE == 0 and index != 0:
            numeric_keyboard.append(keyboard_line)
            keyboard_line = []

    # Add the last keyboard line if needed
    if len(keyboard_line) > 0:
        numeric_keyboard.append(keyboard_line)

    inline_keyboard = numeric_keyboard + inline_keyboard

    try:
        await full_message_send(
            context,
            phrases.CREW_EDIT_DAVY_BACK_FIGHT_PRIORITY.format(
                overview_text, items_text, explanation_text
            ),
            update=update,
            keyboard=inline_keyboard,
            inbound_keyboard=inbound_keyboard,
        )
    # List can stay the same in case of reset
    except BadRequest as bre:
        if "Message is not modified" not in str(bre):
            raise bre
