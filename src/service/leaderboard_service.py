import datetime

import resources.Environment as Env
from src.model.Leaderboard import Leaderboard
from src.model.LeaderboardUser import LeaderboardUser
from src.model.User import User
from src.model.enums.LeaderboardRank import LeaderboardRank, get_rank_by_index, get_rank_by_leaderboard_position, \
    get_rank_by_leaderboard_user


def create_leaderboard() -> Leaderboard:
    """
    Creates a leaderboard list
    :return: The leaderboard
    """

    year = datetime.datetime.now().isocalendar()[0]
    week = datetime.datetime.now().isocalendar()[1]

    # Delete the leaderboard if it exists
    Leaderboard.delete().where(Leaderboard.year == year, Leaderboard.week == week).execute()

    # Create a leaderboard for the current week and year
    leaderboard = Leaderboard()
    leaderboard.year = datetime.datetime.now().isocalendar()[0]
    leaderboard.week = datetime.datetime.now().isocalendar()[1]
    leaderboard.save()

    # Create the leaderboard users
    create_leaderboard_users(leaderboard)

    return leaderboard


def get_leaderboard_rank_message(index: int) -> str:
    """
    Gets the rank message of a leaderboard rank
    :param index: The leaderboard rank index
    :return: The leaderboard rank message
    """
    leaderboard_rank: LeaderboardRank = get_rank_by_index(index)
    return leaderboard_rank.get_emoji_and_rank_message()


def create_leaderboard_users(leaderboard: Leaderboard) -> list[LeaderboardUser]:
    """
    Creates a leaderboard list
    :param leaderboard: The leaderboard to create the users for
    :return: The leaderboard users
    """
    # Get the leaderboard users
    users: list[User] = User.select().order_by(User.bounty.desc()).limit(Env.LEADERBOARD_LIMIT.get_int())

    # Create a list of LeaderboardUsers
    leaderboard_users = []
    for index, user in enumerate(users):

        # Arrested user
        if user.is_arrested():
            continue

        leaderboard_user = LeaderboardUser()
        leaderboard_user.leaderboard = leaderboard
        leaderboard_user.user = user
        leaderboard_user.position = index + 1
        leaderboard_user.bounty = user.bounty
        leaderboard_user.rank_index = get_rank_by_leaderboard_position(index + 1).index
        leaderboard_user.save()

        leaderboard_users.append(leaderboard_user)

    return leaderboard_users


def get_leaderboard(index: int = 0) -> Leaderboard | None:
    """
    Gets the current leaderboard
    :param index: The index of the leaderboard to get. Higher the index, older the leaderboard.
    :return: The leaderboard
    """
    leaderboard: Leaderboard = (Leaderboard.select()
                                .order_by(Leaderboard.year.desc(),
                                          Leaderboard.week.desc())
                                .limit(1)
                                .offset(index)
                                .first())
    return leaderboard


def get_leaderboard_user(user: User, leaderboard: Leaderboard = None, index: int = None) -> LeaderboardUser | None:
    """
    Gets the leaderboard user for the user
    :param user: The user to get the leaderboard user for
    :param leaderboard: The leaderboard to get the leaderboard user for
    :param index: The index of the leaderboard to get. Higher the index, older the leaderboard
    :return: The leaderboard user
    """

    if leaderboard is None and index is None:
        raise ValueError("Either leaderboard or index must be provided")

    if leaderboard is None:
        leaderboard = get_leaderboard(index)

    leaderboard_user: LeaderboardUser = leaderboard.leaderboard_users.where(LeaderboardUser.user == user).first()
    return leaderboard_user


def get_current_leaderboard_user(user: User) -> LeaderboardUser | None:
    """
    Gets the current leaderboard user for the user
    :param user: The user to get the leaderboard user for
    :return: The leaderboard user
    """

    return get_leaderboard_user(user, index=0)


def get_current_leaderboard_rank(user: User) -> LeaderboardRank:
    """
    Gets the current leaderboard rank for the user
    :param user: The user to get the leaderboard rank for
    :return: The leaderboard rank
    """

    leaderboard_user: LeaderboardUser = get_current_leaderboard_user(user)
    return get_rank_by_leaderboard_user(leaderboard_user)
