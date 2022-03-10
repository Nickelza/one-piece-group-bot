import resources.Environment as Env
import resources.emoji as emj


class LeaderboardTitle:
    """
    Class for leaderboard titles.
    """

    def __init__(self, position: int, title_message: str, emoji: str, leaderboard_start: int, leaderboard_end: int,
                 bounty_poster_limit: int | None):
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
        self.bounty_poster_limit: int | None = bounty_poster_limit


PIRATE_KING = LeaderboardTitle(1, 'Pirate King', emj.LEADERBOARD_PIRATE_KING, 0, 0,
                               Env.BOUNTY_POSTER_LIMIT_PIRATE_KING.get())

EMPEROR = LeaderboardTitle(2, 'Emperor', emj.LEADERBOARD_EMPEROR, 1, 4,
                           Env.BOUNTY_POSTER_LIMIT_EMPEROR.get())

FIRST_MATE = LeaderboardTitle(3, 'First Mate', emj.LEADERBOARD_FIRST_MATE, 5, 8,
                              Env.BOUNTY_POSTER_LIMIT_FIRST_MATE.get())

SUPERNOVA = LeaderboardTitle(4, 'Supernova', emj.LEADERBOARD_SUPERNOVA, 9, 19,
                             Env.BOUNTY_POSTER_LIMIT_SUPERNOVA.get())

ROOKIE = LeaderboardTitle(5, 'Rookie', emj.LEADERBOARD_ROOKIE, 20, -1,
                          Env.BOUNTY_POSTER_LIMIT_ROOKIE)

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
