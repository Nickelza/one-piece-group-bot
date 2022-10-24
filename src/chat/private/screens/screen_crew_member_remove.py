from strenum import StrEnum
from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import remove_member as remove_member_from_crew, get_crew
from src.service.message_service import full_message_send, get_yes_no_keyboard, mention_markdown_user


class CrewMemberRemoveReservedKeys(StrEnum):
    """
    The reserved keys for the Crew member remove screen
    """
    MEMBER_ID = 'a'


def manage(update: Update, context: CallbackContext, inbound_keyboard: Keyboard, user: User) -> None:
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
        full_message_send(context, cve.message, update=update, inbound_keyboard=inbound_keyboard)
        return

    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        # Send remove confirmation request
        ot_text = phrases.CREW_REMOVE_MEMBER_CONFIRMATION.format(mention_markdown_user(member))
        inline_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(user, screen=Screen.PVT_CREW_MEMBER_REMOVE,
                                                                     primary_key=member.id,
                                                                     inbound_keyboard=inbound_keyboard,
                                                                     no_is_back_button=True)]

        full_message_send(context, ot_text, update=update, keyboard=inline_keyboard, inbound_keyboard=inbound_keyboard)
        return

    # Remove member
    remove_member_from_crew(member, context=context, send_notification_to_member=True)

    # Send success message
    ot_text = phrases.CREW_REMOVE_MEMBER_SUCCESS.format(mention_markdown_user(member))
    full_message_send(context, ot_text, update=update, inbound_keyboard=inbound_keyboard, back_screen_index=1)
