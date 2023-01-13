from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Manage the start screen
    :param update: The update
    :param context: The context
    :return: None
    """

    # noinspection PyListCreation
    # Cleaner to have each button on a new line
    outbound_keyboard: list[list[Keyboard]] = [[]]

    # Status button
    outbound_keyboard.append([Keyboard(phrases.PVT_KEY_STATUS, screen=Screen.PVT_USER_STATUS,
                                       previous_screen_list=[Screen.PVT_START])])

    # Crew button
    outbound_keyboard.append([Keyboard(phrases.PVT_KEY_CREW, screen=Screen.PVT_CREW,
                                       previous_screen_list=[Screen.PVT_START])])

    # Logs
    outbound_keyboard.append([Keyboard(phrases.PVT_KEY_LOGS, screen=Screen.PVT_LOGS,
                                       previous_screen_list=[Screen.PVT_START])])

    # Settings button
    outbound_keyboard.append([Keyboard(phrases.PVT_KEY_SETTINGS, screen=Screen.PVT_SETTINGS,
                                       previous_screen_list=[Screen.PVT_START])])

    await full_message_send(context, phrases.PVT_TXT_START, update, keyboard=outbound_keyboard)
