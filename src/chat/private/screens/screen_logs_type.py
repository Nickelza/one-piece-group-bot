from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.User import User
from src.model.enums.Log import Log, LogType, get_log_by_type, LOG_TYPE_DETAIL_TEXT_FILL_IN
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.english_phrase_service import determine_article
from src.service.list_service import get_items_text_keyboard
from src.service.message_service import full_message_send
from src.service.user_service import user_is_boss


class LogTypeReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    TYPE = 'a'
    ITEM_ID = 'b'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the log type screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    log: Log = get_log_by_type(LogType(inbound_keyboard.info[LogTypeReservedKeys.TYPE]))
    if await validate(update, context, log, user):
        log.user = user
        items_text, items_keyboard = get_items_text_keyboard(inbound_keyboard, log, LogTypeReservedKeys.ITEM_ID,
                                                             Screen.PVT_LOGS_TYPE_DETAIL)

        log_fill_in_text = LOG_TYPE_DETAIL_TEXT_FILL_IN[log.type]
        ot_text = phrases.LIST_OVERVIEW.format(determine_article(log_fill_in_text), log_fill_in_text, items_text)

        await full_message_send(context, ot_text, update=update, keyboard=items_keyboard,
                                inbound_keyboard=inbound_keyboard,
                                excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE])


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE, log: Log, user: User) -> bool:
    """
    Validate the log type screen

    :param context: The context
    :param update: The update
    :param log: The log
    :param user: The user
    :return: True if the validation is successful, False otherwise
    """

    if log.only_by_boss and not await user_is_boss(user):
        await full_message_send(context, phrases.COMMAND_ONLY_BY_BOSS_ERROR, update=update)
        return False

    return True
