import logging
from enum import IntEnum, StrEnum

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import constants as c
import resources.Environment as Env
import resources.phrases as phrases
from src.chat.private.screens.screen_crew_davy_back_fight_request_received import accept
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
from src.service.message_service import full_message_send, get_yes_no_keyboard, get_deeplink


class StepEdit(IntEnum):
    PARTICIPANTS = 1
    DURATION = 2
    PENALTY = 3


class ScreenReservedKeys(StrEnum):
    PARTICIPANTS = "c"
    DURATION = "d"
    PENALTY = "e"


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

    # Add edit keys to keyboard if not already there
    max_participants = DavyBackFight.get_max_participants(challenger_crew, opponent_crew)
    if not inbound_keyboard.has_key(ScreenReservedKeys.PARTICIPANTS):
        inbound_keyboard.info[ScreenReservedKeys.PARTICIPANTS] = max_participants
    # Cap max participants, in case it was already in memory from another Crew DBF request screen.
    # Bonus point, this also prevents the user from sending a request with more participants than
    # the crew can handle in case someone leaves the Crew meanwhile
    # (even though it's validated again at acceptance).
    else:
        inbound_keyboard.info[ScreenReservedKeys.PARTICIPANTS] = min(
            inbound_keyboard.get(ScreenReservedKeys.PARTICIPANTS),
            max_participants,
        )

    if not inbound_keyboard.has_key(ScreenReservedKeys.DURATION):
        inbound_keyboard.info[ScreenReservedKeys.DURATION] = (
            Env.DAVY_BACK_FIGHT_DEFAULT_DURATION.get_int()
        )
    if not inbound_keyboard.has_key(ScreenReservedKeys.PENALTY):
        inbound_keyboard.info[ScreenReservedKeys.PENALTY] = (
            Env.DAVY_BACK_FIGHT_MAX_LOSE_PENALTY_DURATION.get_int()
        )

    if not await validate(update, context, inbound_keyboard, challenger_crew, opponent_crew):
        return

    # Edit item
    if inbound_keyboard.has_key(ReservedKeyboardKeys.SCREEN_STEP_NO_INPUT):
        await edit_options(update, context, inbound_keyboard, challenger_crew, opponent_crew, user)
        return

    # Request confirmation
    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        await request_confirmation(update, context, inbound_keyboard, opponent_crew, user)
        return

    # Sending the join request to the crew captain
    await send_request_to_captain(
        context,
        challenger_crew,
        opponent_crew,
        inbound_keyboard,
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
            challenger_crew.get_member_count() < Env.DAVY_BACK_FIGHT_MIN_PARTICIPANTS.get_int()
            or opponent_crew.get_member_count() < Env.DAVY_BACK_FIGHT_MIN_PARTICIPANTS.get_int()
        ):
            raise CrewValidationException(
                phrases.CREW_DAVY_BACK_FIGHT_REQUEST_ERROR_MINIMUM_PARTICIPANTS.format(
                    Env.DAVY_BACK_FIGHT_MIN_PARTICIPANTS.get_int()
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

        # Opponent Crew does not allow Davy Back Fight requests
        if not opponent_crew.allow_davy_back_fight_request:
            raise CrewValidationException(
                phrases.CREW_DAVY_BACK_FIGHT_REQUEST_ERROR_OPPONENT_NOT_ALLOWING
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


async def edit_options(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
    challenger_crew: Crew,
    opponent_crew: Crew,
    user: User,
) -> None:
    """
    Edit the Davy Back Fight options
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param challenger_crew: The crew
    :param opponent_crew: The opponent crew
    :param user: The user
    :return: None
    """

    step: StepEdit = StepEdit(inbound_keyboard.get_int(ReservedKeyboardKeys.SCREEN_STEP_NO_INPUT))
    match step:
        case StepEdit.PARTICIPANTS:
            text = phrases.CREW_DAVY_BACK_FIGHT_REQUEST_EDIT_PARTICIPANTS
            key = ScreenReservedKeys.PARTICIPANTS
            minimum = Env.DAVY_BACK_FIGHT_MIN_PARTICIPANTS.get_int()
            maximum = DavyBackFight.get_max_participants(challenger_crew, opponent_crew)
        case StepEdit.DURATION:
            text = phrases.CREW_DAVY_BACK_FIGHT_REQUEST_EDIT_DURATION
            key = ScreenReservedKeys.DURATION
            minimum = Env.DAVY_BACK_FIGHT_MIN_DURATION.get_int()
            maximum = Env.DAVY_BACK_FIGHT_MAX_DURATION.get_int()
        case StepEdit.PENALTY:
            text = phrases.CREW_DAVY_BACK_FIGHT_REQUEST_EDIT_PENALTY
            key = ScreenReservedKeys.PENALTY
            minimum = Env.DAVY_BACK_FIGHT_MIN_LOSE_PENALTY_DURATION.get_int()
            maximum = Env.DAVY_BACK_FIGHT_MAX_LOSE_PENALTY_DURATION.get_int()

        case _:
            raise ValueError()

    # Create numeric keyboard with all possible values
    numeric_keyboard: list[list[Keyboard]] = []
    line_keyboard: list[Keyboard] = []
    for i in range(minimum, maximum + 1):
        line_keyboard.append(
            Keyboard(
                str(i),
                info={key: i},
                inbound_info=inbound_keyboard.info,
                exclude_key_from_inbound_info=[ReservedKeyboardKeys.SCREEN_STEP_NO_INPUT],
            )
        )
        if len(line_keyboard) == c.STANDARD_LIST_KEYBOARD_ROW_SIZE:
            numeric_keyboard.append(line_keyboard)
            line_keyboard = []

    if len(line_keyboard) > 0:
        numeric_keyboard.append(line_keyboard)

    user.private_screen_stay = True
    await full_message_send(
        context,
        text=text,
        update=update,
        keyboard=numeric_keyboard,
        inbound_keyboard=inbound_keyboard,
        user=user,
        excluded_keys_from_back_button=[ReservedKeyboardKeys.SCREEN_STEP_NO_INPUT],
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
        [
            Keyboard(
                phrases.PVT_KEY_CREW_DAVY_BACK_FIGHT_EDIT_PARTICIPANTS,
                screen=inbound_keyboard.screen,
                info={ReservedKeyboardKeys.SCREEN_STEP_NO_INPUT: StepEdit.PARTICIPANTS},
                inbound_info=inbound_keyboard.info,
            )
        ],
        [
            Keyboard(
                phrases.PVT_KEY_CREW_DAVY_BACK_FIGHT_EDIT_DURATION,
                screen=inbound_keyboard.screen,
                info={ReservedKeyboardKeys.SCREEN_STEP_NO_INPUT: StepEdit.DURATION},
                inbound_info=inbound_keyboard.info,
            )
        ],
        [
            Keyboard(
                phrases.PVT_KEY_CREW_DAVY_BACK_FIGHT_EDIT_PENALTY,
                screen=inbound_keyboard.screen,
                info={ReservedKeyboardKeys.SCREEN_STEP_NO_INPUT: StepEdit.PENALTY},
                inbound_info=inbound_keyboard.info,
            )
        ],
        get_yes_no_keyboard(
            screen=inbound_keyboard.screen,
            inbound_keyboard=inbound_keyboard,
            no_is_back_button=True,
            add_inbound_key_info=True,
            yes_text=phrases.KEYBOARD_OPTION_SEND_REQUEST,
            no_text=phrases.KEYBOARD_OPTION_CANCEL,
        ),
    ]

    ot_text = phrases.CREW_DAVY_BACK_FIGHT_REQUEST.format(
        inbound_keyboard.get(ScreenReservedKeys.PARTICIPANTS),
        inbound_keyboard.get(ScreenReservedKeys.DURATION),
        inbound_keyboard.get(ScreenReservedKeys.PENALTY),
        opponent_crew.get_name_escaped(),
    )

    if opponent_crew.auto_accept_davy_back_fight:
        ot_text += phrases.CREW_DAVY_BACK_FIGHT_REQUEST_AUTO_ACCEPT

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
        user=user,
    )


async def send_request_to_captain(
    context: ContextTypes.DEFAULT_TYPE,
    challenger_crew: Crew,
    opponent_crew: Crew,
    inbound_keyboard: Keyboard,
) -> None:
    """
    Send the request to the captain
    :param context: The context object
    :param challenger_crew: The challenger crew
    :param opponent_crew: The opponent crew
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    # Create DBF
    davy_back_fight: DavyBackFight = DavyBackFight()
    davy_back_fight.challenger_crew = challenger_crew
    davy_back_fight.opponent_crew = opponent_crew
    davy_back_fight.participants_count = inbound_keyboard.get(ScreenReservedKeys.PARTICIPANTS)
    davy_back_fight.duration_hours = inbound_keyboard.get(ScreenReservedKeys.DURATION)
    davy_back_fight.penalty_days = inbound_keyboard.get(ScreenReservedKeys.PENALTY)
    davy_back_fight.save()

    captain: User = opponent_crew.get_captain()

    # Auto accept
    if (
        opponent_crew.auto_accept_davy_back_fight
        and davy_back_fight.duration_hours >= Env.DAVY_BACK_FIGHT_DEFAULT_DURATION.get_int()
    ):
        davy_back_fight.is_auto_accepted = True
        davy_back_fight.save()

        ot_text_for_captain = phrases.CREW_DAVY_BACK_FIGHT_CAPTAIN_REQUEST_AUTO_ACCEPT.format(
            challenger_crew.get_name_with_deeplink(add_level=True),
            davy_back_fight.participants_count,
            davy_back_fight.duration_hours,
            davy_back_fight.penalty_days,
            get_deeplink(screen=Screen.PVT_CREW_MODIFY, previous_screens=[Screen.PVT_CREW]),
        )

        # Manage DBF button
        inline_keyboard = [[
            Keyboard(
                phrases.KEY_MANAGE,
                screen=Screen.PVT_CREW_DAVY_BACK_FIGHT_DETAIL,
                inbound_info={
                    ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: davy_back_fight.id,
                    ReservedKeyboardKeys.DIRECT_ITEM: False,
                },
            )
        ]]

        try:
            await full_message_send(
                context,
                ot_text_for_captain,
                chat_id=captain.tg_user_id,
                keyboard=inline_keyboard,
            )
        except TelegramError as te:
            davy_back_fight.delete_instance()
            logging.exception(te)
            raise PrivateChatException(text=phrases.CREW_SEARCH_JOIN_CAPTAIN_ERROR)

        await accept(context, davy_back_fight)
        return

    # Manual accept
    ot_text_for_captain = phrases.CREW_DAVY_BACK_FIGHT_CAPTAIN_REQUEST.format(
        challenger_crew.get_name_with_deeplink(add_level=True),
        davy_back_fight.participants_count,
        davy_back_fight.duration_hours,
        davy_back_fight.penalty_days,
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

    try:
        await full_message_send(
            context,
            ot_text_for_captain,
            chat_id=captain.tg_user_id,
            keyboard=inline_keyboard,
        )
    except TelegramError as te:
        davy_back_fight.delete_instance()
        logging.exception(te)
        raise PrivateChatException(text=phrases.CREW_SEARCH_JOIN_CAPTAIN_ERROR)
