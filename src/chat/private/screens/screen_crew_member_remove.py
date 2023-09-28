from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import remove_member as remove_member_from_crew, get_crew
from src.service.date_service import get_remaining_time_from_next_cron
from src.service.message_service import full_message_send, get_yes_no_keyboard, mention_markdown_user


class CrewMemberRemoveReservedKeys(StrEnum):
    """
    The reserved keys for the Crew member remove screen
    """
    MEMBER_ID = 'a'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the Crew leave screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    # Get member
    member: User = User.get_by_id(inbound_keyboard.info[CrewMemberRemoveReservedKeys.MEMBER_ID])

    try:
        get_crew(user=member, validate_against_crew=user.crew)
    except CrewValidationException as cve:
        await full_message_send(context, cve.message, update=update, inbound_keyboard=inbound_keyboard)
        return

    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        # Send remove confirmation request
        ot_text = phrases.CREW_REMOVE_MEMBER_CONFIRMATION.format(mention_markdown_user(member),
                                                                 get_remaining_time_from_next_cron(
                                                                     Env.CRON_SEND_LEADERBOARD.get()))
        inline_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(user, screen=Screen.PVT_CREW_MEMBER_REMOVE,
                                                                     primary_key=member.id,
                                                                     inbound_keyboard=inbound_keyboard,
                                                                     no_is_back_button=True)]

        await full_message_send(context, ot_text, update=update, keyboard=inline_keyboard,
                                inbound_keyboard=inbound_keyboard)
        return

    # Remove member
    await remove_member_from_crew(member, context=context, send_notification_to_member=True,
                                  disable_crew_can_accept_new_members=True)

    # Send success message
    ot_text = phrases.CREW_REMOVE_MEMBER_SUCCESS.format(mention_markdown_user(member))
    await full_message_send(context, ot_text, update=update, inbound_keyboard=inbound_keyboard, back_screen_index=1)
