from strenum import StrEnum
from telegram import Update
from telegram.ext import CallbackContext

import resources.Environment as Env
import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.Notification import CrewLeaveNotification
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import remove_member as remove_member_from_crew
from src.service.cron_service import get_remaining_time_from_next_cron
from src.service.message_service import full_message_send
from src.service.message_service import get_yes_no_keyboard
from src.service.notification_service import send_notification


class CrewLeaveReservedKeys(StrEnum):
    """
    The reserved keys for the Crew join screen
    """
    CREW_ID = 'a'
    ACCEPT = 'b'


def manage(update: Update, context: CallbackContext, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the Crew join screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    if CrewLeaveReservedKeys.ACCEPT not in inbound_keyboard.info:
        # Send leave confirmation request
        ot_text = phrases.CREW_LEAVE_CONFIRMATION.format(
            get_remaining_time_from_next_cron(Env.CRON_SEND_LEADERBOARD.get()))
        inline_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(user, screen=Screen.PVT_CREW_LEAVE,
                                                                     no_screen=Screen.PVT_CREW)]

        full_message_send(context, ot_text, update=update, keyboard=inline_keyboard, inbound_keyboard=inbound_keyboard)
        return

    crew: Crew = user.crew

    # Leave crew
    remove_member_from_crew(user)

    # Send success message
    ot_text = phrases.CREW_LEAVE_SUCCESS
    full_message_send(context, ot_text, update=update, inbound_keyboard=inbound_keyboard)

    # Send notification to captain
    send_notification(context, crew.get_captain(), CrewLeaveNotification(user))
