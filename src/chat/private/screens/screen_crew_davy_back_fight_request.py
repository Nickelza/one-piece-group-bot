from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import constants as c
import resources.Environment as Env
import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.DavyBackFight import DavyBackFight
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CustomException import CrewValidationException
from src.model.error.PrivateChatError import PrivateChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_next_bounty_reset_time
from src.service.crew_service import get_crew
from src.service.date_service import (
    get_datetime_in_future_hours,
    convert_minutes_to_duration,
    datetime_is_before,
)
from src.service.message_service import full_message_send, get_yes_no_keyboard


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage this screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    try:
        challenger_crew: Crew = get_crew(user)
    except CrewValidationException as cve:
        await full_message_send(
            context, cve.message, update=update, inbound_keyboard=inbound_keyboard
        )
        return

    opponent_crew: Crew = Crew.logical_get(
        inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY)
    )

    if not await validate(update, context, inbound_keyboard, challenger_crew, opponent_crew):
        return

    # Request number of participants
    if ReservedKeyboardKeys.NUMBER not in inbound_keyboard.info:
        await request_number_of_participants(
            update, context, inbound_keyboard, challenger_crew, opponent_crew
        )
        return

    # Request confirmation
    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        await request_confirmation(update, context, inbound_keyboard, challenger_crew, user)
        return

    # Sending the join request to the crew captain
    await send_request_to_captain(
        context,
        challenger_crew,
        opponent_crew,
        inbound_keyboard.get_int(ReservedKeyboardKeys.NUMBER),
    )

    await full_message_send(
        context,
        phrases.CREW_DAVY_BACK_FIGHT_REQUEST_SUCCESS.format(opponent_crew.get_name_escaped()),
        update=update,
        inbound_keyboard=inbound_keyboard,
    )


async def validate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
    challenger_crew: Crew,
    opponent_crew: Crew,
    davy_back_fight: DavyBackFight = None,
) -> bool:
    """
    Validate the Davy Back Fight Request
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param challenger_crew: The challenger
    :param opponent_crew: The opponent
    :param davy_back_fight: The Davy Back Fight if already created
    :return: True if the crew is valid, False otherwise
    """

    try:
        # Challenger crew and opponent crew are the same
        if challenger_crew == opponent_crew:
            raise CrewValidationException(phrases.CREW_DAVY_BACK_FIGHT_REQUEST_ERROR_SAME_CREW)

        # Challenger or opponent crew does not have the minimum required members
        if (
            challenger_crew.get_member_count() < Env.DAVY_BACK_FIGHT_MINIMUM_PARTICIPANTS.get_int()
            or opponent_crew.get_member_count()
            < Env.DAVY_BACK_FIGHT_MINIMUM_PARTICIPANTS.get_int()
        ):
            raise CrewValidationException(
                phrases.CREW_DAVY_BACK_FIGHT_REQUEST_ERROR_MINIMUM_PARTICIPANTS.format(
                    Env.DAVY_BACK_FIGHT_MINIMUM_PARTICIPANTS.get_int()
                )
            )

        # Challenger or opponent crew is already in a DBF
        if (
            challenger_crew.get_active_davy_back_fight() is not None
            or opponent_crew.get_active_davy_back_fight() is not None
        ):
            raise CrewValidationException(
                phrases.CREW_DAVY_BACK_FIGHT_REQUEST_ERROR_ALREADY_IN_FIGHT
            )

        # Challenger crew already has a pending request
        pending_request: DavyBackFight = challenger_crew.get_pending_davy_back_fight()
        if pending_request is not None and pending_request != davy_back_fight:
            raise CrewValidationException(
                phrases.CREW_DAVY_BACK_FIGHT_REQUEST_ERROR_ALREADY_PENDING
            )

        # Challenger or opponent currently in penalty period due to a lost DBF
        if (
            challenger_crew.get_penalty_davy_back_fight() is not None
            or opponent_crew.get_penalty_davy_back_fight() is not None
        ):
            raise CrewValidationException(
                phrases.CREW_DAVY_BACK_FIGHT_REQUEST_ERROR_IN_PENALTY_PERIOD
            )

        # DBF cannot be initiated less than x time before bounty reset
        if datetime_is_before(
            get_next_bounty_reset_time(),
            get_datetime_in_future_hours(
                Env.DAVY_BACK_FIGHT_BOUNTY_RESET_COOLDOWN_DURATION.get_int()
            ),
        ):
            raise CrewValidationException(
                phrases.CREW_DAVY_BACK_FIGHT_REQUEST_ERROR_TOO_LATE.format(
                    Env.DAVY_BACK_FIGHT_BOUNTY_RESET_COOLDOWN_DURATION.get_int()
                )
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


async def request_number_of_participants(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
    challenger_crew: Crew,
    opponent_crew: Crew,
) -> None:
    """
    Request the number of participants
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param challenger_crew: The crew
    :param opponent_crew: The opponent crew
    :return: None
    """

    min_participants = Env.DAVY_BACK_FIGHT_MINIMUM_PARTICIPANTS.get_int()
    max_participants = min(challenger_crew.get_member_count(), opponent_crew.get_member_count())

    # Create numeric keyboard with all possible values
    numeric_keyboard: list[list[Keyboard]] = []
    line_keyboard: list[Keyboard] = []
    for i in range(min_participants, max_participants + 1):
        line_keyboard.append(
            Keyboard(
                str(i), info={ReservedKeyboardKeys.NUMBER: i}, inbound_info=inbound_keyboard.info
            )
        )
        if len(line_keyboard) == c.STANDARD_LIST_KEYBOARD_ROW_SIZE:
            numeric_keyboard.append(line_keyboard)
            line_keyboard = []

    if len(line_keyboard) > 0:
        numeric_keyboard.append(line_keyboard)

    await full_message_send(
        context,
        phrases.CREW_DAVY_BACK_FIGHT_REQUEST_NUMBER_OF_PARTICIPANTS,
        update=update,
        keyboard=numeric_keyboard,
        inbound_keyboard=inbound_keyboard,
    )


async def request_confirmation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
    opponent_crew: Crew,
    user: User,
) -> None:
    """
    Request confirmation to initiate the DBF
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param opponent_crew: The opponent crew
    :param user: The user
    :return: None
    """

    inline_keyboard: list[list[Keyboard]] = [
        get_yes_no_keyboard(
            screen=inbound_keyboard.screen,
            inbound_keyboard=inbound_keyboard,
            no_is_back_button=True,
            add_inbound_key_info=True,
        )
    ]

    user.private_screen_stay = True  # Stay on the same screen, so to request number again
    await full_message_send(
        context,
        phrases.CREW_DAVY_BACK_FIGHT_REQUEST_CONFIRMATION.format(
            opponent_crew.get_name_escaped(),
            inbound_keyboard.get(ReservedKeyboardKeys.NUMBER),
            convert_minutes_to_duration(Env.DAVY_BACK_FIGHT_REQUEST_EXPIRATION_TIME.get_int()),
        ),
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
        excluded_keys_from_back_button=[ReservedKeyboardKeys.NUMBER],
        user=user,
    )


