from strenum import StrEnum
from telegram import Update
from telegram.ext import CallbackContext

import resources.Environment as Env
import resources.phrases as phrases
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import remove_member as remove_member_from_crew, get_crew
from src.service.cron_service import get_remaining_time_from_next_cron
from src.service.message_service import full_message_send, get_yes_no_keyboard


class CrewLeaveReservedKeys(StrEnum):
    """
    The reserved keys for the Crew leave screen
    """
    CREW_ID = 'a'


def manage(update: Update, context: CallbackContext, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the Crew leave screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    try:
        get_crew(user=user)
    except CrewValidationException as cve:
        full_message_send(context, cve.message, update=update, inbound_keyboard=inbound_keyboard)
        return

    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        # Send leave confirmation request
        ot_text = phrases.CREW_LEAVE_CONFIRMATION.format(
            get_remaining_time_from_next_cron(Env.CRON_SEND_LEADERBOARD.get()))
        inline_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(user, screen=Screen.PVT_CREW_LEAVE,
                                                                     inbound_keyboard=inbound_keyboard,
                                                                     no_is_back_button=True)]

        full_message_send(context, ot_text, update=update, keyboard=inline_keyboard, inbound_keyboard=inbound_keyboard)
        return

    # Leave crew
    remove_member_from_crew(user, context=context, send_notification_to_captain=True)

    # Send success message
    ot_text = phrases.CREW_LEAVE_SUCCESS
    full_message_send(context, ot_text, update=update, inbound_keyboard=inbound_keyboard)

