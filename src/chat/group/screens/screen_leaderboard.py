import datetime
import os

from telegram import Message
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_markdown

import constants as c
import resources.phrases as phrases
import src.service.bounty_service as bounty_service
from src.model.Leaderboard import Leaderboard
from src.model.LeaderboardUser import LeaderboardUser
from src.model.User import User
from src.model.enums.LeaderboardTitles import LeaderboardTitles
from src.service.message_service import full_message_send


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
        int(os.environ.get(c.ENV_LEADERBOARD_LIMIT, c.DEFAULT_LEADERBOARD_LIMIT)))

    # Create a list of LeaderboardUsers
    leaderboard_users = []
    for index, user in enumerate(users):
        leaderboard_user = LeaderboardUser()
        leaderboard_user.leaderboard = leaderboard
        leaderboard_user.user = user
        leaderboard_user.position = index + 1
        leaderboard_user.bounty = user.bounty
        leaderboard_user.title = LeaderboardTitles.ND.value
        leaderboard_user.save()

        leaderboard_users.append(leaderboard_user)

    return leaderboard_users


def get_leaderboard_message(leaderboard: Leaderboard) -> str:
    """
    Gets the leaderboard message
    :param leaderboard: The leaderboard
    :return: The leaderboard message
    """
    ot_text = phrases.LEADERBOARD_HEADER.format(leaderboard.week, leaderboard.year,
                                                leaderboard.leaderboard_users.count())

    for leaderboard_user in leaderboard.leaderboard_users:
        user: User = User.get_by_id(leaderboard_user.user.id)

        ot_text += phrases.LEADERBOARD_ROW.format(leaderboard_user.position,
                                                  mention_markdown(user.tg_user_id, user.tg_first_name, 2),
                                                  bounty_service.get_bounty_formatted(user.bounty))

    return ot_text


def manage(context: CallbackContext) -> None:
    """
    Sends the weekly leaderboard to the group
    :param context: Context of callback
    """

    leaderboard = create_leaderboard()

    # Send the leaderboard to the group
    ot_text = get_leaderboard_message(leaderboard)
    message: Message = full_message_send(context, ot_text, chat_id=os.environ[c.ENV_OPD_GROUP_ID])
    message.pin(disable_notification=False)

    # Save the message id
    leaderboard.message_id = message.message_id
    leaderboard.save()
