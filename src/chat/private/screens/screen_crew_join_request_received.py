from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.group.screens.screen_crew_join import validate as validate_crew_join
from src.model.Crew import Crew
from src.model.CrewJoinRequest import CrewJoinRequest
from src.model.User import User
from src.model.enums.Notification import (
    CrewJoinRequestAcceptedNotification,
    CrewJoinRequestRejectedNotification,
)
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.enums.crew.CrewJoinRequestStatus import CrewJoinRequestStatus
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew, add_member
from src.service.message_service import full_message_send
from src.service.notification_service import send_notification


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

    join_request: CrewJoinRequest = CrewJoinRequest.get_by_id(
        inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY)
    )

    try:
        crew: Crew = get_crew(user=user, validate_against_crew=join_request.crew)
    except CrewValidationException as cve:
        await send_outcome_notification(context, join_request, False)
        await full_message_send(
            context, cve.message, update=update, inbound_keyboard=inbound_keyboard
        )
        return

    requesting_user: User = join_request.user

    # Captain rejected
    if not inbound_keyboard.info[ReservedKeyboardKeys.CONFIRM]:
        await send_outcome_notification(context, join_request, False)
        ot_text = phrases.CREW_SEARCH_JOIN_CAPTAIN_REJECTED.format(
            requesting_user.get_markdown_mention()
        )
        await full_message_send(context, ot_text, update=update)
        return

    if not await validate(update, context, inbound_keyboard, crew, requesting_user):
        await send_outcome_notification(context, join_request, False)
        return

    # Add requesting user to crew
    await accept(context, join_request)

    # Accepted message
    ot_text = phrases.CREW_SEARCH_JOIN_CAPTAIN_ACCEPTED.format(
        requesting_user.get_markdown_mention()
    )

    # View member button
    inline_keyboard: list[list[Keyboard]] = [[
        Keyboard(
            phrases.PVT_KEY_CREW_MEMBER_VIEW,
            screen=Screen.PVT_CREW_MEMBER_DETAIL,
            info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: requesting_user.id},
            previous_screen_list=[Screen.PVT_CREW, Screen.PVT_CREW_MEMBER],
        )
    ]]

    await full_message_send(context, ot_text, update=update, keyboard=inline_keyboard)


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
        validate_crew_join(user, crew, specific_crew_error=True)
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


async def accept(context: ContextTypes.DEFAULT_TYPE, join_request: CrewJoinRequest):
    """
    Accept the join request

    :param context: The context object
    :param join_request: The join request object
    :return: None
    """

    crew: Crew = join_request.crew
    user: User = join_request.user

    # Add requesting user to crew
    await add_member(user, crew)
    # Send outcome notification
    await send_outcome_notification(context, join_request, True)


async def send_outcome_notification(
    context: ContextTypes.DEFAULT_TYPE, join_request: CrewJoinRequest, is_accepted: bool
) -> None:
    """
    Send the outcome notification to the captain

    :param context: The context object
    :param join_request: The join request object
    :param is_accepted: Whether the request was accepted
    :return: None
    """

    if is_accepted:
        join_request.status = CrewJoinRequestStatus.ACCEPTED
        join_request.save()
        return await send_notification(
            context, join_request.user, CrewJoinRequestAcceptedNotification(join_request.crew)
        )

    join_request.status = CrewJoinRequestStatus.REJECTED
    join_request.save()
    return await send_notification(
        context, join_request.user, CrewJoinRequestRejectedNotification(join_request.crew)
    )
