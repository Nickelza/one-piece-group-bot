from strenum import StrEnum
from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.enums.Notification import NOTIFICATION_CATEGORY_DESCRIPTIONS
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


class NotificationReservedKeys(StrEnum):
    CATEGORY = 'a'


def manage(update: Update, context: CallbackContext, inbound_keyboard: Keyboard) -> None:
    """
    Manage the settings screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    # View all categories
    inline_keyboard: list[list[Keyboard]] = []
    notifications_sorted = dict(sorted(NOTIFICATION_CATEGORY_DESCRIPTIONS.items(), key=lambda x: x[1]))
    for category, description in notifications_sorted.items():
        inline_keyboard.append([Keyboard(description, screen=Screen.PVT_SETTINGS_NOTIFICATIONS_TYPE,
                                         info={NotificationReservedKeys.CATEGORY: category})])

    full_message_send(context, phrases.PVT_TXT_SETTINGS_NOTIFICATIONS, update=update, keyboard=inline_keyboard,
                      inbound_keyboard=inbound_keyboard)
