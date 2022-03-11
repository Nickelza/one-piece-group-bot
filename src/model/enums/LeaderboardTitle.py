import resources.Environment as Env
from src.model.enums.Emoji import Emoji
from src.model.LeaderboardUser import LeaderboardUser


class LeaderboardTitle:
    """
    Class for leaderboard titles.
    """

    def __init__(self, position: int, title_message: str, emoji: str, leaderboard_start: int, leaderboard_end: int,
                 bounty_poster_limit: int):
        """
        Constructor for leaderboard titles
        :param position: Position of the leaderboard title
        :param title_message: Title message
        :param emoji: Emoji
        :param leaderboard_start: Start index
        :param leaderboard_end: End index
        :param bounty_poster_limit: Bounty poster limit
        """
        self.position: int = position
        self.title_message: str = title_message
        self.emoji: str = emoji
        self.leaderboard_start: int = leaderboard_start
        self.leaderboard_end: int = leaderboard_end
        self.bounty_poster_limit: int = bounty_poster_limit

    def get_emoji_and_title_message(self) -> str:
        """
        Get emoji and title message
        :return: Emoji and title message
        """

        return self.emoji + ' ' + self.title_message


PIRATE_KING = LeaderboardTitle(1, 'Pirate King', Emoji.LEADERBOARD_PIRATE_KING.value, 0, 0,
                               Env.BOUNTY_POSTER_LIMIT_PIRATE_KING.get_int())

EMPEROR = LeaderboardTitle(2, 'Emperor', Emoji.LEADERBOARD_EMPEROR.value, 1, 4,
                           Env.BOUNTY_POSTER_LIMIT_EMPEROR.get_int())

FIRST_MATE = LeaderboardTitle(3, 'First Mate', Emoji.LEADERBOARD_FIRST_MATE.value, 5, 8,
                              Env.BOUNTY_POSTER_LIMIT_FIRST_MATE.get_int())

SUPERNOVA = LeaderboardTitle(4, 'Supernova', Emoji.LEADERBOARD_SUPERNOVA.value, 9, 19,
                             Env.BOUNTY_POSTER_LIMIT_SUPERNOVA.get_int())

ROOKIE = LeaderboardTitle(5, 'Rookie', Emoji.LEADERBOARD_ROOKIE.value, 20, -1,
                          Env.BOUNTY_POSTER_LIMIT_ROOKIE.get_int())

LEADERBOARD_TITLES = [PIRATE_KING, EMPEROR, FIRST_MATE, SUPERNOVA, ROOKIE]


def get_title_by_position(position: int) -> LeaderboardTitle:
    """
    Get the leaderboard title for a given position
    :param position: Position
    :return: Leaderboard title
    """
    for title in LEADERBOARD_TITLES:
        if position == title.position:
            return title

    raise ValueError('Invalid position')


def get_title_by_leaderboard_user(leaderboard_user: LeaderboardUser | None) -> LeaderboardTitle:
    """
    Get the leaderboard title for a given leaderboard user
    :param leaderboard_user: Leaderboard user
    :return: Leaderboard title
    """
    if leaderboard_user is None:
        return ROOKIE

    return get_title_by_leaderboard_index(leaderboard_user.position)


def get_title_by_leaderboard_index(leaderboard_index: int) -> LeaderboardTitle:
    """
    Get the leaderboard title for a given leaderboard index
    :param leaderboard_index: Leaderboard index
    :return: Leaderboard title
    """
    for title in LEADERBOARD_TITLES:
        if title.leaderboard_start <= leaderboard_index <= title.leaderboard_end \
                or (leaderboard_index >= title.leaderboard_start and title.leaderboard_end == -1):
            return title

    raise ValueError('Invalid leaderboard index')
