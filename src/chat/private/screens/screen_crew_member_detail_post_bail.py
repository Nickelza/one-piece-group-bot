from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.ImpelDownLog import ImpelDownLog
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew
from src.service.impel_down_service import post_bail
from src.service.message_service import (
    full_message_send,
    get_yes_no_keyboard,
    mention_markdown_user,
)
from src.utils.string_utils import get_belly_formatted


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage this screen
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
    except CrewValidationException as cve:
        await full_message_send(
            context, cve.message, update=update, inbound_keyboard=inbound_keyboard
        )
        return

    if not await validate(update, context, user, member):
        return

    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        # Send post bail confirmation request
        ot_text = phrases.CREW_POST_BAIL_CONFIRMATION_REQUEST.format(
            mention_markdown_user(member), get_belly_formatted(member.get_current_bail())
        )
        inline_keyboard: list[list[Keyboard]] = [
            get_yes_no_keyboard(
                user,
                screen=Screen.PVT_CREW_MEMBER_DETAIL_POST_BAIL,
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

    impel_down_log: ImpelDownLog = member.get_current_impel_down_log()
    await post_bail(context, update, impel_down_log, user)

    # Send success message
    await full_message_send(
        context,
        phrases.CREW_POST_BAIL_SUCCESS,
        update=update,
        inbound_keyboard=inbound_keyboard,
    )


async def validate(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, member: User
) -> bool:
    """
    Validate the user
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param member: The member object
    :return: True if the validation is successful, False otherwise
    """

    try:
        # Member has no temporary sentence
        if not member.is_arrested_temporary():
            raise CrewValidationException(phrases.CREW_POST_BAIL_MEMBER_NOT_ARRESTED_TEMPORARY)

        # User does not have enough bounty
        bail = member.get_current_bail()
        if bail > user.bounty:
            raise CrewValidationException(
                phrases.CREW_POST_BAIL_NOT_ENOUGH_BOUNTY.format(
                    get_belly_formatted(bail), user.get_bounty_formatted()
                )
            )

        # User can't post bail for themselves
        if user.id == member.id:
            raise CrewValidationException(phrases.CREW_POST_BAIL_CANNOT_POST_BAIL_FOR_SELF)

    except CrewValidationException as cve:
        await full_message_send(context, cve.message, update=update, show_alert=True)
        return False

    return True
