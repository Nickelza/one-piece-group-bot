from enum import Enum


class GameStatus(Enum):
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


def get_finished_statuses() -> list[GameStatus]:
    """
    Get the finished statuses
    :return: The finished statuses
    """
    return [GameStatus.WON, GameStatus.LOST, GameStatus.DRAW, GameStatus.FORCED_END]


def is_finished_by_status(game_status: GameStatus) -> bool:
    """
    Is the game finished by status
    :param game_status: The game status
    :return: Is the game finished
    """
    return game_status in get_finished_statuses()
