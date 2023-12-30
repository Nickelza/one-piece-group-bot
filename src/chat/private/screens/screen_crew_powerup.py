from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.User import User
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew, get_crew_abilities_text
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

    # Abilities button
    inline_keyboard.append(
        [Keyboard(phrases.PVT_KEY_CREW_ABILITY, screen=Screen.PVT_CREW_ABILITY)]
    )

    await full_message_send(
        context,
        phrases.CREW_POWERUP.format(crew.level, get_crew_abilities_text(crew=crew)),
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )
