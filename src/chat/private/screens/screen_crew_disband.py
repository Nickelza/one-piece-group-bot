from strenum import StrEnum
from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.Notification import CrewDisbandNotification
from src.model.enums.Screen import Screen
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_next_bounty_reset_time
from src.service.crew_service import remove_member as remove_member_from_crew, get_crew
from src.service.cron_service import get_remaining_time
from src.service.message_service import full_message_send
from src.service.message_service import get_yes_no_keyboard
from src.service.notification_service import send_notification


class CrewDisbandReservedKeys(StrEnum):
    """
    The reserved keys for the Crew disband screen
    """
    CREW_ID = 'a'
    CONFIRM = 'b'


def manage(update: Update, context: CallbackContext, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the Crew disband screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    try:
        crew: Crew = get_crew(user=user)
    except CrewValidationException as cve:
        full_message_send(context, cve.message, update=update, inbound_keyboard=inbound_keyboard)
        return

    if CrewDisbandReservedKeys.CONFIRM not in inbound_keyboard.info:
        # Send disband confirmation request
        ot_text = phrases.CREW_DISBAND_CONFIRMATION.format(get_remaining_time(get_next_bounty_reset_time()))
        inline_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(user, screen=Screen.PVT_CREW_DISBAND,
                                                                     no_screen=Screen.PVT_CREW)]

        full_message_send(context, ot_text, update=update, keyboard=inline_keyboard, inbound_keyboard=inbound_keyboard)
        return

    crew_members: list[User] = crew.get_members()

    for member in crew_members:
        is_captain = (member.id == user.id)

        if is_captain:
            user.can_create_crew = False
            remove_member_from_crew(user)  # Else user will not be updated
        else:
            remove_member_from_crew(member)
            send_notification(context, member, CrewDisbandNotification())

    crew.is_active = False
    crew.save()

    # Send success message
    ot_text = phrases.CREW_DISBAND_SUCCESS
    full_message_send(context, ot_text, update=update, inbound_keyboard=inbound_keyboard)
