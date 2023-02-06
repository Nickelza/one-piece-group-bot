from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.model.User import User
from src.model.enums.Location import get_by_bounty
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import remove_member as remove_member_from_crew, get_crew
from src.service.cron_service import get_remaining_time_from_next_cron
from src.service.message_service import full_message_send, get_yes_no_keyboard, escape_valid_markdown_chars


class CrewLeaveReservedKeys(StrEnum):
    """
    The reserved keys for the Crew leave screen
    """
    CREW_ID = 'a'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
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
        await full_message_send(context, cve.message, update=update, inbound_keyboard=inbound_keyboard)
        return

    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        ot_text = phrases.CREW_LEAVE_CONFIRMATION.format(
            get_remaining_time_from_next_cron(Env.CRON_SEND_LEADERBOARD.get()))

        # Check if the new location after leaving Crew is lower than the current one
        current_location = get_by_bounty(user.get_max_bounty())
        new_location = get_by_bounty(user.bounty)
        if new_location.level < user.location_level:
            ot_text += (phrases
                        .CREW_LEAVE_CONFIRMATION_LOCATION_DOWNGRADE
                        .format(escape_valid_markdown_chars(new_location.name),
                                escape_valid_markdown_chars(current_location.name)))

        # Send leave confirmation request
        inline_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(user, screen=Screen.PVT_CREW_LEAVE,
                                                                     inbound_keyboard=inbound_keyboard,
                                                                     no_is_back_button=True)]

        await full_message_send(context, ot_text, update=update, keyboard=inline_keyboard,
                                inbound_keyboard=inbound_keyboard)
        return

    # Leave crew
    await remove_member_from_crew(user, context=context, send_notification_to_captain=True,
                                  disable_user_can_join_crew=True)

    # Send success message
    ot_text = phrases.CREW_LEAVE_SUCCESS
    await full_message_send(context, ot_text, update=update, inbound_keyboard=inbound_keyboard)
