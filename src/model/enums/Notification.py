from datetime import datetime
from enum import IntEnum

import resources.Environment as Env
import resources.phrases as phrases
import src.model.enums.Location as Location
from src.model.DevilFruit import DevilFruit
from src.model.Game import Game
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.impel_down.ImpelDownBountyAction import ImpelDownBountyAction
from src.model.enums.impel_down.ImpelDownSentenceType import ImpelDownSentenceType
from src.model.game.GameType import GameType
from src.service.cron_service import get_remaining_time
from src.service.date_service import default_datetime_format
from src.service.message_service import get_image_preview, escape_valid_markdown_chars, mention_markdown_user


class NotificationCategory(IntEnum):
    """Enum for different categories of notifications"""

    CREW = 1
    LOCATION = 2
    GAME = 3
    IMPEL_DOWN = 4
    PREDICTION = 5
    DELETED_MESSAGE = 6
    BOUNTY_GIFT = 7
    DEVIL_FRUIT = 8


NOTIFICATION_CATEGORY_DESCRIPTIONS = {
    NotificationCategory.CREW: phrases.NOTIFICATION_CATEGORY_CREW,
    NotificationCategory.LOCATION: phrases.NOTIFICATION_CATEGORY_LOCATION,
    NotificationCategory.GAME: phrases.NOTIFICATION_CATEGORY_GAME,
    NotificationCategory.IMPEL_DOWN: phrases.NOTIFICATION_CATEGORY_IMPEL_DOWN,
    NotificationCategory.PREDICTION: phrases.NOTIFICATION_CATEGORY_PREDICTION,
    NotificationCategory.DELETED_MESSAGE: phrases.NOTIFICATION_CATEGORY_DELETED_MESSAGE,
    NotificationCategory.BOUNTY_GIFT: phrases.NOTIFICATION_CATEGORY_BOUNTY_GIFT,
    NotificationCategory.DEVIL_FRUIT: phrases.NOTIFICATION_CATEGORY_DEVIL_FRUIT
}


class NotificationType(IntEnum):
    """Enum for the different types of notifications."""

    CREW_LEAVE = 1
    LOCATION_UPDATE = 2
    CREW_DISBAND = 3
    CREW_DISBAND_WARNING = 4
    GAME_TURN = 5
    CREW_MEMBER_REMOVE = 6
    IMPEL_DOWN_RESTRICTION_PLACED = 7
    IMPEL_DOWN_RESTRICTION_REMOVED = 8
    PREDICTION_RESULT = 9
    PREDICTION_BET_INVALID = 10
    DELETED_MESSAGE_ARREST = 11
    DELETED_MESSAGE_MUTE = 12
    DELETED_MESSAGE_LOCATION = 13
    BOUNTY_GIFT_RECEIVED = 14
    DEVIL_FRUIT_AWARDED = 15
    DEVIL_FRUIT_EXPIRED = 16


class Notification:
    """Class for notifications."""

    def __init__(self, category: NotificationCategory, notification_type: NotificationType, text: str, description: str,
                 button_text: str, disable_web_page_preview: bool = True, disable_notification: bool = True):
        """
        Constructor

        :param category: Category of the notification
        :param notification_type: The type of notification
        :param text: Base text that will be sent
        :param description: Description of the notification to be provided in settings
        :param button_text: Text for the button to change the notification settings
        :param disable_web_page_preview: True if the web page preview should be disabled
        :param disable_notification: True if telegram should not notify of the message
        """

        self.category = category
        self.type = notification_type
        self.text = text
        self.description = description
        self.button_text = button_text
        self.disable_web_page_preview = disable_web_page_preview
        self.disable_notification = disable_notification

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

    def __init__(self, user: User = None, location: Location = None):
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
                                escape_valid_markdown_chars(self.location.name),
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


