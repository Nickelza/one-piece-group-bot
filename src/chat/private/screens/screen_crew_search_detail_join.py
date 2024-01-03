from datetime import datetime

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import resources.Environment as Env
from resources import phrases
from src.chat.group.screens.screen_crew_join import validate as validate_crew_join
from src.model.Crew import Crew
from src.model.CrewJoinRequest import CrewJoinRequest
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CustomException import CrewValidationException
from src.model.error.PrivateChatError import PrivateChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.date_service import (
    get_remaining_duration,
    get_datetime_in_future_hours,
    get_datetime_in_future_days,
)
from src.service.message_service import full_message_send, get_yes_no_keyboard


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

    crew: Crew = Crew.logical_get(inbound_keyboard.get(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY))

    if not await validate(update, context, inbound_keyboard, crew, user):
        return

    # Not confirmed, show the confirmation screen
    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        await request_confirmation(update, context, inbound_keyboard, crew)
        return

    # Sending the join request to the crew captain
    await send_request_to_captain(context, crew, user)

    await full_message_send(
        context,
        phrases.CREW_SEARCH_JOIN_SUCCESS.format(crew.get_name_escaped()),
        update=update,
        inbound_keyboard=inbound_keyboard,
    )


async def request_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, crew: Crew
) -> None:
    """
    Request confirmation to join crew
    :param update: The update object
    :param context: The context object
    :param inbound_keyboard: The inbound keyboard
    :param crew: The crew object
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

    await full_message_send(
        context,
        phrases.CREW_SEARCH_JOIN_CONFIRMATION_REQUEST.format(crew.get_name_escaped()),
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )


async def validate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
    crew: Crew,
    user: User,
) -> bool:
    """
    Validate the crew level up screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param crew: The crew
    :param user: The user
    :return: None
    """

    try:
        if not crew.allow_join_from_search:
            raise CrewValidationException(phrases.CREW_SEARCH_JOIN_NOT_ALLOWED)

        # User has reached maximum amount of join requests per n hours
        join_requests: list[CrewJoinRequest] = CrewJoinRequest.get_all_requests_in_cooldown_period(
            user
        )
        if len(join_requests) >= Env.CREW_JOIN_REQUESTS_PER_COOLDOWN.get_int():
            reset_time: datetime = get_datetime_in_future_hours(
                Env.CREW_JOIN_REQUEST_COOLDOWN_DURATION.get_int(), join_requests[0].date
            )
            raise CrewValidationException(
                phrases.CREW_SEARCH_JOIN_MAXIMUM_REQUESTS_PER_COOLDOWN.format(
                    get_remaining_duration(reset_time)
                )
            )

        # User has reached maximum number of join requests for same crew
        join_requests_same_crew: list[CrewJoinRequest] = (
            CrewJoinRequest.get_all_requests_in_cooldown_period_for_crew(user, crew)
        )
        if len(join_requests_same_crew) >= 1:
            reset_time: datetime = get_datetime_in_future_days(
                Env.CREW_JOIN_REQUEST_COOLDOWN_SAME_CREW_DURATION.get_int(),
                join_requests_same_crew[0].date,
            )
            raise CrewValidationException(
                phrases.CREW_SEARCH_JOIN_MAXIMUM_REQUESTS_SAME_CREW_PER_COOLDOWN.format(
                    get_remaining_duration(reset_time)
                )
            )

        validate_crew_join(user, crew, specific_user_error=True, specific_crew_error=True)

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

    return True


async def send_request_to_captain(
    context: ContextTypes.DEFAULT_TYPE,
    crew: Crew,
    user: User,
) -> None:
    """
    Send the request to the captain
    :param context: The context object
    :param crew: The crew object
    :param user: The user object
    :return: None
    """

    # Create request
    join_request: CrewJoinRequest = CrewJoinRequest()
    join_request.user = user
    join_request.crew = crew
    join_request.save()

    ot_text_for_captain = phrases.CREW_SEARCH_JOIN_CAPTAIN_REQUEST.format(
        user.get_markdown_mention(), user.get_bounty_formatted()
    )

    inline_keyboard: list[list[Keyboard]] = [
        get_yes_no_keyboard(
            screen=Screen.PVT_CREW_JOIN_REQUEST_RECEIVED,
            yes_text=phrases.KEYBOARD_OPTION_ACCEPT,
            no_text=phrases.KEYBOARD_OPTION_REJECT,
            primary_key=join_request.id,
        )
    ]

    captain: User = crew.get_captain()

    try:
        await full_message_send(
            context,
            ot_text_for_captain,
            chat_id=captain.tg_user_id,
            keyboard=inline_keyboard,
        )
    except TelegramError:
        join_request.delete_instance()
        raise PrivateChatException(text=phrases.CREW_SEARCH_JOIN_CAPTAIN_ERROR)
