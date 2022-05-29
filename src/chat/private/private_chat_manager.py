from telegram import Update
from telegram.ext import CallbackContext

import src.model.enums.Command as Command
from src.chat.private.screens.screen_settings import manage as manage_screen_settings
from src.chat.private.screens.screen_settings_location_update import manage as manage_screen_settings_location_update
from src.chat.private.screens.screen_start import manage as manage_screen_start
from src.chat.private.screens.screen_status import manage as manage_screen_status
from src.model.User import User
from src.model.enums.Screen import Screen
from src.model.error.PrivateChatError import PrivateChatError
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


def manage(update: Update, context: CallbackContext, command: Command.Command, user: User, keyboard: Keyboard) -> None:
    """
    Main function for the group chat manager
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command to execute
    :param user: User
    :param keyboard: Keyboard
    :return: None
    """

    dispatch_screens(update, context, command, user, keyboard)


def dispatch_screens(update: Update, context: CallbackContext, command: Command.Command, user: User,
                     keyboard: Keyboard) -> None:
    """
    Dispatches the different screens
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command to execute
    :param user: User
    :param keyboard: Keyboard
    :return: None
    """

    if command is not Command.ND:
        match command.screen:
            case Screen.PVT_START:  # Start
                manage_screen_start(update, context)

            case Screen.PVT_SETTINGS:  # Settings
                manage_screen_settings(update, context, keyboard)

            case Screen.PVT_SETTINGS_LOCATION_UPDATE:  # Settings Location Update
                manage_screen_settings_location_update(update, context, user, keyboard)

            case Screen.PVT_USER_STATUS:  # Status
                manage_screen_status(update, context, command, inbound_keyboard=keyboard)

            case _:  # Unknown screen
                if update.callback_query is not None:
                    full_message_send(context, PrivateChatError.UNRECOGNIZED_SCREEN.build(), update, new_message=True)