class CrewDisbandWarningNotification(Notification):
    """Class for crew disband warning notifications."""

    def __init__(self):
        """Constructor"""

        super().__init__(NotificationCategory.CREW, NotificationType.CREW_DISBAND_WARNING,
                         phrases.CREW_DISBAND_WARNING_NOTIFICATION,
                         phrases.CREW_DISBAND_WARNING_NOTIFICATION_DESCRIPTION,
                         phrases.CREW_DISBAND_WARNING_NOTIFICATION_KEY)

    def build(self) -> str:
        """Builds the notification."""

        return self.text.format(Env.CREW_CREATE_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int() - 1)


class GameTurnNotification(Notification):
    """Class for game turn notifications."""

    def __init__(self, game: Game = None, opponent: User = None):
        """Constructor

        :param game: The game
        :param opponent: The opponent whose turn it's not
        """

        self.game = game
        self.opponent = opponent
        super().__init__(NotificationCategory.GAME, NotificationType.GAME_TURN,
                         phrases.GAME_TURN_NOTIFICATION,
                         phrases.GAME_TURN_NOTIFICATION_DESCRIPTION,
                         phrases.GAME_TURN_NOTIFICATION_KEY,
                         disable_notification=False)

    def build(self) -> str:
        """Builds the notification."""

        from src.service.game_service import get_game_name

        return self.text.format(get_game_name(GameType(self.game.type)),
                                mention_markdown_user(self.opponent),
                                self.game.message_id)


class CrewMemberRemoveNotification(Notification):
    """Class for crew member remove notifications."""

    def __init__(self, crew_member: User = None):
        """Constructor

        :param crew_member: The crew member that was removed
        """

        self.crew_member = crew_member
        super().__init__(NotificationCategory.CREW, NotificationType.CREW_MEMBER_REMOVE,
                         phrases.CREW_MEMBER_REMOVE_NOTIFICATION,
                         phrases.CREW_MEMBER_REMOVE_NOTIFICATION_DESCRIPTION,
                         phrases.CREW_MEMBER_REMOVE_NOTIFICATION_KEY)

    def build(self) -> str:
        """Builds the notification"""

        return self.text.format(mention_markdown_user(self.crew_member))


class ImpelDownNotificationRestrictionPlaced(Notification):
    """Class for impel down restriction place notifications."""

    def __init__(self, sentence_type: ImpelDownSentenceType = None, release_date_time: datetime = None,
                 bounty_action: ImpelDownBountyAction = None, reason: str = None):
        """
        Constructor

        :param sentence_type: The sentence type
        :param release_date_time: The release date time
        :param bounty_action: The bounty action
        :param reason: The reason
        """

        self.sentence_type = sentence_type
        self.release_date_time = release_date_time
        self.bounty_action = bounty_action
        self.reason = reason

        super().__init__(NotificationCategory.IMPEL_DOWN, NotificationType.IMPEL_DOWN_RESTRICTION_PLACED,
                         phrases.IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION,
                         phrases.IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_DESCRIPTION,
                         phrases.IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_KEY)

    def build(self) -> str:
        """Builds the notification"""

        restriction_text = ''
        duration_text = ''

        # Bounty action
        if self.bounty_action is ImpelDownBountyAction.HALVE:
            restriction_text += phrases.IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_BOUNTY_HALVED
        elif self.bounty_action is ImpelDownBountyAction.ERASE:
            restriction_text += phrases.IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_BOUNTY_ERASED

        # Sentence type
        if self.sentence_type is not ImpelDownSentenceType.NONE:
            restriction_text += phrases.IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_WITH_DURATION

            duration_text = phrases.IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_DURATION.format(
                get_remaining_time(self.release_date_time) if self.sentence_type is ImpelDownSentenceType.TEMPORARY
                else phrases.IMPEL_DOWN_RESTRICTION_PLACED_NOTIFICATION_DURATION_PERMANENT)

        return self.text.format(escape_valid_markdown_chars(self.reason), restriction_text, duration_text)


