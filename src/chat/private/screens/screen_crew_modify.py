from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.chat.private.screens.screen_crew_create import Step
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew
from src.service.message_service import full_message_send


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

    crew = get_crew(user=user)
    inline_keyboard: list[list[Keyboard]] = []

    # Name edit button
    button_info = {
        ReservedKeyboardKeys.IN_EDIT_ID: crew.id,
        ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_NAME,
    }
    inline_keyboard.append([
        Keyboard(
            phrases.PVT_KEY_CREW_EDIT_NAME, screen=Screen.PVT_CREW_CREATE_OR_EDIT, info=button_info
        )
    ])

    # Disband button
    inline_keyboard.append(
        [Keyboard(phrases.PVT_KEY_CREW_DISBAND, screen=Screen.PVT_CREW_DISBAND, info=button_info)]
    )

    await full_message_send(
        context,
        phrases.TEXT_WHAT_TO_MODIFY,
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )
