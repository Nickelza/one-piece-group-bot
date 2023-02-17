from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.User import User
from src.model.enums.Log import Log, LOG_TYPE_BUTTON_TEXTS, get_log_by_type
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send
from src.service.user_service import user_is_boss


class LogReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    TYPE = 'a'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the logs screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    # View all logs type
    inline_keyboard: list[list[Keyboard]] = []
    logs_sorted = dict(sorted(LOG_TYPE_BUTTON_TEXTS.items(), key=lambda x: x[1]))
    for log_type, button_text in logs_sorted.items():
        log: Log = get_log_by_type(log_type)
        if not log.only_by_boss or user_is_boss(user):
            inline_keyboard.append([Keyboard(button_text, screen=Screen.PVT_LOGS_TYPE,
                                             info={LogReservedKeys.TYPE: log_type})])

    await full_message_send(context, phrases.PVT_TXT_LOGS, update=update, keyboard=inline_keyboard,
                            inbound_keyboard=inbound_keyboard)