class ImpelDownNotificationRestrictionRemoved(Notification):
    """Class for impel down restriction remove notifications."""

    def __init__(self):
        """Constructor"""

        super().__init__(NotificationCategory.IMPEL_DOWN, NotificationType.IMPEL_DOWN_RESTRICTION_REMOVED,
                         phrases.IMPEL_DOWN_RESTRICTION_REMOVED_NOTIFICATION,
                         phrases.IMPEL_DOWN_RESTRICTION_REMOVED_NOTIFICATION_DESCRIPTION,
                         phrases.IMPEL_DOWN_RESTRICTION_REMOVED_NOTIFICATION_KEY)


class PredictionResultNotification(Notification):
    """Class for prediction result notifications."""

    def __init__(self, prediction: Prediction = None, prediction_options: list[PredictionOption] = None,
                 correct_prediction_options: list[PredictionOption] = None, total_win: int = None):
        """
        Constructor

        :param prediction: The prediction
        :param prediction_options: The prediction options that were chosen by the user
        :param correct_prediction_options: The correct prediction options
        :param total_win: The total win
        """

        self.prediction = prediction
        self.prediction_options = prediction_options
        self.correct_prediction_options = correct_prediction_options
        self.total_win = total_win

        super().__init__(NotificationCategory.PREDICTION, NotificationType.PREDICTION_RESULT,
                         phrases.PREDICTION_RESULT_NOTIFICATION,
                         phrases.PREDICTION_RESULT_NOTIFICATION_DESCRIPTION,
                         phrases.PREDICTION_RESULT_NOTIFICATION_KEY)

    def build(self) -> str:
        """Builds the notification"""

        from src.service.bounty_service import get_belly_formatted

        # Result text
        result_text = phrases.TEXT_WON if self.total_win >= 0 else phrases.TEXT_LOST

        # User prediction options
        user_prediction_options_list = ''
        for option in self.prediction_options:
            option_emoji = Emoji.LOG_POSITIVE if option.is_correct else Emoji.LOG_NEGATIVE
            user_prediction_options_list += phrases.PREDICTION_RESULT_NOTIFICATION_OPTION.format(
                option_emoji, escape_valid_markdown_chars(option.option))
        phrase_to_use = (phrases.PREDICTION_RESULT_NOTIFICATION_YOUR_OPTION
                         if len(self.prediction_options) == 1
                         else phrases.PREDICTION_RESULT_NOTIFICATION_YOUR_OPTIONS)
        user_prediction_options_text = phrase_to_use.format(user_prediction_options_list)

        prediction_has_correct_options = len(self.correct_prediction_options) > 0
        # Correct prediction options
        prediction_has_multiple_options = len(self.correct_prediction_options) > 0 or len(self.prediction_options) > 0
        user_got_the_only_correct_option = len(self.correct_prediction_options) == 1 and len(
            [option for option in self.prediction_options if option.is_correct]) == 1

        # Show correct options list if:
        # - Prediction has at least one correct option
        # - Prediction has multiple options or didn't get the only correct option
        correct_prediction_options_text = ''
        if prediction_has_correct_options and (prediction_has_multiple_options
                                               and not user_got_the_only_correct_option):
            correct_prediction_options_list = ''
            for option in self.correct_prediction_options:
                correct_prediction_options_list += phrases.PREDICTION_RESULT_NOTIFICATION_OPTION_NO_EMOJI.format(
                    escape_valid_markdown_chars(option.option))
            correct_prediction_options_text = phrases.PREDICTION_RESULT_NOTIFICATION_CORRECT_OPTIONS.format(
                correct_prediction_options_list)

        # Wager refunded notice
        wager_refunded_text = ''
        if not prediction_has_correct_options:
            wager_refunded_text = phrases.PREDICTION_RESULT_NOTIFICATION_WAGER_REFUNDED_NO_CORRECT_OPTIONS
        elif self.prediction.refund_wager:
            # User lost more than the refundable amount
            if self.total_win < 0 and abs(self.total_win) > self.prediction.max_refund_wager:
                wager_refunded_text = phrases.PREDICTION_RESULT_NOTIFICATION_WAGER_REFUNDED_PARTIAL.format(
                    get_belly_formatted(self.prediction.max_refund_wager))
            else:
                wager_refunded_text = phrases.PREDICTION_RESULT_NOTIFICATION_WAGER_REFUNDED

        return self.text.format(result_text, get_belly_formatted(abs(self.total_win)),
                                escape_valid_markdown_chars(self.prediction.question), user_prediction_options_text,
                                correct_prediction_options_text, wager_refunded_text, self.prediction.message_id)


