from enum import IntEnum, StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.User import User
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.date_service import get_timezone_from_location, get_utc_offset
from src.service.message_service import full_message_send, escape_valid_markdown_chars


class Step(IntEnum):
    SET_TIMEZONE = 0


class TimezoneReservedKeys(StrEnum):
    """
    The reserved keys for the timezone setting screen
    """
    RESET = 'a'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the timezone setting screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    user.private_screen_step = Step.SET_TIMEZONE

    if inbound_keyboard is None:
        try:
            timezone = get_timezone_from_location(update.message.text)
        except KeyError:
            timezone = None

        if timezone is None:
            await full_message_send(context, phrases.PVT_TXT_SETTINGS_TIMEZONE_INVALID, update=update,
                                    inbound_keyboard=inbound_keyboard,
                                    previous_screens=user.get_private_screen_list()[:-1])
            return

        user.timezone = timezone
    else:
        # Reset timezone
        if TimezoneReservedKeys.RESET in inbound_keyboard.info:
            user.timezone = None

    inline_keyboard: list[list[Keyboard]] = []
    if user.timezone is not None:
        # Reset timezone key
        inline_keyboard.append([Keyboard(phrases.PVT_KEY_SETTINGS_TIMEZONE_RESET,
                                         screen=Screen.PVT_SETTINGS_TIMEZONE,
                                         info={TimezoneReservedKeys.RESET: 1})])

    await full_message_send(context, get_text(user), update=update, keyboard=inline_keyboard,
                            inbound_keyboard=inbound_keyboard, previous_screens=user.get_private_screen_list()[:-1])


def get_text(user: User) -> str:
    """
    Get the text for the timezone setting screen
    :param user: The user
    :return: The text
    """

    timezone_text = escape_valid_markdown_chars(user.timezone) if user.timezone is not None else phrases.PVT_TXT_UNKNOWN
    offset_text = get_utc_offset(user.timezone)
    return phrases.PVT_TXT_SETTINGS_TIMEZONE.format(timezone_text, offset_text)
