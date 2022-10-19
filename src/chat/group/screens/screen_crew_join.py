from strenum import StrEnum
from telegram import Update
from telegram.ext import CallbackContext

import resources.Environment as Env
import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.SavedMedia import SavedMedia
from src.model.User import User
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.Screen import Screen
from src.model.error.CustomException import CrewValidationException, CrewJoinValidationCrewException, \
    CrewJoinValidationUserException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import add_member, get_crew
from src.service.cron_service import get_remaining_time_from_next_cron
from src.service.message_service import mention_markdown_user, get_yes_no_keyboard, \
    full_media_send, full_message_or_media_send_or_edit, escape_valid_markdown_chars


class CrewReservedKeys(StrEnum):
    """
    The reserved keys for the Crew join screen
    """
    CREW_ID = 'a'
    ACCEPT = 'b'
    REQUESTING_USER_ID = 'c'
    CAPTAIN_USER_ID = 'd'


def manage(update: Update, context: CallbackContext, user: User, inbound_keyboard: Keyboard, target_user: User) -> None:
    """
    Manage the Crew join screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :param target_user: The target user in case of a reply
    :return: None
    """

    try:
        crew: Crew = get_crew(user=target_user, inbound_keyboard=inbound_keyboard, crew_id_key=CrewReservedKeys.CREW_ID)

        # Request to join a Crew
        if inbound_keyboard is None:
            send_request(update, context, user, crew)
            return

        keyboard_interaction(update, context, user, crew, inbound_keyboard)
    except CrewValidationException as cve:
        full_message_or_media_send_or_edit(context, cve.message, update=update, add_delete_button=True)


def validate(user: User, crew: Crew, specific_user_error: bool = False, specific_crew_error: bool = False) -> None:
    """
    Validate the crew join request
    :param user: The user object
    :param crew: The crew object
    :param specific_user_error: If True, raise a specific error message for the user
    :param specific_crew_error: If True, raise a specific error message for the crew
    :return: Raise an exception if the request is not valid
    """
    try:
        # User already in a Crew
        if user.is_crew_member():
            raise CrewJoinValidationUserException(phrases.CREW_USER_ALREADY_IN_CREW if specific_user_error else None)

        # User cannot join a Crew
        if not user.can_join_crew:
            raise CrewJoinValidationUserException(phrases.CREW_USER_CANNOT_JOIN_CREW_UNTIL_RESET.format(
                get_remaining_time_from_next_cron(Env.CRON_SEND_LEADERBOARD.get())) if specific_user_error else None)

        # Target crew has reached the maximum number of members
        if crew.is_full():
            raise CrewJoinValidationCrewException(
                phrases.CREW_JOIN_REQUEST_CREW_FULL if specific_crew_error else None)

    except CrewJoinValidationUserException as e:
        raise CrewValidationException(
            e.message if e.message is not None else phrases.CREW_JOIN_REQUEST_CREW_CANNOT_ACCEPT_USER)
    except CrewJoinValidationCrewException as e:
        raise CrewValidationException(
            e.message if e.message is not None else phrases.CREW_JOIN_REQUEST_USER_CANNOT_JOIN_CREW)


def send_request(update: Update, context: CallbackContext, user: User, crew: Crew) -> None:
    """
    Send request to join a Crew
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param crew: The crew object
    :return: None
    """

    validate(user, crew, specific_user_error=True)

    # Get captain
    captain: User = crew.get_captain()

    caption = phrases.CREW_JOIN_REQUEST_CAPTION.format(mention_markdown_user(user), captain.tg_user_id)

    # Keyboard
    extra_keys = [{CrewReservedKeys.REQUESTING_USER_ID: user.id}]
    inline_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(captain, screen=Screen.GRP_CREW_JOIN,
                                                                 yes_text=phrases.KEYBOARD_OPTION_ACCEPT,
                                                                 no_text=phrases.KEYBOARD_OPTION_REJECT,
                                                                 primary_key=crew.id, extra_keys=extra_keys)]

    # Get SavedMedia
    join_crew_media: SavedMedia = SavedMedia.logical_get(SavedMediaName.JOIN_CREW)
    full_media_send(context, join_crew_media, update=update, caption=caption, keyboard=inline_keyboard,
                    add_delete_button=True)


def keyboard_interaction(update: Update, context: CallbackContext, captain: User, crew: Crew, inbound_keyboard: Keyboard
                         ) -> None:
    """
    Keyboard interaction
    :param update: The update object
    :param context: The context object
    :param captain: The captain
    :param crew: The crew object
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    requesting_user: User = User.get(inbound_keyboard.info[CrewReservedKeys.REQUESTING_USER_ID])

    # Captain clicked on reject button
    if not inbound_keyboard.info[CrewReservedKeys.ACCEPT]:
        ot_text = phrases.CREW_JOIN_REQUEST_REJECTED.format(requesting_user.tg_user_id,
                                                            escape_valid_markdown_chars(crew.name))
        full_media_send(context, caption=ot_text, update=update, add_delete_button=True,
                        authorized_users=[captain.tg_user_id, requesting_user.tg_user_id],
                        edit_only_caption_and_keyboard=True)
        return

    validate(requesting_user, crew, specific_crew_error=True)

    # Add requesting user to crew
    add_member(requesting_user, crew)

    # Accepted message
    ot_text = phrases.CREW_JOIN_REQUEST_ACCEPTED.format(mention_markdown_user(requesting_user),
                                                        escape_valid_markdown_chars(crew.name))
    full_media_send(context, caption=ot_text, update=update, add_delete_button=True,
                    authorized_users=[captain.tg_user_id, requesting_user.tg_user_id],
                    edit_only_caption_and_keyboard=True)
