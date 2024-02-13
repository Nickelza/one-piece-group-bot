from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import constants as c
from resources import phrases
from src.model.Crew import Crew
from src.model.DavyBackFight import DavyBackFight
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.GameStatus import GameStatus
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew
from src.service.date_service import get_remaining_duration
from src.service.davy_back_fight_service import swap_participant
from src.service.message_service import full_message_send


class ScreenReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    MEMBER_TO_SWAP = "c"


async def validate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
    crew: Crew,
    davy_back_fight: DavyBackFight,
) -> bool:
    """
    Validate the Davy Back Fight participants select screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param crew: The crew
    :param davy_back_fight: The Davy Back Fight if already created
    :return: True if the crew is valid, False otherwise
    """

    # No member selected, it's okay to just view list
    if not inbound_keyboard.has_key(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY):
        return True

    try:
        # Already started
        if davy_back_fight.get_status() is not GameStatus.COUNTDOWN_TO_START:
            raise CrewValidationException(
                phrases.CREW_DAVY_BACK_FIGHT_PARTICIPANTS_SELECT_ERROR_ALREADY_STARTED
            )

        # No extra member to swap with
        if crew.get_member_count() == davy_back_fight.participants_count:
            raise CrewValidationException(
                phrases.CREW_DAVY_BACK_FIGHT_PARTICIPANTS_SELECT_ERROR_NOT_ENOUGH_MEMBERS
            )

        return True
    except CrewValidationException as e:
        await full_message_send(
            context,
            str(e),
            update=update,
            answer_callback=True,
            show_alert=True,
            inbound_keyboard=inbound_keyboard,
        )

        return False


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

    dbf: DavyBackFight = DavyBackFight.get_by_id(
        inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY)
    )
    crew: Crew = get_crew(user)

    # Allow members view even in case they can't be changed, only if no member is selected
    if not await validate(update, context, inbound_keyboard, crew, dbf):
        return

    filter_participant: bool | None = None
    if ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY in inbound_keyboard.info:
        member: User = User.get_by_id(
            inbound_keyboard.info[ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY]
        )
        is_participant: bool = member in dbf.get_participants_users(crew=crew)

        # Add or remove participant
        if ScreenReservedKeys.MEMBER_TO_SWAP in inbound_keyboard.info:
            member_to_swap: User = User.get_by_id(
                inbound_keyboard.info[ScreenReservedKeys.MEMBER_TO_SWAP]
            )
            old_participant: User = member if is_participant else member_to_swap
            new_participant: User = member_to_swap if is_participant else member
            swap_participant(dbf, old_participant, new_participant)
            inbound_keyboard.info.pop(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY)
            inbound_keyboard.info.pop(ScreenReservedKeys.MEMBER_TO_SWAP)
            ot_text = phrases.CREW_DAVY_BACK_FIGHT_PARTICIPANTS_SELECT.format(
                get_remaining_duration(dbf.start_date)
            )

            # Refresh the dbf object
            dbf = DavyBackFight.get_by_id(dbf.id)

            # Swap successful alert
            await full_message_send(
                context,
                phrases.SWAP_SUCCESSFUL,
                update=update,
                answer_callback=True,
            )
        else:
            filter_participant = not is_participant
            ot_text = phrases.CREW_DAVY_BACK_FIGHT_PARTICIPANTS_SELECT_SWAP
    else:
        ot_text = phrases.CREW_DAVY_BACK_FIGHT_PARTICIPANTS_SELECT.format(
            get_remaining_duration(dbf.start_date)
        )

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=get_members_keyboard(inbound_keyboard, crew, dbf, filter_participant),
        inbound_keyboard=inbound_keyboard,
    )


def get_members_keyboard(
    inbound_keyboard: Keyboard,
    crew: Crew,
    davy_back_fight: DavyBackFight,
    filter_participant: bool | None,
) -> list[list[Keyboard]]:
    """
    Get the members keyboard
    :param inbound_keyboard: The inbound keyboard
    :param crew: The crew
    :param davy_back_fight: The Davy Back Fight
    :param filter_participant: If to filter the participants
    :return: The keyboard
    """

    members: list[User] = []
    participants: list[User] = davy_back_fight.get_participants_users(crew=crew)

    # Show all members
    if filter_participant is None:
        members = crew.get_members()
    elif filter_participant:  # Only those participating
        members = participants
    elif not filter_participant:  # Only those not participating
        members = davy_back_fight.get_non_participants_users(crew)

    keyboard: list[list[Keyboard]] = [[]]
    keyboard_row: list[Keyboard] = []

    for member in members:
        is_participant = member in participants
        emoji = Emoji.ENABLED if is_participant else Emoji.DISABLED_EMPTY
        key = (
            ScreenReservedKeys.MEMBER_TO_SWAP
            if ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY in inbound_keyboard.info
            else ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY
        )
        button: Keyboard = Keyboard(
            f"{emoji} {member.tg_first_name}",
            info={key: member.id},
            inbound_info=inbound_keyboard.info,
        )

        if len(keyboard_row) == c.FEATURE_KEYBOARD_ROW_SIZE:
            keyboard.append(keyboard_row)
            keyboard_row = []

        keyboard_row.append(button)

    if len(keyboard_row) > 0:
        keyboard.append(keyboard_row)

    # Cancel button
    if inbound_keyboard.has_key(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY):
        info = inbound_keyboard.info.copy()
        info.pop(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY)
        info.pop(ScreenReservedKeys.MEMBER_TO_SWAP, None)
        keyboard.append(
            [
                Keyboard(
                    phrases.KEYBOARD_OPTION_CANCEL,
                    inbound_info=info,
                )
            ]
        )

    return keyboard
