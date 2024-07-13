from telegram import Update
from telegram.ext import ContextTypes

from src.chat.group.screens.screen_daily_reward import manage as private_manage
from src.model.User import User


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User) -> None:
    """
    Manage this screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :return: None
    """

    return await private_manage(update, context, user)
