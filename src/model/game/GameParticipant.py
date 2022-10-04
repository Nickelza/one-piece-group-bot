from enum import IntEnum


class GameParticipant(IntEnum):
    """
    Enum for the status of a game.
    """
    NONE = 0
    CHALLENGER = 1
    OPPONENT = 2
