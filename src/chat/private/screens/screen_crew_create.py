import datetime
from enum import IntEnum

from telegram import Update
from telegram.ext import CallbackContext

import resources.Environment as Env
import resources.phrases as phrases
import src.model.enums.CrewRole as CrewRole
import src.model.enums.LeaderboardRank as LeaderboardRank
from src.model.Crew import Crew
from src.model.User import User
from src.model.error.CustomException import CrewValidationException
from src.model.error.PrivateChatError import PrivateChatError, PrivateChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_next_bounty_reset_time
from src.service.cron_service import get_remaining_time
from src.service.leaderboard_service import get_leaderboard_user
from src.service.message_service import full_message_send, escape_valid_markdown_chars, get_create_or_edit_status


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

    should_ignore_input, should_create_item, should_validate_input = get_create_or_edit_status(user, inbound_keyboard)

    if not should_ignore_input:
        # Validate that the user can create a crew
        if should_create_item:
            if not validate(update, context, inbound_keyboard, user):
                return
            crew = Crew()
        else:
            crew = Crew.get(user.private_screen_in_edit_id)

        if user.private_screen_step is None:
            user.private_screen_step = Step.REQUEST_NAME

        try:
            match Step(user.private_screen_step):
                case Step.REQUEST_NAME:  # Request crew name
                    ot_text = phrases.CREW_CREATE_REQUEST_NAME

                case Step.END:  # End
                    try:
                        # Error raised if invalid
                        validate_crew_name(update.effective_message.text)
                    except TypeError:
                        raise CrewValidationException(phrases.STEP_REQUIRES_TEXT)

                    crew_name = update.effective_message.text

                    # Save crew
                    crew.name = crew_name
                    crew.save()

                    # Add user to crew
                    if should_create_item:
                        # Add user to Crew as captain
                        user.crew = crew
                        user.crew_role = CrewRole.CrewRole.CAPTAIN
                        user.crew_join_date = datetime.datetime.now()

                        # Creation success message
                        ot_text = phrases.CREW_CREATE_SUCCESS.format(escape_valid_markdown_chars(crew_name))
                    else:  # Edit mode
                        # Edit success message
                        ot_text = phrases.CREW_NAME_EDIT_SUCCESS.format(escape_valid_markdown_chars(crew_name))

                    # Reset user private screen
                    user.reset_private_screen()

                case _:
                    raise PrivateChatException(PrivateChatError.UNKNOWN_EXTRA_STEP)

            if user.private_screen_step is not None:
                user.private_screen_step += 1

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
        if user.is_crew_member():
            raise CrewValidationException(phrases.CREW_USER_ALREADY_IN_CREW)

        # User cannot create a crew
        if not user.can_create_crew:
            ot_text = phrases.CREW_CANNOT_CREATE_CREW.format(get_remaining_time(get_next_bounty_reset_time()))
            raise CrewValidationException(ot_text)

        # User has not appeared in the latest required leaderboards
        required_rank = LeaderboardRank.get_rank_by_index(Env.CREW_CREATE_MIN_LATEST_LEADERBOARD_RANK.get_int())
        for i in range(Env.CREW_CREATE_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int()):
            leaderboard_rank: LeaderboardRank.LeaderboardRank = LeaderboardRank.get_rank_by_leaderboard_user(
                get_leaderboard_user(user, index=i))
            if not leaderboard_rank.is_equal_or_higher(required_rank):
                raise CrewValidationException(phrases.CREW_USER_NOT_IN_LATEST_LEADERBOARD_REQUIRED_APPEARANCES)

    except CrewValidationException as e:
        # Show alert if callback else send a message
        full_message_send(context, str(e), update=update, inbound_keyboard=inbound_keyboard, answer_callback=True,
                          show_alert=True)
        return False

    return True


def validate_crew_name(crew_name: str) -> None:
    """
    Validate the crew name
    :param crew_name: The crew name
    :return: True if valid, False otherwise
    """

    # Crew name already exists, case-insensitive
    if Crew.get_by_name(crew_name) is not None:
        raise CrewValidationException(phrases.CREW_CREATE_NAME_ALREADY_EXISTS)

    # Name is too long
    if len(crew_name) > Env.CREW_NAME_MAX_LENGTH.get_int():
        raise CrewValidationException(phrases.CREW_CREATE_NAME_TOO_LONG)
