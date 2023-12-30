from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.User import User
from src.model.enums.Notification import CrewFirstMateDemotionNotification
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew
from src.service.leaderboard_service import get_remaining_time_to_next_leaderboard
from src.service.message_service import (
    full_message_send,
    get_yes_no_keyboard,
    mention_markdown_user,
)
from src.service.notification_service import send_notification


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the Crew First Mate demote screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    # Get member
    member: User = User.get_by_id(inbound_keyboard.info[ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY])

    try:
        get_crew(user=member, validate_against_crew=user.crew)

        # Member is not the First Mate
        if not member.is_crew_first_mate():
            raise CrewValidationException(phrases.CREW_DEMOTE_FROM_FIRST_MATE_IS_NOT_FIRST_MATE)

    except CrewValidationException as cve:
        await full_message_send(
            context, cve.message, update=update, inbound_keyboard=inbound_keyboard
        )
        return

    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        # Send demote from First Mate confirmation request
        ot_text = phrases.CREW_DEMOTE_FROM_FIRST_MATE_CONFIRMATION.format(
            mention_markdown_user(member), get_remaining_time_to_next_leaderboard()
        )
        inline_keyboard: list[list[Keyboard]] = [
            get_yes_no_keyboard(
                user,
                screen=inbound_keyboard.screen,
                primary_key=member.id,
                inbound_keyboard=inbound_keyboard,
                no_is_back_button=True,
            )
        ]

        await full_message_send(
            context,
            ot_text,
            update=update,
            keyboard=inline_keyboard,
            inbound_keyboard=inbound_keyboard,
        )
        return

    # Demote from First Mate
    member.crew_role = None
    member.save()

    # Send success message
    ot_text = phrases.CREW_DEMOTE_FROM_FIRST_MATE_SUCCESS.format(mention_markdown_user(member))
    await full_message_send(context, ot_text, update=update, inbound_keyboard=inbound_keyboard)

    # Send notification
    await send_notification(context, member, CrewFirstMateDemotionNotification(), update=update)
