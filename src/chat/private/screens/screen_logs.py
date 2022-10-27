from strenum import StrEnum
from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.enums.Log import LOG_TYPE_BUTTON_TEXTS
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


class LogReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    TYPE = 'a'


def manage(update: Update, context: CallbackContext, inbound_keyboard: Keyboard) -> None:
    """
    Manage the logs screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    # View all logs type
    inline_keyboard: list[list[Keyboard]] = []
    logs_sorted = dict(sorted(LOG_TYPE_BUTTON_TEXTS.items(), key=lambda x: x[1]))
    for log_type, button_text in logs_sorted.items():
        inline_keyboard.append([Keyboard(button_text, screen=Screen.PVT_LOGS_TYPE,
                                         info={LogReservedKeys.TYPE: log_type})])

    full_message_send(context, phrases.PVT_TXT_LOGS, update=update, keyboard=inline_keyboard,
                      inbound_keyboard=inbound_keyboard)
