import datetime
from enum import IntEnum

from telegram import Update
from telegram.ext import CallbackContext

import resources.Environment as Env
import resources.phrases as phrases
import src.model.enums.CrewRole as CrewRole
from src.model.Crew import Crew
from src.model.User import User
from src.model.error.CustomException import CrewValidationException
from src.model.error.PrivateChatError import PrivateChatError
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_next_bounty_reset_time
from src.service.cron_service import get_remaining_time
from src.service.leaderboard_service import get_leaderboard_user
from src.service.message_service import full_message_send, escape_valid_markdown_chars


class Step(IntEnum):
    REQUEST_NAME = 0
    END = 1


def manage(update: Update, context: CallbackContext, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the crew create screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    # Validate
    if not validate(update, context, inbound_keyboard, user):
        return

    if user.private_screen_step is None:
        user.private_screen_step = Step.REQUEST_NAME

    try:
        match Step(user.private_screen_step):
            case Step.REQUEST_NAME:  # Request crew name
                ot_text = phrases.CREW_CREATE_REQUEST_NAME

            case Step.END:  # End
                crew_name = update.effective_message.text

                # Crew name already exists, case-insensitive
                if Crew.get_by_name(crew_name) is not None:
                    raise CrewValidationException(phrases.CREW_CREATE_NAME_ALREADY_EXISTS)

                # Name is too long
                if len(crew_name) > Env.CREW_NAME_MAX_LENGTH.get_int():
                    raise CrewValidationException(phrases.CREW_CREATE_NAME_TOO_LONG)

                # Save crew
                crew = Crew()
                crew.name = crew_name
                crew.save()

                # Add user to crew
                user.crew = crew
                user.crew_role = CrewRole.CrewRole.CAPTAIN
                user.crew_join_date = datetime.datetime.now()

                ot_text = phrases.CREW_CREATE_SUCCESS.format(escape_valid_markdown_chars(crew_name))

                user.private_screen_step = None

            case _:
                raise CrewValidationException(PrivateChatError.UNKNOWN_EXTRA_STEP)

        if user.private_screen_step is not None:
            user.private_screen_step += 1

        user.save()

    except CrewValidationException as e:
        ot_text = str(e)

    # Send message
    full_message_send(context, str(ot_text), update=update, inbound_keyboard=inbound_keyboard,
                      previous_screens=user.get_private_screen_list()[:-1])


def validate(update: Update, context: CallbackContext, inbound_keyboard: Keyboard, user: User) -> bool:
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
        if user.crew is not None:
            raise CrewValidationException(phrases.CREW_USER_ALREADY_IN_CREW)

        # User cannot create a crew
        if not user.can_create_crew:
            ot_text = phrases.CREW_CANNOT_CREATE_CREW.format(get_remaining_time(get_next_bounty_reset_time()))
            raise CrewValidationException(ot_text)

        # User has not appeared in the latest required leaderboards
        for i in range(Env.CREW_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int()):
            if get_leaderboard_user(user, index=i) is None:
                raise CrewValidationException(phrases.CREW_USER_NOT_IN_LATEST_LEADERBOARD_REQUIRED_APPEARANCES)

    except CrewValidationException as e:
        # Show alert if callback else send a message
        full_message_send(context, str(e), update=update, inbound_keyboard=inbound_keyboard, answer_callback=True,
                          show_alert=True)
        return False

    return True
