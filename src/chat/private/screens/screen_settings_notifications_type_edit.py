from strenum import StrEnum
from telegram import Update
from telegram.ext import CallbackContext

from src.model.DisabledNotification import DisabledNotification
from src.model.User import User
from src.model.enums.Notification import get_notification_by_type, NotificationType, Notification
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send
from src.service.notification_service import is_enabled as is_notification_enabled
from src.service.settings_service import get_current_setting_text, get_toggle_keyboard


class NotificationTypeEditReservedKeys(StrEnum):
    CATEGORY = 'a'
    TYPE = 'b'


def manage(update: Update, context: CallbackContext, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the notification type edit screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    # Get the notification
    notification: Notification = get_notification_by_type(
        NotificationType(inbound_keyboard.info[NotificationTypeEditReservedKeys.TYPE]))

    # Toggle set
    if ReservedKeyboardKeys.TOGGLE in inbound_keyboard.info:

        # Turn on - Delete record from DisabledNotification
        if inbound_keyboard.info[ReservedKeyboardKeys.TOGGLE]:
            DisabledNotification.delete().where((DisabledNotification.user == user) &
                                                (DisabledNotification.type == notification.type)).execute()
        else:  # Turn off - Create record in DisabledNotification
            disabled_notification = DisabledNotification()
            disabled_notification.user = user
            disabled_notification.type = notification.type
            disabled_notification.save()

    # Get toggle keyboard
    enabled = is_notification_enabled(user, notification)
    inline_keyboard: list[list[Keyboard]] = [[get_toggle_keyboard(enabled, inbound_keyboard.screen, inbound_keyboard)]]

    ot_text = get_current_setting_text(enabled, notification.description)
    full_message_send(context, ot_text, update=update, keyboard=inline_keyboard, inbound_keyboard=inbound_keyboard,
                      excluded_keys_from_back_button=[NotificationTypeEditReservedKeys.TYPE])
