from telegram import Update
from telegram.ext import CallbackContext

import src.model.enums.Command as Command
from src.chat.private.screens.screen_start import manage as manage_screen_start
from src.model.enums.Screen import Screen
from src.model.error.PrivateChatError import PrivateChatError
from src.service.message_service import full_message_send


def manage(update: Update, context: CallbackContext, command: Command.Command) -> None:
    """
    Main function for the group chat manager
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command to execute
    :return: None
    """

    dispatch_screens(update, context, command)


def dispatch_screens(update: Update, context: CallbackContext, command: Command.Command) -> None:
    """
    Dispatches the different screens
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command to execute
    :return: None
    """

    if command is not Command.ND:
        match command.screen:
            case Screen.PVT_START:  # User status
                manage_screen_start(update, context)

            case _:  # Unknown screen
                if update.callback_query is not None:
                    full_message_send(context, PrivateChatError.UNRECOGNIZED_SCREEN.build(), update, new_message=True)
