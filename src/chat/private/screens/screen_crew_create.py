import datetime
from enum import IntEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
import src.model.enums.crew.CrewRole as CrewRole
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CustomException import CrewValidationException
from src.model.error.PrivateChatError import PrivateChatError, PrivateChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import (
    add_or_remove_bounty,
    validate_amount,
    get_amount_from_string,
    get_duration_to_next_bounty_reset,
)
from src.service.message_service import (
    full_message_send,
    escape_valid_markdown_chars,
    get_create_or_edit_status,
)


class Step(IntEnum):
    REQUEST_NAME = 0
    END = 1
    REQUEST_DESCRIPTION = 2
    SAVE_DESCRIPTION = 3
    REQUEST_REQUIRED_BOUNTY = 4
    SAVE_REQUIRED_BOUNTY = 5


REQUIRES_TEXT = [Step.END, Step.SAVE_DESCRIPTION, Step.SAVE_REQUIRED_BOUNTY]


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the crew create screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    should_ignore_input, should_create_item, should_validate_input = get_create_or_edit_status(
        user, inbound_keyboard
    )

    if not should_ignore_input:
        # Validate that the user can create a crew
        if should_create_item:
            if not await validate(update, context, inbound_keyboard, user):
                return
            crew = Crew()
        else:
            crew = Crew.get(user.private_screen_in_edit_id)

        if user.private_screen_step is None:
            user.private_screen_step = Step.REQUEST_NAME

        step = Step(user.private_screen_step)
        try:
            # Step requires a text input
            if step in REQUIRES_TEXT and inbound_keyboard is None:
                if update.effective_message.text is None:
                    raise CrewValidationException(phrases.STEP_REQUIRES_TEXT)

            match step:
                case Step.REQUEST_NAME:  # Request crew name
                    ot_text = phrases.CREW_CREATE_REQUEST_NAME

                case Step.END:  # End
                    # Error raised if invalid
                    validate_crew_name(update.effective_message.text)

                    crew_name = update.effective_message.text
                    # Save crew
                    crew.name = crew_name

                    # Add user to crew
                    if should_create_item:
                        crew.save()
                        # Remove price from user bounty
                        await add_or_remove_bounty(
                            user, Env.CREW_CREATE_PRICE.get_int(), add=False
                        )

                        # Add user to Crew as captain
                        user.crew = crew
                        user.crew_role = CrewRole.CrewRole.CAPTAIN
                        user.crew_join_date = datetime.datetime.now()

                        # Creation success message
                        ot_text = phrases.CREW_CREATE_SUCCESS.format(
                            escape_valid_markdown_chars(crew_name)
                        )

                    else:  # Edit mode
                        # Edit success message
                        ot_text = phrases.CREW_EDIT_NAME_SUCCESS.format(
                            escape_valid_markdown_chars(crew_name)
                        )

                case Step.REQUEST_DESCRIPTION:  # Request crew description
                    ot_text = phrases.CREW_EDIT_REQUEST_DESCRIPTION

                case Step.SAVE_DESCRIPTION:  # Save crew description
                    if (
                        inbound_keyboard is not None
                        and ReservedKeyboardKeys.RESET in inbound_keyboard.info
                    ):
                        crew.description = None
                    else:
                        # Error raised if invalid
                        validate_crew_description(update.effective_message.text)

                        crew.description = update.effective_message.text
                    ot_text = phrases.CREW_EDIT_DESCRIPTION_SUCCESS

                case Step.REQUEST_REQUIRED_BOUNTY:  # Request crew required bounty
                    ot_text = phrases.CREW_EDIT_REQUEST_REQUIRED_BOUNTY

                case Step.SAVE_REQUIRED_BOUNTY:  # Save crew required bounty
                    if (
                        inbound_keyboard is not None
                        and ReservedKeyboardKeys.RESET in inbound_keyboard.info
                    ):
                        crew.required_bounty = 0
                    else:
                        # Error raised if invalid
                        await validate_crew_minimum_required_bounty(
                            update, context, user, update.effective_message.text
                        )

                        crew.required_bounty = get_amount_from_string(
                            update.effective_message.text, user
                        )
                    ot_text = phrases.CREW_EDIT_REQUIRED_BOUNTY_SUCCESS

                case _:
                    raise PrivateChatException(PrivateChatError.UNKNOWN_EXTRA_STEP)

            # Input provided, save crew and reset private screen
            if step in REQUIRES_TEXT:
                crew.save()
                user.reset_private_screen()
            else:
                user.private_screen_force_go_back = True

            if user.private_screen_step is not None:
                user.private_screen_step += 1

        except CrewValidationException as e:
            if e.message is None:
                return

            ot_text = str(e)

        inline_keyboard = []

        # In case of description and required bounty, show reset button
        if (
            step in [Step.REQUEST_DESCRIPTION, Step.REQUEST_REQUIRED_BOUNTY]
            and inbound_keyboard is not None
        ):
            inline_keyboard.append([
                Keyboard(
                    phrases.KEY_RESET,
                    screen=Screen.PVT_CREW_CREATE_OR_EDIT,
                    info={
                        ReservedKeyboardKeys.RESET: True,
                        ReservedKeyboardKeys.SCREEN_STEP: user.private_screen_step,
                    },
                )
            ])

        # Send message
        await full_message_send(
            context,
            str(ot_text),
            update=update,
            inbound_keyboard=inbound_keyboard,
            previous_screens=user.get_private_screen_list(),
            keyboard=inline_keyboard,
        )


