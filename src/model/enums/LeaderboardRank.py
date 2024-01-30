from enum import IntEnum

import resources.Environment as Env
import resources.phrases as phrases
from src.model.LeaderboardUser import LeaderboardUser
from src.model.User import User
from src.model.enums.Emoji import Emoji


class LeaderboardRankIndex(IntEnum):
    PIRATE_KING = 1
    EMPEROR = 2
    FIRST_MATE = 3
    SUPERNOVA = 4
    ROOKIE = 5
    ADMIN = 6
    LEGENDARY_PIRATE = 7
    WARLORD = 8

    def is_special(self) -> bool:
        """
        Checks if the rank is special
        :return: True if the rank is special
        """

        return self in [
            LeaderboardRankIndex.ADMIN,
            LeaderboardRankIndex.LEGENDARY_PIRATE,
            LeaderboardRankIndex.WARLORD,
        ]


RANK_ORDER = [
    LeaderboardRankIndex.ADMIN,
    LeaderboardRankIndex.LEGENDARY_PIRATE,
    LeaderboardRankIndex.PIRATE_KING,
    LeaderboardRankIndex.WARLORD,
    LeaderboardRankIndex.EMPEROR,
    LeaderboardRankIndex.FIRST_MATE,
    LeaderboardRankIndex.SUPERNOVA,
    LeaderboardRankIndex.ROOKIE,
]


class LeaderboardRank:
    """
    Class for leaderboard ranks.
    """

    def __init__(
        self,
        index: int,
        title: str,
        emoji: str,
        leaderboard_start: int | None,
        leaderboard_end: int | None,
        bounty_poster_limit: int,
        max_win_probability: float,
        min_win_probability: float,
    ) -> None:
        """
        Constructor for leaderboard ranks
        :param index: Index of the leaderboard rank. Lower index means higher rank
        :param title: Title
        :param emoji: Emoji
        :param leaderboard_start: Start index
        :param leaderboard_end: End index
        :param bounty_poster_limit: Bounty poster limit
        :param max_win_probability: Max win probability in percentage
        :param min_win_probability: Min win probability in percentage
        """
        self.index: int = index
        self.title: str = title
        self.emoji: str = emoji
        self.leaderboard_start: int = leaderboard_start
        self.leaderboard_end: int = leaderboard_end
        self.bounty_poster_limit: int = bounty_poster_limit
        self.max_win_probability: float = max_win_probability
        self.min_win_probability: float = min_win_probability

    def get_emoji_and_rank_message(self) -> str:
        """
        Get emoji and rank message
        :return: Emoji and rank message
        """

        return self.emoji + " " + self.title

    def is_higher(self, other: "LeaderboardRank") -> bool:
        """
        Checks if current rank  higher than the other rank
        :param other: The other rank
        :return: True if the rank is higher than the other rank
        """
        return RANK_ORDER.index(LeaderboardRankIndex(self.index)) < RANK_ORDER.index(
            LeaderboardRankIndex(other.index)
        )


PIRATE_KING = LeaderboardRank(
    LeaderboardRankIndex.PIRATE_KING,
    phrases.LEADERBOARD_RANK_PIRATE_KING,
    Emoji.LEADERBOARD_PIRATE_KING,
    1,
    1,
    Env.BOUNTY_POSTER_LIMIT_PIRATE_KING.get_int(),
    Env.FIGHT_MAX_WIN_PROBABILITY_PIRATE_KING.get_float(),
    Env.FIGHT_MIN_WIN_PROBABILITY_PIRATE_KING.get_float(),
)

EMPEROR = LeaderboardRank(
    LeaderboardRankIndex.EMPEROR,
    phrases.LEADERBOARD_RANK_EMPEROR,
    Emoji.LEADERBOARD_EMPEROR,
    2,
    5,
    Env.BOUNTY_POSTER_LIMIT_EMPEROR.get_int(),
    Env.FIGHT_MAX_WIN_PROBABILITY_FIRST_MATE.get_float(),
    Env.FIGHT_MIN_WIN_PROBABILITY_FIRST_MATE.get_float(),
)

FIRST_MATE = LeaderboardRank(
    LeaderboardRankIndex.FIRST_MATE,
    phrases.LEADERBOARD_RANK_FIRST_MATE,
    Emoji.LEADERBOARD_FIRST_MATE,
    6,
    9,
    Env.BOUNTY_POSTER_LIMIT_FIRST_MATE.get_int(),
    Env.FIGHT_MAX_WIN_PROBABILITY_FIRST_MATE.get_float(),
    Env.FIGHT_MIN_WIN_PROBABILITY_FIRST_MATE.get_float(),
)

