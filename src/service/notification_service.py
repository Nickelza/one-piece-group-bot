from telegram.error import Unauthorized
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.chat.private.screens.screen_settings_notifications_type import NotificationTypeReservedKeys
from src.model.DisabledNotification import DisabledNotification
from src.model.User import User
from src.model.enums.Notification import Notification
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


def send_notification(context: CallbackContext, user: User, notification: Notification) -> None:
    """
    Sends a notification to the user
    :param context: The context object
    :param user: User
    :param notification: Notification
    :return: None
    """

    if is_enabled(user, notification):
        # Create Keyboard for notification management
        inline_keyboard: list[list[Keyboard]] = []
        previous_screens = [Screen.PVT_START, Screen.PVT_SETTINGS, Screen.PVT_SETTINGS_NOTIFICATIONS,
                            Screen.PVT_SETTINGS_NOTIFICATIONS_TYPE]
        button_info = {NotificationTypeReservedKeys.CATEGORY: notification.category,
                       NotificationTypeReservedKeys.TYPE: notification.type}

        inline_keyboard.append([Keyboard(phrases.PVT_KEY_MANAGE_NOTIFICATION_SETTINGS, info=button_info,
                                         screen=Screen.PVT_SETTINGS_NOTIFICATIONS_TYPE_EDIT,
                                         previous_screen_list=previous_screens)])

        try:
            full_message_send(context, notification.build(), chat_id=user.tg_user_id, keyboard=inline_keyboard,
                              disable_web_page_preview=notification.disable_web_page_preview,
                              disable_notification=notification.disable_notification)
        except Unauthorized:  # User has blocked the bot
            pass


def is_enabled(user: User, notification: Notification) -> bool:
    """
    Checks if a notification is enabled for a user
    :param user: User
    :param notification: Notification
    :return: True if the notification is enabled
    """

    return DisabledNotification.get_or_none(DisabledNotification.user == user,
                                            DisabledNotification.type == notification.type) is None
