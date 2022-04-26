from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


def manage(update: Update, context: CallbackContext) -> None:
    """
    Manage the start screen
    :param update: The update
    :param context: The context
    :return: None
    """

    # Keyboard with settings option
    keyboard: Keyboard = Keyboard(phrases.PVT_KEY_SETTINGS, screen=Screen.PVT_SETTINGS,
                                  previous_screen_list=[Screen.PVT_START])
    full_message_send(context, phrases.PVT_TXT_START, update, keyboard=[[keyboard]])