async def validate(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> bool:
    """
    Validate the crew create screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    try:
        # User already in a crew
        if user.is_crew_member():
            raise CrewValidationException(phrases.CREW_USER_ALREADY_IN_CREW)

        # User cannot create a crew
        if not user.can_create_crew:
            ot_text = phrases.CREW_CANNOT_CREATE_CREW.format(get_duration_to_next_bounty_reset())

            raise CrewValidationException(ot_text)

        # User does not have enough bounty
        if user.bounty < Env.CREW_CREATE_PRICE.get_int():
            raise CrewValidationException(phrases.CREW_CREATE_USER_NOT_ENOUGH_BOUNTY)

    except CrewValidationException as e:
        # Show alert if callback else send a message
        await full_message_send(
            context,
            str(e),
            update=update,
            answer_callback=True,
            show_alert=True,
            inbound_keyboard=inbound_keyboard,
        )
        return False

    return True


def validate_crew_name(crew_name: str) -> None:
    """
    Validate the crew name
    :param crew_name: The crew name
    :return: Raise an exception if invalid
    """

    # Crew name already exists, case-insensitive
    if Crew.get_by_name_if_active(crew_name) is not None:
        raise CrewValidationException(phrases.CREW_CREATE_NAME_ALREADY_EXISTS)

    # Name is too long
    if len(crew_name) > Env.CREW_NAME_MAX_LENGTH.get_int():
        raise CrewValidationException(phrases.CREW_CREATE_NAME_TOO_LONG)


def validate_crew_description(crew_description: str) -> None:
    """
    Validate the crew description
    :param crew_description: The crew description
    :return: Raise an exception if invalid
    """

    # Description is too long
    if len(crew_description) > Env.CREW_DESCRIPTION_MAX_LENGTH.get_int():
        raise CrewValidationException(phrases.CREW_EDIT_DESCRIPTION_TOO_LONG)


async def validate_crew_minimum_required_bounty(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, text: str
) -> None:
    """
    Validate the crew required bounty
    :param update: The update
    :param context: The context
    :param user: The user
    :param text: The text
    :return: Raise an exception if invalid
    """

    if not await validate_amount(
        update,
        context,
        user,
        text,
        0,
        should_validate_user_has_amount=False,
    ):
        raise CrewValidationException()
