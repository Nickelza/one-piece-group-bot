from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.chat.common.screens.screen_crew_join import validate
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import add_member, get_crew
from src.service.message_service import (
    mention_markdown_user,
    get_yes_no_keyboard,
    full_media_send,
)


class CrewReservedKeys(StrEnum):
    """
    The reserved keys for the Crew join screen
    """

    CREW_ID = "a"
    REQUESTING_USER_ID = "b"
    CAPTAIN_USER_ID = "c"


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    inbound_keyboard: Keyboard,
    target_user: User,
) -> None:
    """
    Manage the Crew join screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :param target_user: The target user in case of a reply
    :return: None
    """

    crew: Crew = get_crew(
        user=target_user,
        inbound_keyboard=inbound_keyboard,
        crew_id_key=CrewReservedKeys.CREW_ID,
    )

    # Request to join a Crew
    if inbound_keyboard is None:
        await send_request(update, context, user, crew)
        return

    await keyboard_interaction(update, context, crew, inbound_keyboard)


async def send_request(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, crew: Crew
) -> None:
    """
    Send request to join a Crew
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param crew: The crew object
    :return: None
    """

    validate(user, crew, specific_user_error=True)

    # Get captain and first mate
    captain: User = crew.get_captain()
    first_mate: User = crew.get_first_mate()

    caption = phrases.CREW_JOIN_REQUEST_CAPTION.format(
        mention_markdown_user(user),
        captain.get_mention_url(),
        (first_mate.get_mention_url() if first_mate is not None else ""),
    )

    # Keyboard
    extra_keys = {CrewReservedKeys.REQUESTING_USER_ID: user.id}
    inline_keyboard: list[list[Keyboard]] = [
        get_yes_no_keyboard(
            screen=Screen.GRP_CREW_JOIN,
            yes_text=phrases.KEYBOARD_OPTION_ACCEPT,
            no_text=phrases.KEYBOARD_OPTION_REJECT,
            primary_key=crew.id,
            extra_keys=extra_keys,
            authorized_users=[captain, first_mate],
        )
    ]

    # Get SavedMedia
    await full_media_send(
        context,
        saved_media_name=SavedMediaName.CREW_JOIN,
        update=update,
        caption=caption,
        keyboard=inline_keyboard,
        add_delete_button=True,
    )


async def keyboard_interaction(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    crew: Crew,
    inbound_keyboard: Keyboard,
) -> None:
    """
    Keyboard interaction
    :param update: The update object
    :param context: The context object
    :param crew: The crew object
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    requesting_user: User = User.get(inbound_keyboard.info[CrewReservedKeys.REQUESTING_USER_ID])

    # Captain clicked on reject button
    if not inbound_keyboard.info[ReservedKeyboardKeys.CONFIRM]:
        ot_text = phrases.CREW_JOIN_REQUEST_REJECTED.format(
            requesting_user.tg_user_id, crew.get_name_escaped()
        )
        await full_media_send(
            context,
            caption=ot_text,
            update=update,
            add_delete_button=True,
            authorized_users=[requesting_user],
            edit_only_caption_and_keyboard=True,
        )
        return

    validate(requesting_user, crew, specific_crew_error=True)

    # Add requesting user to crew
    await add_member(requesting_user, crew)

    # Accepted message
    ot_text = phrases.CREW_JOIN_REQUEST_ACCEPTED.format(
        mention_markdown_user(requesting_user), crew.get_name_escaped()
    )
    await full_media_send(
        context,
        caption=ot_text,
        update=update,
        add_delete_button=True,
        authorized_users=[requesting_user],
        edit_only_caption_and_keyboard=True,
    )
