from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.enums.Notification import get_notifications_by_category, NotificationCategory
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


class NotificationTypeReservedKeys(StrEnum):
    CATEGORY = 'a'
    TYPE = 'b'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard) -> None:
    """
    Manage the settings screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    # View all notification in the category
    inline_keyboard: list[list[Keyboard]] = []
    category = NotificationCategory(inbound_keyboard.info[NotificationTypeReservedKeys.CATEGORY])
    for notification in get_notifications_by_category(category):
        inline_keyboard.append([Keyboard(notification.button_text, screen=Screen.PVT_SETTINGS_NOTIFICATIONS_TYPE_EDIT,
                                         info={NotificationTypeReservedKeys.TYPE: notification.type},
                                         inbound_info=inbound_keyboard.info)])

    await full_message_send(context, phrases.PVT_TXT_SETTINGS_NOTIFICATIONS_TYPE, update=update,
                            keyboard=inline_keyboard, inbound_keyboard=inbound_keyboard,
                            excluded_keys_from_back_button=[NotificationTypeReservedKeys.CATEGORY])
