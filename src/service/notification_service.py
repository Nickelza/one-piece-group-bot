import logging
import traceback

from telegram import Update, Message
from telegram.error import Forbidden
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.chat.private.screens.screen_settings_notifications_type import (
    NotificationTypeReservedKeys,
)
from src.model.DisabledNotification import DisabledNotification
from src.model.User import User
from src.model.enums.Notification import Notification
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


async def send_notification(
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    notification: Notification,
    should_forward_message: bool = False,
    update: Update = None,
) -> None:
    """
    Sends a notification to the user, fire and forget
    :param context: The context object
    :param user: User
    :param notification: Notification
    :param should_forward_message: If the message of the update should be forwarded
    :param update: The update object
    :return: None
    """

    if user is None:
        logging.error("Trying to send a notification to a None user")
        logging.error(traceback.format_stack())
        return

    if (
        should_forward_message
    ):  # Sync since it's for deleted messages, else no message is forwarded before the deletion
        await send_notification_execute(
            context, user, notification, should_forward_message, update
        )
    else:
        context.application.create_task(
            send_notification_execute(context, user, notification, should_forward_message, update)
        )


async def send_notification_execute(
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    notification: Notification,
    should_forward_message: bool = False,
    update: Update = None,
) -> None:
    """
    Sends a notification to the user
    :param context: The context object
    :param user: User
    :param notification: Notification
    :param should_forward_message: If the message of the update should be forwarded
    :param update: The update object
    :return: None
    """

    if should_forward_message and update is None:
        raise ValueError("If should_forward_message is not None, update must be not None")

    if is_enabled(user, notification):
        # Create Keyboard for notification management
        inline_keyboard: list[list[Keyboard]] = []
        previous_screens = [
            Screen.PVT_START,
            Screen.PVT_SETTINGS,
            Screen.PVT_SETTINGS_NOTIFICATIONS,
            Screen.PVT_SETTINGS_NOTIFICATIONS_TYPE,
        ]
        button_info = {
            NotificationTypeReservedKeys.CATEGORY: notification.category,
            NotificationTypeReservedKeys.TYPE: notification.type,
        }

        inline_keyboard.append(notification.get_go_to_item_keyboard())
        inline_keyboard.append([
            Keyboard(
                phrases.PVT_KEY_MANAGE_NOTIFICATION_SETTINGS,
                info=button_info,
                screen=Screen.PVT_SETTINGS_NOTIFICATIONS_TYPE_EDIT,
                previous_screen_list=previous_screens,
            )
        ])

        try:
            quote_message_id = None
            if should_forward_message:
                message: Message = await update.message.forward(
                    user.tg_user_id, disable_notification=True
                )
                quote_message_id = message.message_id

            await full_message_send(
                context,
                notification.build(),
                chat_id=user.tg_user_id,
                keyboard=inline_keyboard,
                disable_notification=notification.disable_notification,
                reply_to_message_id=quote_message_id,
                disable_web_page_preview=notification.disable_web_page_preview,
            )
        except Forbidden:  # User has blocked the bot
            pass


def is_enabled(user: User, notification: Notification) -> bool:
    """
    Checks if a notification is enabled for a user
    :param user: User
    :param notification: Notification
    :return: True if the notification is enabled
    """

    return (
        DisabledNotification.get_or_none(
            DisabledNotification.user == user, DisabledNotification.type == notification.type
        )
        is None
    )
