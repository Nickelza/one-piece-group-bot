from strenum import StrEnum
from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.SavedMedia import SavedMedia
from src.model.User import User
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.Screen import Screen
from src.model.error.CustomException import CrewValidationException
from src.model.error.GroupChatError import GroupChatError, GroupChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import add_member
from src.service.message_service import mention_markdown_user, get_yes_no_keyboard, \
    full_media_send, full_message_or_media_send_or_edit, escape_valid_markdown_chars


class CrewReservedKeys(StrEnum):
    """
    The reserved keys for the Crew join screen
    """
    CREW_ID = 'a'
    ACCEPT = 'b'
    REQUESTING_USER_ID = 'c'


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
        crew: Crew = get_crew(target_user, inbound_keyboard)

        # Request to join a Crew
        if inbound_keyboard is None:
            send_request(update, context, user, crew)
            return

        keyboard_interaction(update, context, user, crew, inbound_keyboard)
    except CrewValidationException as cve:
        full_message_or_media_send_or_edit(context, cve.message, update=update, add_delete_button=True)


def get_crew(target_user: User, inbound_keyboard: Keyboard) -> Crew:
    """
    Get crew
    :param target_user: The target user
    :param inbound_keyboard: The inbound keyboard
    :return: The crew
    """

    if target_user is not None:
        return target_user.crew

    # Get crew
    crew: Crew = Crew.logical_get(inbound_keyboard.info[CrewReservedKeys.CREW_ID])

    # Crew is not found
    if crew is None:
        raise CrewValidationException(phrases.CREW_NOT_FOUND)

    return crew


def request_validation(user: User, crew: Crew) -> None:
    """
    Validate the crew join request
    :param user: The user object
    :param crew: The crew object
    :return: Raise an exception if the request is not valid
    """

    # User already in a Crew
    if user.is_crew_member():
        raise CrewValidationException(phrases.CREW_USER_ALREADY_IN_CREW)

    # Target crew has reached the maximum number of members
    if crew.is_full():
        raise CrewValidationException(phrases.CREW_JOIN_REQUEST_CREW_FULL)


def send_request(update: Update, context: CallbackContext, user: User, crew: Crew) -> None:
    """
    Send request to join a Crew
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param crew: The crew object
    :return: None
    """

    request_validation(user, crew)

    # Get SavedMedia
    join_crew_media: SavedMedia = SavedMedia.get_or_none(SavedMedia.name == SavedMediaName.JOIN_CREW)
    # SavedMedia is not found
    if join_crew_media is None:
        raise GroupChatException(GroupChatError.SAVED_MEDIA_NOT_FOUND)

    # Get captain
    captain: User = crew.get_captain()

    caption = phrases.CREW_JOIN_REQUEST_CAPTION.format(mention_markdown_user(user), captain.tg_user_id)

    # Keyboard
    extra_keys = [{CrewReservedKeys.REQUESTING_USER_ID: user.id}]
    inline_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(captain, crew.id, phrases.KEYBOARD_OPTION_ACCEPT,
                                                                 phrases.KEYBOARD_OPTION_REJECT,
                                                                 Screen.GRP_CREW_JOIN, extra_keys=extra_keys)]

    full_media_send(context, join_crew_media, update=update, caption=caption, keyboard=inline_keyboard,
                    add_delete_button=True)


def keyboard_interaction_validation(captain: User, crew: Crew, requesting_user: User, inbound_keyboard_info: dict
                                    ) -> None:
    """
    Validate the crew join request confirmation or rejection
    :param captain: The captain of the crew
    :param crew: The crew object
    :param requesting_user: The requesting user
    :param inbound_keyboard_info: The inbound keyboard info
    :return: Raise an exception if the request is not valid
    """
    # Captain is not the same
    if crew.get_captain() != captain:
        raise CrewValidationException(phrases.CREW_JOIN_REQUEST_CAPTAIN_CHANGED)

    # Request rejected, no further validation needed
    if not inbound_keyboard_info[CrewReservedKeys.ACCEPT]:
        return

    # Requesting user already in a Crew
    if requesting_user.is_crew_member():
        raise CrewValidationException(phrases.CREW_REQUESTING_USER_ALREADY_IN_CREW)

    # Crew has reached the maximum number of members
    if crew.is_full():
        raise CrewValidationException(phrases.CREW_JOIN_REQUEST_CREW_FULL)


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
    keyboard_interaction_validation(captain, crew, requesting_user, inbound_keyboard.info)

    # Captain clicked on reject button
    if not inbound_keyboard.info['b']:
        ot_text = phrases.CREW_JOIN_REQUEST_REJECTED.format(requesting_user.tg_user_id,
                                                            escape_valid_markdown_chars(crew.name))
        full_media_send(context, caption=ot_text, update=update, add_delete_button=True,
                        authorized_users=[captain.tg_user_id, requesting_user.tg_user_id],
                        edit_only_caption_and_keyboard=True)
        return

    # Add requesting user to crew
    add_member(requesting_user, crew)

    # Accepted message
    ot_text = phrases.CREW_JOIN_REQUEST_ACCEPTED.format(requesting_user.tg_user_id,
                                                        escape_valid_markdown_chars(crew.name))
    full_media_send(context, caption=ot_text, update=update, add_delete_button=True,
                    authorized_users=[captain.tg_user_id, requesting_user.tg_user_id],
                    edit_only_caption_and_keyboard=True)
