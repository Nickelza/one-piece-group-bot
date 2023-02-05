from telegram import Update
from telegram.ext import ContextTypes

import src.model.enums.Command as Command
from src.model.error.AdminChatError import AdminChatError, AdminChatException


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, command: Command.Command) -> None:
    """
    Main function for the admin chat manager
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command to execute
    :return: None
    """

    await dispatch_screens(update, context, command)


async def dispatch_screens(update: Update, context: ContextTypes.DEFAULT_TYPE, command: Command.Command) -> None:
    """
    Dispatches the different screens
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command to execute
    :return: None
    """

    if command is not Command.ND:
        match command.screen:
            case _:  # Unknown screen
                if update.callback_query is not None:
                    raise AdminChatException(AdminChatError.UNRECOGNIZED_SCREEN)