class PredictionBetInvalidNotification(Notification):
    """Class for invalid prediction bet notifications."""

    def __init__(self, prediction: Prediction = None, prediction_options_user: list[PredictionOptionUser] = None,
                 total_refund: int = None):
        """
        Constructor

        :param prediction: The prediction
        :param prediction_options_user: The invalid prediction options that were chosen by the user
        :param total_refund: The total refund
        """

        self.prediction = prediction
        self.prediction_options_user = prediction_options_user
        self.total_refund = total_refund

        super().__init__(NotificationCategory.PREDICTION, NotificationType.PREDICTION_BET_INVALID,
                         phrases.PREDICTION_BET_INVALID_NOTIFICATION,
                         phrases.PREDICTION_BET_INVALID_NOTIFICATION_DESCRIPTION,
                         phrases.PREDICTION_BET_INVALID_NOTIFICATION_KEY)

    def build(self) -> str:
        from src.service.bounty_service import get_belly_formatted

        if len(self.prediction_options_user) == 1:
            bet_has = phrases.PREDICTION_BET_INVALID_BET_HAS
            it_was = phrases.TEXT_IT_WAS
        else:
            bet_has = phrases.PREDICTION_BET_INVALID_BETS_HAVE
            it_was = phrases.TEXT_THEY_WERE

        invalid_prediction_options_list = ''
        for prediction_option_user in self.prediction_options_user:
            prediction_option: PredictionOption = prediction_option_user.prediction_option
            invalid_prediction_options_list += phrases.PREDICTION_BET_INVALID_NOTIFICATION_OPTION.format(
                escape_valid_markdown_chars(prediction_option.option),
                default_datetime_format(prediction_option_user.date))

        return self.text.format(bet_has, it_was, escape_valid_markdown_chars(self.prediction.question),
                                default_datetime_format(self.prediction.cut_off_date), invalid_prediction_options_list,
                                get_belly_formatted(self.total_refund), self.prediction.message_id)


class DeletedMessageArrestNotification(Notification):
    """Class for deleted messages because user is arrested notifications."""

    def __init__(self):
        """Constructor"""

        super().__init__(NotificationCategory.DELETED_MESSAGE, NotificationType.DELETED_MESSAGE_ARREST,
                         phrases.DELETED_MESSAGE_ARREST_NOTIFICATION,
                         phrases.DELETED_MESSAGE_ARREST_NOTIFICATION_DESCRIPTION,
                         phrases.DELETED_MESSAGE_ARREST_NOTIFICATION_KEY,
                         disable_notification=False)


class DeletedMessageMuteNotification(Notification):
    """Class for deleted messages because user is muted notifications."""

    def __init__(self):
        """Constructor"""

        super().__init__(NotificationCategory.DELETED_MESSAGE, NotificationType.DELETED_MESSAGE_MUTE,
                         phrases.DELETED_MESSAGE_MUTE_NOTIFICATION,
                         phrases.DELETED_MESSAGE_MUTE_NOTIFICATION_DESCRIPTION,
                         phrases.DELETED_MESSAGE_MUTE_NOTIFICATION_KEY,
                         disable_notification=False)


