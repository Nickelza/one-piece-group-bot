from enum import IntEnum


class GameStatus(IntEnum):
    """
    Enum for the status of a game.
    """
    IN_PROGRESS = 0
    WON = 1
    LOST = 2
    DRAW = 3
    AWAITING_SELECTION = 4
    AWAITING_OPPONENT_CONFIRMATION = 5
    FORCED_END = 6

    @staticmethod
    def get_finished() -> list['GameStatus']:
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
