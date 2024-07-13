from telegram import Update
from telegram.ext import ContextTypes

from src.chat.group.screens.screen_doc_q_game import manage as private_manage
from src.model.User import User
from src.model.pojo.Keyboard import Keyboard


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, inbound_keyboard: Keyboard
) -> None:
    """
    Manage the fight request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    return await private_manage(update, context, user, inbound_keyboard)
