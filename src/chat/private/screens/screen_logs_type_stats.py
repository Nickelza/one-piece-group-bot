from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.private.screens.screen_logs_type import validate
from src.model.User import User
from src.model.enums.Log import Log, LogType, get_log_by_type
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


class LogTypeReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    TYPE = 'a'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the log stats detail screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    log: Log = get_log_by_type(LogType(inbound_keyboard.get(LogTypeReservedKeys.TYPE)))
    log.user = user

    if await validate(update, context, log, user):
        try:
            await full_message_send(context, log.get_stats_text(), update=update, inbound_keyboard=inbound_keyboard)
        except AttributeError:
            await full_message_send(context, phrases.LOG_STATS_NOT_ENOUGH_DATA, update=update,
                                    inbound_keyboard=inbound_keyboard)
