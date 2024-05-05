from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard
) -> None:
    """
    Manage the settings screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    # Notifications
    inline_keyboard: list[list[Keyboard]] = [
        [
            Keyboard(
                phrases.PVT_KEY_SETTINGS_NOTIFICATIONS, screen=Screen.PVT_SETTINGS_NOTIFICATIONS
            )
        ],
        [Keyboard(phrases.PVT_KEY_SETTINGS_TIMEZONE, screen=Screen.PVT_SETTINGS_TIMEZONE)],
    ]

    await full_message_send(
        context,
        phrases.TXT_SETTINGS,
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )
