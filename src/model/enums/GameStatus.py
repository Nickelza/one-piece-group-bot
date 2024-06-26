from enum import IntEnum

from resources import phrases
from src.model.enums.Emoji import Emoji


class GameStatus(IntEnum):
    """
    Enum for the status of a game.
    """

    ND = -1
    IN_PROGRESS = 0
    WON = 1
    LOST = 2
    DRAW = 3
    AWAITING_SELECTION = 4
    AWAITING_OPPONENT_CONFIRMATION = 5
    FORCED_END = 6
    COUNTDOWN_TO_START = 7
    WINNING = 8
    LOSING = 9

    @staticmethod
    def get_finished() -> list["GameStatus"]:
        """
        Get the finished statuses.
        :return: The finished statuses
        """
        return [GameStatus.WON, GameStatus.LOST, GameStatus.DRAW, GameStatus.FORCED_END]

    def is_finished(self) -> bool:
        """
        Check if the status is finished.
        :return: True if finished, False otherwise
        """
        return self in GameStatus.get_finished()

    def get_log_emoji(self) -> str:
        """
        Get the emoji for the log.
        :return: The emoji
        """
        if self in [GameStatus.WON, GameStatus.WINNING]:
            return Emoji.LOG_POSITIVE
        elif self in [GameStatus.LOST, GameStatus.LOSING]:
            return Emoji.LOG_NEGATIVE
        elif self == GameStatus.DRAW:
            return Emoji.LOG_DRAW
        elif self == GameStatus.FORCED_END:
            return Emoji.LOG_FORCED_END

        return Emoji.LOG_NEUTRAL

    def get_status_by_challenger(self, user_is_challenger: bool) -> "GameStatus":
        """
        Get the status by the challenger.
        :param user_is_challenger: True if user is challenger, False otherwise
        :return: The status
        """

        if user_is_challenger:
            return self
        elif self == GameStatus.WON:
            return GameStatus.LOST
        elif self == GameStatus.LOST:
            return GameStatus.WON

        return self

    def get_opposite_status(self):
        """
        Get the opposite status.
        :return: The opposite status
        """

        if self == GameStatus.WON:
            return GameStatus.LOST
        elif self == GameStatus.LOST:
            return GameStatus.WON

        raise ValueError("Status with no opposite: " + str(self))

    def no_wager_was_collected(self):
        """
        Check if no wager was collected.
        :return: True if no wager was collected, False otherwise
        """

        return self in (GameStatus.AWAITING_SELECTION, GameStatus.AWAITING_OPPONENT_CONFIRMATION)


GAME_STATUS_DESCRIPTIONS = {
    GameStatus.ND: phrases.GAME_STATUS_ND,
    GameStatus.IN_PROGRESS: phrases.GAME_STATUS_IN_PROGRESS,
    GameStatus.WON: phrases.GAME_STATUS_WON,
    GameStatus.LOST: phrases.GAME_STATUS_LOST,
    GameStatus.DRAW: phrases.GAME_STATUS_DRAW,
    GameStatus.AWAITING_SELECTION: phrases.GAME_STATUS_AWAITING_SELECTION,
    GameStatus.AWAITING_OPPONENT_CONFIRMATION: phrases.GAME_STATUS_AWAITING_OPPONENT_CONFIRMATION,
    GameStatus.FORCED_END: phrases.GAME_STATUS_FORCED_END,
    GameStatus.COUNTDOWN_TO_START: phrases.GAME_STATUS_COUNTDOWN_TO_START,
    GameStatus.WINNING: phrases.GAME_STATUS_WINNING,
    GameStatus.LOSING: phrases.GAME_STATUS_LOSING,
}
