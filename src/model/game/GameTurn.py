from enum import Enum


class GameTurn(Enum):
    """
    Enum for the game turn
    """
    CHALLENGER = 1
    OPPONENT = 2
    FINISHED = 3
