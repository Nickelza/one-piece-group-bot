from enum import Enum


class GameStatus(Enum):
    """
    Enum for the status of a game.
    """
    IN_PROGRESS = 0
    WON = 1
    LOST = 2
