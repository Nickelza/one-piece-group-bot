from telegram import Update
from telegram.ext import ContextTypes

from src.model.User import User
from src.model.enums.ScoutType import ScoutType
from src.model.pojo.Keyboard import Keyboard
from src.service.fight_plunder_service import (
    plunder_validate,
    private_manage,
)


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

    # Validate the request
    if not await plunder_validate(update, context, user, False, inbound_keyboard):
        return

    return await private_manage(update, context, user, inbound_keyboard, ScoutType.PLUNDER)
