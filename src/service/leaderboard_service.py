import datetime

import resources.Environment as Env
from src.model.Leaderboard import Leaderboard
from src.model.LeaderboardUser import LeaderboardUser
from src.model.User import User
from src.model.enums.LeaderboardTitle import LeaderboardTitle


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


def create_leaderboard_users(leaderboard: Leaderboard) -> list[LeaderboardUser]:
    """
    Creates a leaderboard list
    :param leaderboard: The leaderboard to create the users for
    :return: The leaderboard users
    """
    # Get the leaderboard users
    users: list[User] = User.select().order_by(User.bounty.desc()).limit(
        int(Env.LEADERBOARD_LIMIT.get()))

    # Create a list of LeaderboardUsers
    leaderboard_users = []
    for index, user in enumerate(users):
        leaderboard_user = LeaderboardUser()
        leaderboard_user.leaderboard = leaderboard
        leaderboard_user.user = user
        leaderboard_user.position = index + 1
        leaderboard_user.bounty = user.bounty
        leaderboard_user.title = LeaderboardTitle.ND.value
        leaderboard_user.save()

        leaderboard_users.append(leaderboard_user)

    return leaderboard_users


def get_current_leaderboard_user(user: User) -> LeaderboardUser | None:
    """
    Gets the current leaderboard user for the user
    :param user: The user to get the leaderboard user for
    :return: The leaderboard user
    """
    leaderboard_user: LeaderboardUser = (LeaderboardUser.select()
                                         .join(Leaderboard)
                                         .order_by(LeaderboardUser.leaderboard.year.desc(),
                                                   LeaderboardUser.leaderboard.week.desc())
                                         .where(LeaderboardUser.user == user)
                                         .first())
    return leaderboard_user
