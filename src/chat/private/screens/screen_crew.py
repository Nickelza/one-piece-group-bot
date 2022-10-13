from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
import src.model.enums.CrewRole as CrewRole
from src.chat.private.screens.screen_crew_create import Step
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send, mention_markdown_user, escape_valid_markdown_chars


def manage(update: Update, context: CallbackContext, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the crew screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    inline_keyboard: list[list[Keyboard]] = []
    if not user.is_crew_member():
        ot_text = phrases.CREW_USER_NOT_IN_CREW

        # Create crew button
        inline_keyboard.append([Keyboard(phrases.PVT_KEY_CREW_CREATE, screen=Screen.PVT_CREW_CREATE_OR_EDIT)])
    else:
        crew: Crew = user.crew
        crew_members: list[User] = crew.get_members()

        crew_members_text = ''
        for crew_member in crew_members:
            if crew_member.crew_role is None:
                crew_members_text += phrases.CREW_OVERVIEW_MEMBER.format(mention_markdown_user(crew_member))
            else:
                crew_members_text += phrases.CREW_OVERVIEW_MEMBER_ROLE.format(
                    mention_markdown_user(crew_member),
                    CrewRole.CREW_ROLE_NAME_MAP[CrewRole.CrewRole(crew_member.crew_role)])

        ot_text = phrases.CREW_OVERVIEW.format(escape_valid_markdown_chars(crew.name), crew_members_text)

        if user.is_crew_captain():
            # Name edit button
            button_info = {ReservedKeyboardKeys.IN_EDIT_ID: crew.id,
                           ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_NAME}
            inline_keyboard.append([Keyboard(phrases.PVT_KEY_CREW_EDIT_NAME, screen=Screen.PVT_CREW_CREATE_OR_EDIT,
                                             info=button_info)])
        else:
            # Leave crew button
            inline_keyboard.append([Keyboard(phrases.PVT_KEY_CREW_LEAVE, screen=Screen.PVT_CREW_LEAVE)])

    full_message_send(context, ot_text, update=update, keyboard=inline_keyboard, inbound_keyboard=inbound_keyboard)
