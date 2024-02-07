from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
from resources import phrases
from src.chat.private.screens.screen_crew_davy_back_fight_request import validate
from src.model.Crew import Crew
from src.model.DavyBackFight import DavyBackFight
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.Notification import (
    CrewDavyBackFightRequestAcceptedNotification,
    CrewDavyBackFightRequestRejectedNotification,
)
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.error.CustomException import CrewValidationException
from src.model.error.PrivateChatError import PrivateChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew
from src.service.date_service import (
    get_datetime_in_future_minutes,
    get_datetime_in_future_hours,
)
from src.service.davy_back_fight_service import set_default_participants
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

    davy_back_fight: DavyBackFight = DavyBackFight.get_by_id(
        inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY)
    )

    try:
        crew: Crew = get_crew(user=user, validate_against_crew=davy_back_fight.opponent_crew)
    except CrewValidationException as cve:
        await send_outcome_notification(context, davy_back_fight, False)
        await full_message_send(
            context, cve.message, update=update, inbound_keyboard=inbound_keyboard
        )
        return

    challenger_crew: Crew = davy_back_fight.challenger_crew

    # Captain rejected
    if not inbound_keyboard.info[ReservedKeyboardKeys.CONFIRM]:
        await send_outcome_notification(context, davy_back_fight, False)
        ot_text = phrases.CREW_DAVY_BACK_FIGHT_CAPTAIN_REJECTED.format(
            challenger_crew.get_name_with_deeplink()
        )
        await full_message_send(context, ot_text, update=update)
        return

    if not await validate(
        update, context, inbound_keyboard, challenger_crew, crew, davy_back_fight=davy_back_fight
    ):
        await send_outcome_notification(context, davy_back_fight, False)
        return

    # Accept request
    await accept(context, davy_back_fight)

    # Accepted message
    ot_text = phrases.CREW_DAVY_BACK_FIGHT_CAPTAIN_ACCEPTED.format(
        challenger_crew.get_name_with_deeplink()
    )

    # Manage DBF button
    # TODO: Add this button

    await full_message_send(context, ot_text, update=update)


async def accept(context: ContextTypes.DEFAULT_TYPE, davy_back_fight: DavyBackFight) -> None:
    """
    Accept the Davy Back Fight request

    :param context: The context object
    :param davy_back_fight: The davy back fight object
    :return: None
    """

    try:
        davy_back_fight.status = GameStatus.COUNTDOWN_TO_START
        set_default_participants(davy_back_fight.challenger_crew, davy_back_fight)
        set_default_participants(davy_back_fight.opponent_crew, davy_back_fight)
        davy_back_fight.start_date = get_datetime_in_future_minutes(
            Env.CREW_DAVY_BACK_FIGHT_START_WAIT_TIME.get_int()
        )
        davy_back_fight.end_date = get_datetime_in_future_hours(
            Env.CREW_DAVY_BACK_FIGHT_DURATION.get_int(), start_time=davy_back_fight.start_date
        )
        davy_back_fight.save()

        await send_outcome_notification(context, davy_back_fight, True)
    except CrewValidationException as e:
        await send_outcome_notification(context, davy_back_fight, False)
        davy_back_fight.delete_instance()

        raise PrivateChatException(text=e.message)


async def send_outcome_notification(
    context: ContextTypes.DEFAULT_TYPE, davy_back_fight: DavyBackFight, is_accepted: bool
) -> None:
    """
    Send the outcome notification to the captain

    :param context: The context object
    :param davy_back_fight: The davy back fight object
    :param is_accepted: Whether the request was accepted
    :return: None
    """

    challenger_crew: Crew = davy_back_fight.challenger_crew
    if is_accepted:
        return await send_notification(
            context,
            challenger_crew.get_captain(),
            CrewDavyBackFightRequestAcceptedNotification(challenger_crew),
        )

    davy_back_fight.status = GameStatus.FORCED_END
    davy_back_fight.save()

    return await send_notification(
        context,
        challenger_crew.get_captain(),
        CrewDavyBackFightRequestRejectedNotification(challenger_crew),
    )
