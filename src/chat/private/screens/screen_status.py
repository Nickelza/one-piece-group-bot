from telegram import Update
from telegram.ext import CallbackContext

from src.chat.group.screens.screen_status import manage as group_manage_status
from src.model.User import User
from src.model.enums.Command import Command
from src.model.pojo.Keyboard import Keyboard


def manage(update: Update, context: CallbackContext, command: Command, user: User, inbound_keyboard: Keyboard) -> None:
    """
    Manage the start screen
    :param update: The update
    :param context: The context
    :param command: The command
    :param user: The user
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    group_manage_status(update, context, command, user, inbound_keyboard)
