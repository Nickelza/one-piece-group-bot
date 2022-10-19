from enum import IntEnum

import resources.phrases as phrases
import src.model.enums.Location as Location
from src.model.User import User
from src.service.message_service import mention_markdown_user


class NotificationCategory(IntEnum):
    """Enum for different categories of notifications"""

    CREW = 1
    LOCATION = 2


NOTIFICATION_CATEGORY_DESCRIPTIONS = {
    NotificationCategory.CREW: phrases.NOTIFICATION_CATEGORY_CREW,
    NotificationCategory.LOCATION: phrases.NOTIFICATION_CATEGORY_LOCATION
}


class NotificationType(IntEnum):
    """Enum for the different types of notifications."""

    CREW_LEAVE = 1
    LOCATION_UPDATE = 2
    CREW_DISBAND = 3


class Notification:
    """Class for notifications."""

    def __init__(self, category: NotificationCategory, notification_type: NotificationType, text: str, description: str,
                 button_text: str, disable_web_page_preview: bool = True):
        """
        Constructor

        :param category: Category of the notification
        :param notification_type: The type of notification
        :param text: Base text that will be sent
        :param description: Description of the notification to be provided in settings
        :param button_text: Text for the button to change the notification settings
        :param disable_web_page_preview: True if the web page preview should be disabled
        """

        self.category = category
        self.type = notification_type
        self.text = text
        self.description = description
        self.button_text = button_text
        self.disable_web_page_preview = disable_web_page_preview

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

    def build(self) -> str:
        """Builds the notification."""

        return self.text.format(mention_markdown_user(self.crew_member))


class LocationUpdateNotification(Notification):
    """Class for location update notifications."""

    def __init__(self, user: User = None, location: Location.Location = None):
        """
        :param user: User
        :param location: The new location
        """

        self.user = user
        self.location = location
        super().__init__(NotificationCategory.LOCATION, NotificationType.LOCATION_UPDATE,
                         phrases.LOCATION_UPDATE_NOTIFICATION,
                         phrases.LOCATION_UPDATE_NOTIFICATION_DESCRIPTION,
                         phrases.LOCATION_UPDATE_NOTIFICATION_KEY,
                         disable_web_page_preview=False)

    def build(self) -> str:
        """Builds the notification."""

        from src.service.message_service import get_image_preview
        from src.service.bounty_service import get_belly_formatted

        # Determine preposition to use for the location
        if 'island' in self.location.name.lower() or 'archipelago' in self.location.name.lower():
            preposition = 'on'
            if self.location.name.lower().startswith('island'):
                preposition += ' the'
        else:
            preposition = 'in'

        # Determine text suffix
        try:
            next_location = Location.get_by_level(self.location.level + 1)
            text_suffix = phrases.LOCATION_NEXT_LEVEL_REQUIREMENT.format(
                get_belly_formatted(next_location.required_bounty))
        except ValueError:
            text_suffix = phrases.LOCATION_CURRENT_LEVEL_MAX

        return self.text.format(get_image_preview(self.location.image_url),
                                mention_markdown_user(self.user),
                                preposition,
                                self.location.name,
                                text_suffix)


class CrewDisbandNotification(Notification):
    """Class for crew disband notifications."""

    def __init__(self):
        """Constructor"""

        super().__init__(NotificationCategory.CREW, NotificationType.CREW_DISBAND,
                         phrases.CREW_DISBAND_NOTIFICATION,
                         phrases.CREW_DISBAND_NOTIFICATION_DESCRIPTION,
                         phrases.CREW_DISBAND_NOTIFICATION_KEY)

    def build(self) -> str:
        """Builds the notification."""

        return self.text


NOTIFICATIONS = [CrewLeaveNotification(), LocationUpdateNotification(), CrewDisbandNotification()]


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