class DeletedMessageLocationNotification(Notification):
    """Class for deleted messages because user has not reached the required location notifications."""

    def __init__(self, user: User = None, required_location_level: int = None):
        """
        Constructor

        :param user: The user
        :param required_location_level: The required location level
        """

        self.user = user
        self.required_location_level = required_location_level

        super().__init__(NotificationCategory.DELETED_MESSAGE, NotificationType.DELETED_MESSAGE_LOCATION,
                         phrases.DELETED_MESSAGE_LOCATION_NOTIFICATION,
                         phrases.DELETED_MESSAGE_LOCATION_NOTIFICATION_DESCRIPTION,
                         phrases.DELETED_MESSAGE_LOCATION_NOTIFICATION_KEY,
                         disable_notification=False)

    def build(self) -> str:
        current_location: Location = Location.get_by_level(self.user.location_level)
        required_location: Location = Location.get_by_level(self.required_location_level)
        return self.text.format(escape_valid_markdown_chars(current_location.name),
                                escape_valid_markdown_chars(required_location.name), )


class BountyGiftReceivedNotification(Notification):
    """Class for bounty gift received notifications."""

    def __init__(self, sender: User = None, amount: int = None):
        """
        Constructor

        :param sender: The sender
        :param amount: The amount
        """

        self.sender = sender
        self.amount = amount

        super().__init__(NotificationCategory.BOUNTY_GIFT, NotificationType.BOUNTY_GIFT_RECEIVED,
                         phrases.BOUNTY_GIFT_RECEIVED_NOTIFICATION,
                         phrases.BOUNTY_GIFT_RECEIVED_NOTIFICATION_DESCRIPTION,
                         phrases.BOUNTY_GIFT_RECEIVED_NOTIFICATION_KEY)

    def build(self) -> str:
        from src.service.bounty_service import get_belly_formatted

        return self.text.format(get_belly_formatted(self.amount), self.sender.get_markdown_mention())


class DevilFruitAwardedNotification(Notification):
    """Class for Devil Fruit awarded notifications."""

    def __init__(self, devil_fruit: DevilFruit = None, reason: str = None):
        """
        Constructor

        :param devil_fruit: The Devil Fruit
        :param reason: The reason
        """

        self.devil_fruit = devil_fruit
        self.reason = reason

        super().__init__(NotificationCategory.DEVIL_FRUIT, NotificationType.DEVIL_FRUIT_AWARDED,
                         phrases.DEVIL_FRUIT_AWARDED_NOTIFICATION,
                         phrases.DEVIL_FRUIT_AWARDED_NOTIFICATION_DESCRIPTION,
                         phrases.DEVIL_FRUIT_AWARDED_NOTIFICATION_KEY)

    def build(self) -> str:
        return self.text.format(escape_valid_markdown_chars(self.devil_fruit.get_full_name()),
                                escape_valid_markdown_chars(self.reason))


class DevilFruitExpiredNotification(Notification):
    """Class for Devil Fruit expired notifications."""

    def __init__(self, devil_fruit: DevilFruit = None):
        """
        Constructor

        :param devil_fruit: The Devil Fruit
        """

        self.devil_fruit = devil_fruit

        super().__init__(NotificationCategory.DEVIL_FRUIT, NotificationType.DEVIL_FRUIT_EXPIRED,
                         phrases.DEVIL_FRUIT_EXPIRED_NOTIFICATION,
                         phrases.DEVIL_FRUIT_EXPIRED_NOTIFICATION_DESCRIPTION,
                         phrases.DEVIL_FRUIT_EXPIRED_NOTIFICATION_KEY)

    def build(self) -> str:
        return self.text.format(escape_valid_markdown_chars(self.devil_fruit.get_full_name()),
                                Env.DEVIL_FRUIT_RESPAWN_HOURS.get_int())


NOTIFICATIONS = [CrewLeaveNotification(), LocationUpdateNotification(), CrewDisbandNotification(),
                 CrewDisbandWarningNotification(), GameTurnNotification(), CrewMemberRemoveNotification(),
                 ImpelDownNotificationRestrictionPlaced(), ImpelDownNotificationRestrictionRemoved(),
                 PredictionResultNotification(), PredictionBetInvalidNotification(), DeletedMessageArrestNotification(),
                 DeletedMessageMuteNotification(), DeletedMessageLocationNotification(),
                 BountyGiftReceivedNotification(), DevilFruitAwardedNotification(), DevilFruitExpiredNotification()]


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
