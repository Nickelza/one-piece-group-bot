import datetime

from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.Notification import CrewCaptainPromotionNotification
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.crew.CrewRole import CrewRole
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_duration_to_next_bounty_reset
from src.service.crew_service import get_crew
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
    Manage the Crew Captain promote screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    # Get member
    member: User = User.get_by_id(inbound_keyboard.info[ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY])

    try:
        crew: Crew = get_crew(user=member, validate_against_crew=user.crew)

        # Member is not First Mate
        if not member.is_crew_first_mate():
            raise CrewValidationException(
                phrases.CREW_PROMOTE_TO_CAPTAIN_CANNOT_PROMOTE_NOT_FIRST_MATE
            )

        # Crew cannot promote Captain
        if not crew.can_promote_captain:
            raise CrewValidationException(
                phrases.CREW_PROMOTE_TO_CAPTAIN_CANNOT_PROMOTE_UNTIL_NEXT_RESET.format(
                    get_duration_to_next_bounty_reset()
                )
            )

        # Crew in a Davy Back Fight or has a Penalty
        if crew.has_active_davy_back_fight() or crew.has_penalty_davy_back_fight():
            raise CrewValidationException(phrases.CREW_PROMOTE_CANNOT_PROMOTE_DAVY_BACK_FIGHT)

    except CrewValidationException as cve:
        await full_message_send(
            context,
            cve.message,
            update=update,
            inbound_keyboard=inbound_keyboard,
            show_alert=True,
        )
        return

    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        # Send promote to Captain confirmation request
        ot_text = phrases.CREW_PROMOTE_TO_CAPTAIN_CONFIRMATION.format(
            mention_markdown_user(member)
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

    # Appoint to Captain
    crew.can_promote_captain = False

    member.crew_role = CrewRole.CAPTAIN
    user.crew_role = CrewRole.FIRST_MATE
    member.crew_promotion_date = user.crew_promotion_date = datetime.datetime.now()

    crew.save()
    member.save()
    user.save()

    # Send success message
    ot_text = phrases.CREW_PROMOTE_TO_CAPTAIN_SUCCESS.format(mention_markdown_user(member))
    await full_message_send(context, ot_text, update=update, inbound_keyboard=inbound_keyboard)

    # Send notification
    await send_notification(context, member, CrewCaptainPromotionNotification(), update=update)
