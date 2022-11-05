from strenum import StrEnum
from telegram import Update
from telegram.ext import CallbackContext

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
    ITEM_ID = 'b'


def manage(update: Update, context: CallbackContext, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the log type detail screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    log: Log = get_log_by_type(LogType(inbound_keyboard.get(LogTypeReservedKeys.TYPE)))

    if validate(update, context, log, user):
        log.user = user
        log.set_object(inbound_keyboard.get_int(LogTypeReservedKeys.ITEM_ID))

        full_message_send(context, log.get_item_detail_text(), update=update, inbound_keyboard=inbound_keyboard)
