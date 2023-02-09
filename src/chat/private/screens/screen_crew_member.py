from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import constants as c
import resources.phrases as phrases
from src.model.User import User
from src.model.enums.Screen import Screen
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew
from src.service.message_service import full_message_send


class CrewMemberReservedKeys(StrEnum):
    """
    The reserved keys for the Crew disband screen
    """
    MEMBER_ID = 'a'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the Crew member screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    # Get member
    member: User = User.get_by_id(inbound_keyboard.info[CrewMemberReservedKeys.MEMBER_ID])

    try:
        get_crew(user=member, validate_against_crew=user.crew)
    except CrewValidationException as cve:
        await full_message_send(context, cve.message, update=update, inbound_keyboard=inbound_keyboard)
        return

    # Get crew member text
    ot_text = phrases.CREW_MEMBER.format(member.get_markdown_mention(), member.get_bounty_formatted(),
                                         member.crew_join_date.strftime(c.STANDARD_DATE_FORMAT),
                                         (phrases.TEXT_YES if member.has_crew_mvp_bonus() else phrases.TEXT_NO))

    inline_keyboard: list[list[Keyboard]] = []
    # Show remove button if user is captain and member is not captain
    if user.is_crew_captain() and user != member:
        inline_keyboard.append([Keyboard(phrases.PVT_KEY_CREW_MEMBER_REMOVE, screen=Screen.PVT_CREW_MEMBER_REMOVE,
                                         info={CrewMemberReservedKeys.MEMBER_ID: member.id},
                                         inbound_info=inbound_keyboard.info)])

    await full_message_send(context, ot_text, update=update, keyboard=inline_keyboard,
                            inbound_keyboard=inbound_keyboard)
