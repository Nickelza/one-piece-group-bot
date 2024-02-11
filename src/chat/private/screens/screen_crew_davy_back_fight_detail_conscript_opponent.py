import datetime

from telegram import Update
from telegram.ext import ContextTypes

import constants as c
from resources import phrases
from src.model.Crew import Crew
from src.model.DavyBackFight import DavyBackFight
from src.model.User import User
from src.model.enums.Notification import (
    CrewConscriptionStartNotification,
    CrewConscriptionStartCaptainNotification,
)
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.enums.crew.CrewRole import CrewRole
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import remove_member, add_member
from src.service.message_service import full_message_send, get_yes_no_keyboard
from src.service.notification_service import send_notification


async def validate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
    davy_back_fight: DavyBackFight,
) -> bool:
    """
    Validate the Davy Back Fight opponent conscription
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param davy_back_fight: The Davy Back Fight
    :return: True if the crew is valid, False otherwise
    """
    try:
        # Penalty period ended
        if not davy_back_fight.in_penalty_period():
            raise CrewValidationException(
                phrases.CREW_DAVY_BACK_FIGHT_OPPONENT_CONSCRIPT_ERROR_PENALTY_PERIOD_ENDED
            )

        # Already conscripted
        if davy_back_fight.conscript is not None:
            raise CrewValidationException(
                phrases.CREW_DAVY_BACK_FIGHT_OPPONENT_CONSCRIPT_ERROR_ALREADY_CONSCRIPTED
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
    crew: Crew = user.crew

    if not await validate(update, context, inbound_keyboard, dbf):
        return

    # Choose conscript
    if not inbound_keyboard.has_key(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY):
        await choose_conscript(update, context, inbound_keyboard, crew, dbf)
        return

    # Not confirmed, show the confirmation screen
    if not (
        inbound_keyboard.has_key(ReservedKeyboardKeys.CONFIRM)
        and inbound_keyboard.get(ReservedKeyboardKeys.CONFIRM)
    ):
        await request_confirmation(update, context, inbound_keyboard)
        return

    conscript: User = User.get_by_id(
        inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY)
    )
    captain_of_previous_crew: User = conscript.crew.get_captain()

    # Remove from old Crew
    await remove_member(conscript, from_davy_back_fight_conscript=True)
    # Add to new Crew
    await add_member(
        conscript, crew, CrewRole.CONSCRIPT, conscription_end_date=dbf.penalty_end_date
    )

    dbf.conscript = conscript
    dbf.conscript_date = datetime.datetime.now()
    dbf.save()

    # Send notification to user and captain
    await send_notification(
        context, conscript, CrewConscriptionStartNotification(conscript), update=update
    )
    await send_notification(
        context,
        captain_of_previous_crew,
        CrewConscriptionStartCaptainNotification(conscript),
        update=update,
    )

    # Add view member button
    inline_keyboard = [[
        Keyboard(
            phrases.KEY_VIEW,
            screen=Screen.PVT_CREW_MEMBER_DETAIL,
            info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: conscript.id},
            previous_screen_list=[Screen.PVT_CREW],
        )
    ]]

    await full_message_send(
        context,
        phrases.CREW_DAVY_BACK_FIGHT_OPPONENT_CONSCRIPT_SUCCESS.format(
            conscript.get_markdown_mention()
        ),
        update=update,
        inbound_keyboard=inbound_keyboard,
        keyboard=inline_keyboard,
        excluded_keys_from_back_button=[ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY],
    )


async def choose_conscript(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
    crew: Crew,
    davy_back_fight: DavyBackFight,
):
    """
    Get the opponents keyboard
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param crew: The crew
    :param davy_back_fight: The Davy Back Fight
    :return: None
    """

    opponent_crew: Crew = davy_back_fight.get_opponent_crew(crew)
    participants: list[User] = davy_back_fight.get_participants_users(crew=opponent_crew)

    keyboard: list[list[Keyboard]] = [[]]
    keyboard_row: list[Keyboard] = []

    for user in participants:
        if user.is_crew_captain_or_first_mate():
            continue

        button: Keyboard = Keyboard(
            user.tg_first_name,
            info={ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY: user.id},
            inbound_info=inbound_keyboard.info,
        )

        if len(keyboard_row) == c.FEATURE_KEYBOARD_ROW_SIZE:
            keyboard.append(keyboard_row)
            keyboard_row = []

        keyboard_row.append(button)

    if len(keyboard_row) > 0:
        keyboard.append(keyboard_row)

    await full_message_send(
        context,
        phrases.CREW_DAVY_BACK_FIGHT_OPPONENT_CONSCRIPT_CHOOSE_CONSCRIPT.format(
            davy_back_fight.get_penalty_remaining_time()
        ),
        update=update,
        keyboard=keyboard,
        inbound_keyboard=inbound_keyboard,
        excluded_keys_from_back_button=[ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY],
    )


async def request_confirmation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
):
    """
    Request confirmation to conscript the opponent
    :param update: The update object
    :param context: The context object
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    conscript: User = User.get_by_id(
        inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY)
    )

    ot_text = phrases.CREW_DAVY_BACK_FIGHT_OPPONENT_CONSCRIPT_CHOOSE_CONFIRMATION_REQUEST.format(
        conscript.get_markdown_mention()
    )

    inline_keyboard: list[list[Keyboard]] = [
        get_yes_no_keyboard(
            screen=inbound_keyboard.screen,
            inbound_keyboard=inbound_keyboard,
            add_inbound_key_info=True,
            no_keys_to_exclude=[
                ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY,
            ],
        )
    ]

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
        excluded_keys_from_back_button=[ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY],
    )
