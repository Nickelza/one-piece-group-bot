from telegram import Update
from telegram.ext import ContextTypes

from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import FightPlunderReservedKeys
from src.model.enums.ScoutType import ScoutType
from src.model.pojo.Keyboard import Keyboard
from src.service.fight_plunder_service import (
    group_send_scout_request,
    plunder_validate,
    plunder_send_request,
    plunder_confirm_request,
)


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    keyboard: Keyboard,
    group_chat: GroupChat,
) -> None:
    """
    Manage the plunder request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param keyboard: The keyboard object
    :param group_chat: The group chat
    :return: None
    """

    # Validate the request
    if not await plunder_validate(update, context, user, True, keyboard):
        return

    # Request to plunder
    if keyboard is None:
        # Scouting request
        await group_send_scout_request(update, context, user, ScoutType.PLUNDER)
        return

    elif not keyboard.has_key(FightPlunderReservedKeys.ITEM_ID):
        await plunder_send_request(update, context, user, keyboard, group_chat)
        return

    await plunder_confirm_request(update, context, user, keyboard, group_chat)
