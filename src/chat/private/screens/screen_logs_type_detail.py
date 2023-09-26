from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

from src.chat.private.screens.screen_logs_type import validate
from src.model.User import User
from src.model.enums.Log import Log, LogType, get_log_by_type
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


class LogTypeReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    TYPE = 'a'
    ITEM_ID = 'b'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the log type detail screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    log: Log = get_log_by_type(LogType(inbound_keyboard.get(LogTypeReservedKeys.TYPE)))

    if await validate(update, context, log, user):
        # For deep linking
        if Screen.PVT_LOGS_TYPE not in inbound_keyboard.previous_screen_list:
            # From deep linking, go back to stats
            inbound_keyboard.previous_screen_list.append(Screen.PVT_LOGS_TYPE_STATS)

        log.user = user
        log.set_object(inbound_keyboard.get_int(LogTypeReservedKeys.ITEM_ID))

        await full_message_send(context, log.get_item_detail_text(), update=update, inbound_keyboard=inbound_keyboard)
