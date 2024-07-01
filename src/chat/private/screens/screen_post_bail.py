from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.ImpelDownLog import ImpelDownLog
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.ChatWarning import ChatWarning
from src.model.error.CustomException import (
    ImpelDownValidationException,
    UnauthorizedToViewItemException,
)
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

    # Get prisoner
    prisoner: User = User.get_by_id(
        inbound_keyboard.info[ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY]
    )

    if not await validate(update, context, user, prisoner):
        return

    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        # Send post bail confirmation request
        target_mention = (
            phrases.TEXT_YOURSELF if prisoner == user else mention_markdown_user(prisoner)
        )
        ot_text = phrases.POST_BAIL_CONFIRMATION_REQUEST.format(
            target_mention, get_belly_formatted(prisoner.get_current_bail())
        )
        inline_keyboard: list[list[Keyboard]] = [
            get_yes_no_keyboard(
                user,
                screen=Screen.PVT_POST_BAIL,
                primary_key=prisoner.id,
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

    impel_down_log: ImpelDownLog = prisoner.get_current_impel_down_log()
    await post_bail(context, update, impel_down_log, user)

    # Send success message
    await full_message_send(
        context,
        phrases.CREW_POST_BAIL_SUCCESS,
        update=update,
        inbound_keyboard=inbound_keyboard,
    )


async def validate(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, prisoner: User
) -> bool:
    """
    Validate the user
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param prisoner: The prisoner object
    :return: True if the validation is successful, False otherwise
    """

    try:
        # If prisoner is different from user, they must be in same Crew
        if prisoner != user:
            try:
                get_crew(user=prisoner, validate_against_crew=user.crew)
            except ChatWarning:
                raise UnauthorizedToViewItemException

        # Prisoner has no temporary sentence
        if not prisoner.is_arrested_temporary():
            raise ImpelDownValidationException(phrases.POST_BAIL_MEMBER_NOT_ARRESTED_TEMPORARY)

        # User does not have enough bounty
        bail = prisoner.get_current_bail()
        if bail > user.bounty:
            raise ImpelDownValidationException(
                phrases.POST_BAIL_NOT_ENOUGH_BOUNTY.format(
                    get_belly_formatted(bail), user.get_bounty_formatted()
                )
            )
    except ImpelDownValidationException as e:
        await full_message_send(context, e.message, update=update, show_alert=True)
        return False

    return True