SUPERNOVA = LeaderboardRank(
    LeaderboardRankIndex.SUPERNOVA,
    phrases.LEADERBOARD_RANK_SUPERNOVA,
    Emoji.LEADERBOARD_SUPERNOVA,
    10,
    20,
    Env.BOUNTY_POSTER_LIMIT_SUPERNOVA.get_int(),
    Env.FIGHT_MAX_WIN_PROBABILITY_SUPERNOVA.get_float(),
    Env.FIGHT_MIN_WIN_PROBABILITY_SUPERNOVA.get_float(),
)

ROOKIE = LeaderboardRank(
    LeaderboardRankIndex.ROOKIE,
    phrases.LEADERBOARD_RANK_ROOKIE,
    Emoji.LEADERBOARD_ROOKIE,
    21,
    -1,
    Env.BOUNTY_POSTER_LIMIT_ROOKIE.get_int(),
    Env.FIGHT_MAX_WIN_PROBABILITY_ROOKIE.get_float(),
    Env.FIGHT_MIN_WIN_PROBABILITY_ROOKIE.get_float(),
)

ADMIN = LeaderboardRank(
    LeaderboardRankIndex.ADMIN,
    phrases.LEADERBOARD_RANK_ADMIN,
    Emoji.LEADERBOARD_ADMIN,
    None,
    None,
    Env.BOUNTY_POSTER_LIMIT_PIRATE_KING.get_int(),
    Env.FIGHT_MAX_WIN_PROBABILITY_PIRATE_KING.get_float(),
    Env.FIGHT_MIN_WIN_PROBABILITY_PIRATE_KING.get_float(),
)

LEGENDARY_PIRATE = LeaderboardRank(
    LeaderboardRankIndex.LEGENDARY_PIRATE,
    phrases.LEADERBOARD_RANK_LEGENDARY_PIRATE,
    Emoji.LEADERBOARD_LEGENDARY_PIRATE,
    None,
    None,
    Env.BOUNTY_POSTER_LIMIT_PIRATE_KING.get_int(),
    Env.FIGHT_MAX_WIN_PROBABILITY_PIRATE_KING.get_float(),
    Env.FIGHT_MIN_WIN_PROBABILITY_PIRATE_KING.get_float(),
)

WARLORD = LeaderboardRank(
    LeaderboardRankIndex.WARLORD,
    phrases.LEADERBOARD_RANK_WARLORD,
    Emoji.LEADERBOARD_WARLORD,
    None,
    None,
    Env.BOUNTY_POSTER_LIMIT_WARLORD.get_int(),
    Env.FIGHT_MAX_WIN_PROBABILITY_EMPEROR.get_float(),
    Env.FIGHT_MIN_WIN_PROBABILITY_EMPEROR.get_float(),
)

LEADERBOARD_RANKS = [
    PIRATE_KING,
    EMPEROR,
    FIRST_MATE,
    SUPERNOVA,
    ROOKIE,
    ADMIN,
    LEGENDARY_PIRATE,
    WARLORD,
]


def get_rank_by_index(index: int) -> LeaderboardRank:
    """
    Get the leaderboard rank for a given rank
    :param index: Index
    :return: Leaderboard rank
    """
    for rank in LEADERBOARD_RANKS:
        if index == rank.index:
            return rank

    raise ValueError("Invalid index")


def get_rank_by_leaderboard_user(leaderboard_user: LeaderboardUser | None) -> LeaderboardRank:
    """
    Get the leaderboard rank for a given leaderboard user
    :param leaderboard_user: Leaderboard user
    :return: Leaderboard rank
    """
    if leaderboard_user is None:
        return ROOKIE

    return get_rank_by_index(leaderboard_user.rank_index)


def get_rank_by_leaderboard_position(leaderboard_position: int) -> LeaderboardRank:
    """
    Get the leaderboard rank for a given leaderboard position
    :param leaderboard_position: Leaderboard position
    :return: Leaderboard rank
    """
    for rank in LEADERBOARD_RANKS:
        if rank.leaderboard_start <= leaderboard_position <= rank.leaderboard_end or (
            leaderboard_position >= rank.leaderboard_start and rank.leaderboard_end == -1
        ):
            return rank

    raise ValueError("Invalid leaderboard position")


def get_special_rank(user: User) -> LeaderboardRank | None:
    """
    Get the special rank for a given user
    :param user: User
    :return: Special rank
    """
    if user.is_admin:
        return ADMIN

    if user.is_legendary_pirate():
        return LEGENDARY_PIRATE

    if user.is_warlord():
        return WARLORD

    return None