async def send_request_to_captain(
    context: ContextTypes.DEFAULT_TYPE,
    challenger_crew: Crew,
    opponent_crew: Crew,
    participants_count: int,
) -> None:
    """
    Send the request to the captain
    :param context: The context object
    :param challenger_crew: The challenger crew
    :param opponent_crew: The opponent crew
    :param participants_count: The number of participants
    :return: None
    """

    # Create DBF
    davy_back_fight: DavyBackFight = DavyBackFight()
    davy_back_fight.challenger_crew = challenger_crew
    davy_back_fight.opponent_crew = opponent_crew
    davy_back_fight.participants_count = participants_count
    davy_back_fight.save()

    ot_text_for_captain = phrases.CREW_DAVY_BACK_FIGHT_CAPTAIN_REQUEST.format(
        challenger_crew.get_name_with_deeplink(),
        participants_count,
        convert_minutes_to_duration(Env.DAVY_BACK_FIGHT_REQUEST_EXPIRATION_TIME.get_int()),
    )

    inline_keyboard: list[list[Keyboard]] = [
        get_yes_no_keyboard(
            screen=Screen.PVT_CREW_DAVY_BACK_FIGHT_REQUEST_RECEIVED,
            yes_text=phrases.KEYBOARD_OPTION_ACCEPT,
            no_text=phrases.KEYBOARD_OPTION_REJECT,
            primary_key=davy_back_fight.id,
        )
    ]

    captain: User = opponent_crew.get_captain()

    try:
        await full_message_send(
            context,
            ot_text_for_captain,
            chat_id=captain.tg_user_id,
            keyboard=inline_keyboard,
        )
    except TelegramError:
        davy_back_fight.delete_instance()
        raise PrivateChatException(text=phrases.CREW_SEARCH_JOIN_CAPTAIN_ERROR)
