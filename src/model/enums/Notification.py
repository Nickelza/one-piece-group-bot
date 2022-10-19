from enum import IntEnum

import resources.phrases as phrases
from src.model.User import User
from src.service.message_service import mention_markdown_user


class NotificationCategory(IntEnum):
    """Enum for different categories of notifications"""

    CREW = 1


NOTIFICATION_CATEGORY_DESCRIPTIONS = {
    NotificationCategory.CREW: phrases.NOTIFICATION_CATEGORY_CREW
}


class NotificationType(IntEnum):
    """Enum for the different types of notifications."""

    CREW_LEAVE = 1


class Notification:
    """Class for notifications."""

    def __init__(self, category: NotificationCategory, notification_type: NotificationType, text: str, description: str,
                 button_text: str):
        """
        Constructor

        :param category: Category of the notification
        :param notification_type: The type of notification
        :param text: Base text that will be sent
        :param description: Description of the notification to be provided in settings
        :param button_text: Text for the button to change the notification settings
        """

        self.category = category
        self.type = notification_type
        self.text = text
        self.description = description
        self.button_text = button_text

    def build(self):
        """Builds the notification."""

        return self.text


class CrewLeaveNotification(Notification):
    """Class for crew leave notifications."""

    def __init__(self, crew_member: User = None):
        """
        :param crew_member: Member of the crew that left
        """

        self.crew_member = crew_member
        super().__init__(NotificationCategory.CREW, NotificationType.CREW_LEAVE,
                         phrases.CREW_LEAVE_NOTIFICATION,
                         phrases.CREW_LEAVE_NOTIFICATION_DESCRIPTION,
                         phrases.CREW_LEAVE_NOTIFICATION_KEY)

    def build(self):
        """Builds the notification."""

        return self.text.format(mention_markdown_user(self.crew_member))


NOTIFICATIONS = [CrewLeaveNotification()]


def get_notifications_by_category(notification_category: NotificationCategory) -> list[Notification]:
    """
    Get all notifications by category

    :param notification_category: The category
    :return: List of notifications
    """

    return [
        notification for notification in NOTIFICATIONS if notification.category is notification_category]


def get_notification_by_type(notification_type: NotificationType) -> Notification:
    """
    Get a notification by type

    :param notification_type: The type
    :return: The notification
    """

    return next(notification for notification in NOTIFICATIONS if notification.type is notification_type)
