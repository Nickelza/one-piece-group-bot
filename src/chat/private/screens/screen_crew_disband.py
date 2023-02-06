from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_next_bounty_reset_time
from src.service.crew_service import get_crew, disband_crew
from src.service.cron_service import get_remaining_time
from src.service.message_service import full_message_send
from src.service.message_service import get_yes_no_keyboard


class CrewDisbandReservedKeys(StrEnum):
    """
    The reserved keys for the Crew disband screen
    """
    CREW_ID = 'a'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the Crew disband screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    try:
        get_crew(user=user)
    except CrewValidationException as cve:
        await full_message_send(context, cve.message, update=update, inbound_keyboard=inbound_keyboard)
        return

    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        # Send disband confirmation request
        ot_text = phrases.CREW_DISBAND_CONFIRMATION.format(get_remaining_time(get_next_bounty_reset_time()))
        inline_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(user, screen=Screen.PVT_CREW_DISBAND,
                                                                     inbound_keyboard=inbound_keyboard,
                                                                     no_is_back_button=True)]

        await full_message_send(context, ot_text, update=update, keyboard=inline_keyboard,
                                inbound_keyboard=inbound_keyboard)
        return

    await disband_crew(context, user)

    # Send success message
    ot_text = phrases.CREW_DISBAND_SUCCESS
    await full_message_send(context, ot_text, update=update, inbound_keyboard=inbound_keyboard)
