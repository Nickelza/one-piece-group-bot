from enum import IntEnum


class GameOutcome(IntEnum):
    """
    Enum for the status of a game.
    """
    NONE = 0
    CHALLENGER_WON = 1
    OPPONENT_WON = 2
    DRAW = 3
