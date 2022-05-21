from enum import Enum


class GameParticipant(Enum):
    """
    Enum for the status of a game.
    """
    NONE = 0
    CHALLENGER = 1
    OPPONENT = 2
