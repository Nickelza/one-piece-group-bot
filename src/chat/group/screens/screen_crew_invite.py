from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.chat.group.screens.screen_crew_join import CrewReservedKeys, get_crew, validate
from src.model.Crew import Crew
from src.model.SavedMedia import SavedMedia
from src.model.User import User
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.Screen import Screen
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import add_member
from src.service.message_service import mention_markdown_user, get_yes_no_keyboard, \
    full_media_send, full_message_or_media_send_or_edit, escape_valid_markdown_chars


def manage(update: Update, context: CallbackContext, user: User, inbound_keyboard: Keyboard, target_user: User) -> None:
    """
    Manage the Crew invite screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :param target_user: The target user in case of a reply
    :return: None
    """

    try:
        crew: Crew = get_crew(user, inbound_keyboard)

        # Invite to a Crew
        if inbound_keyboard is None:
            send_request(update, context, user, target_user, crew)
            return

        keyboard_interaction(update, context, user, crew, inbound_keyboard)
    except CrewValidationException as cve:
        full_message_or_media_send_or_edit(context, cve.message, update=update, add_delete_button=True)


def send_request(update: Update, context: CallbackContext, captain: User, target_user: User, crew: Crew) -> None:
    """
    Send request to invite a user to a Crew
    :param update: The update object
    :param context: The context object
    :param captain: The captain issuing the invite
    :param target_user: The user being invited
    :param crew: The crew object
    :return: None
    """

    validate(target_user, crew, specific_crew_error=True)

    caption = phrases.CREW_INVITE_REQUEST_CAPTION.format(mention_markdown_user(captain),
                                                         mention_markdown_user(target_user))

    # Keyboard
    extra_keys = [{CrewReservedKeys.CAPTAIN_USER_ID: captain.id}]
    inline_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(target_user, screen=Screen.GRP_CREW_INVITE,
                                                                 yes_text=phrases.KEYBOARD_OPTION_ACCEPT,
                                                                 no_text=phrases.KEYBOARD_OPTION_REJECT,
                                                                 primary_key=crew.id, extra_keys=extra_keys)]

    # Get SavedMedia
    invite_to_crew_media: SavedMedia = SavedMedia.logical_get(SavedMediaName.INVITE_TO_CREW)
    full_media_send(context, invite_to_crew_media, update=update, caption=caption, keyboard=inline_keyboard,
                    add_delete_button=True)


def keyboard_interaction(update: Update, context: CallbackContext, invited_user: User, crew: Crew,
                         inbound_keyboard: Keyboard) -> None:
    """
    Keyboard interaction
    :param update: The update object
    :param context: The context object
    :param invited_user: The invited user
    :param crew: The crew object
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    captain: User = User.get(inbound_keyboard.info[CrewReservedKeys.CAPTAIN_USER_ID])

    # User clicked on reject button
    if not inbound_keyboard.info[CrewReservedKeys.ACCEPT]:
        ot_text = phrases.CREW_INVITE_REQUEST_REJECTED.format(escape_valid_markdown_chars(crew.name),
                                                              mention_markdown_user(invited_user))
        full_media_send(context, caption=ot_text, update=update, add_delete_button=True,
                        authorized_users=[captain.tg_user_id, invited_user.tg_user_id],
                        edit_only_caption_and_keyboard=True)
        return

    validate(invited_user, crew, specific_user_error=True)

    # Add invited user to crew
    add_member(invited_user, crew)

    # Accepted message
    ot_text = phrases.CREW_INVITE_REQUEST_ACCEPTED.format(mention_markdown_user(invited_user),
                                                          escape_valid_markdown_chars(crew.name))
    full_media_send(context, caption=ot_text, update=update, add_delete_button=True,
                    authorized_users=[captain.tg_user_id, invited_user.tg_user_id],
                    edit_only_caption_and_keyboard=True)
