import datetime
import logging

from telegram import Message
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import src.model.enums.LeaderboardRank as LeaderboardRank
from resources import phrases as phrases, Environment as Env
from src.model.Crew import Crew
from src.model.Group import Group
from src.model.GroupChat import GroupChat
from src.model.Leaderboard import Leaderboard
from src.model.LeaderboardUser import LeaderboardUser
from src.model.User import User
from src.model.Warlord import Warlord
from src.model.enums.Feature import Feature
from src.model.enums.LeaderboardRank import LeaderboardRankIndex
from src.model.enums.Location import get_first_new_world, get_last_paradise
from src.service.bounty_poster_service import reset_bounty_poster_limit
from src.service.crew_service import disband_inactive_crews, warn_inactive_captains
from src.service.date_service import default_date_format
from src.service.devil_fruit_service import revoke_devil_fruit_from_inactive_users, \
    warn_inactive_users_with_eaten_devil_fruit
from src.service.group_service import broadcast_to_chats_with_feature_enabled_dispatch
from src.service.message_service import mention_markdown_v2, full_message_send, get_message_url


def get_leaderboard_message(leaderboard: Leaderboard, global_leaderboard_message_id: int = None) -> str:
    """
    Gets the leaderboard message
    :param leaderboard: The leaderboard
    :param global_leaderboard_message_id: The global leaderboard message id
    :return: The leaderboard message
    """

    from src.service.bounty_service import get_next_bounty_reset_time
    from src.service.date_service import get_remaining_duration

    content_text = ""
    for index, leaderboard_user in enumerate(leaderboard.leaderboard_users):
        leaderboard_user: LeaderboardUser = leaderboard_user
        user: User = leaderboard_user.user

        # Special rank, don't show in leaderboard
        if LeaderboardRankIndex(leaderboard_user.rank_index).is_special():
            continue

        content_text += phrases.LEADERBOARD_ROW.format(leaderboard_user.position,
                                                       get_leaderboard_rank_message(leaderboard_user.rank_index),
                                                       mention_markdown_v2(user.tg_user_id, user.tg_first_name),
                                                       user.get_bounty_formatted())

    next_bounty_reset_time = get_next_bounty_reset_time()
    local_global_text = phrases.LEADERBOARD_GLOBAL if leaderboard.group is None else phrases.LEADERBOARD_LOCAL
    if global_leaderboard_message_id is not None:
        view_global_leaderboard_text = phrases.LEADERBOARD_VIEW_GLOBAL_LEADERBOARD.format(
            get_message_url(message_id=global_leaderboard_message_id, chat_id=Env.UPDATES_CHANNEL_ID.get()))
    else:
        view_global_leaderboard_text = ""
    return phrases.LEADERBOARD.format(local_global_text, leaderboard.week, leaderboard.year,
                                      leaderboard.leaderboard_users.count(), content_text, view_global_leaderboard_text,
                                      default_date_format(next_bounty_reset_time),
                                      get_remaining_duration(next_bounty_reset_time))


async def send_leaderboard(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Sends the weekly leaderboard to the group chat
    :param context: Context of callback
    """
    from src.service.bounty_service import should_reset_bounty, reset_bounty

    # Create and send the leaderboard, not fire and forget because all leaderboards need to be completed before
    # eventually resetting the bounty
    await manage_leaderboard(context)

    # Reset bounty poster limit
    context.application.create_task(reset_bounty_poster_limit(reset_previous_leaderboard=True))

    # Reset can join crew flag
    User.update(can_join_crew=True).execute()

    # Rest crew can accept new members flag
    Crew.update(can_accept_new_members=True).execute()

    # Reset bounty if last leaderboard of the month
    if should_reset_bounty(datetime.datetime.now(datetime.timezone.utc)):
        context.application.create_task(reset_bounty(context))

    # Disband inactive crews
    context.application.create_task(disband_inactive_crews(context))

    # Warn captains about inactive crews
    context.application.create_task(warn_inactive_captains(context))

    # Revoke eaten Devil Fruits from inactive users
    context.application.create_task(revoke_devil_fruit_from_inactive_users(context))

    # Warn inactive users with eaten Devil Fruits
    context.application.create_task(warn_inactive_users_with_eaten_devil_fruit(context))


async def manage_leaderboard(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Manages the leaderboard
    :param context: Context of callback
    :return: None
    """

    # Create and send global leaderboard
    global_leaderboard = await create_and_send_leaderboard(context)

    # Get all active groups
    groups: list[Group] = Group.select().where(Group.is_active == True).order_by(Group.id.asc())

    # Create and send local leaderboards
    for group in groups:
        context.application.create_task(create_and_send_leaderboard(context, group, global_leaderboard))


async def create_and_send_leaderboard(context: ContextTypes, group: Group = None, global_leaderboard: Leaderboard = None
                                      ) -> Leaderboard | None:
    """
    Creates a leaderboard list and sends it to the group chat
    :return: The leaderboard
    """

    if group is not None and global_leaderboard is None:
        raise ValueError("In order to create a local leaderboard, a global leaderboard must be provided")

    # If local leaderboard, check that the group has enough active users
    if group is not None and len(group.get_active_users()) < Env.LEADERBOARD_MIN_ACTIVE_USERS.get_int():
        return

    leaderboard = Leaderboard()

    # If global leaderboard is provided, use its data
    if global_leaderboard is not None:
        year = global_leaderboard.year
        week = global_leaderboard.week
    else:
        year = datetime.datetime.now().isocalendar()[0]
        week = datetime.datetime.now().isocalendar()[1]

    # Delete the leaderboard if it exists
    Leaderboard.delete().where(Leaderboard.year == year, Leaderboard.week == week, Leaderboard.group == group).execute()

    # Create a leaderboard for the current week and year and group
    leaderboard.year = datetime.datetime.now().isocalendar()[0]
    leaderboard.week = datetime.datetime.now().isocalendar()[1]
    leaderboard.group = group

    leaderboard.save()

    # Create the leaderboard users
    create_leaderboard_users(leaderboard, group)

    # Send message to chats
    if Env.SEND_MESSAGE_LEADERBOARD.get_bool():
        ot_text = get_leaderboard_message(leaderboard, (global_leaderboard.global_message_id
                                                        if global_leaderboard is not None else None))
        if group is not None:
            await broadcast_to_chats_with_feature_enabled_dispatch(context, Feature.LEADERBOARD, ot_text,
                                                                   filter_by_groups=[group])
        else:
            try:
                message: Message = await full_message_send(context, ot_text, chat_id=Env.UPDATES_CHANNEL_ID.get())
                leaderboard.global_message_id = message.message_id
                leaderboard.save()
            except TelegramError:
                logging.exception(f'Failed to send global leaderboard to {Env.UPDATES_CHANNEL_ID.get()}')

    return leaderboard


def get_leaderboard_rank_message(index: int) -> str:
    """
    Gets the rank message of a leaderboard rank
    :param index: The leaderboard rank index
    :return: The leaderboard rank message
    """
    leaderboard_rank: LeaderboardRank = LeaderboardRank.get_rank_by_index(index)
    return leaderboard_rank.get_emoji_and_rank_message()


def create_leaderboard_users(leaderboard: Leaderboard, group: Group | None) -> list[LeaderboardUser]:
    """
    Creates a leaderboard list
    :param leaderboard: The leaderboard to create the users for
    :param group: The group to create the users for
    :return: The leaderboard users
    """

    leaderboard_users: list[LeaderboardUser] = []
    position = 1

    # If global leaderboard, exclude users that are exempted from global leaderboard requirements
    excluded_user_ids: list[int] = []
    if group is None:
        excluded_user_ids: list[int] = list(User
                                            .select(User.id)
                                            .where(User.is_exempt_from_global_leaderboard_requirements == True)
                                            .execute())

        # Add warlords
        excluded_user_ids.extend(Warlord.get_active_user_ids())

    # Get previous leaderboard users who were Emperors or higher
    previous_leaderboard: Leaderboard = get_leaderboard(1, group)
    if previous_leaderboard is None:
        previous_leaderboard_users = []
    else:
        previous_leaderboard_users = previous_leaderboard.leaderboard_users

    # Ids of eligible users for the leaderboard
    if group is None:
        eligible_leaderboard_user_ids: list[int] = User.select(User.id)
    else:
        eligible_leaderboard_user_ids: list[int] = User.select(User.id).where(User.id.in_(group.get_active_users_ids()))

    # Eligible users for Pirate King position - Those who were Emperor or higher in the previous leaderboard
    eligible_pk_users: list[User] = [leaderboard_user.user for leaderboard_user in previous_leaderboard_users
                                     if leaderboard_user.rank_index <= LeaderboardRank.EMPEROR.index]

    # Get current New World users, excluding arrested users and Admins
    new_world_users: list[User] = list(User.select()
                                       .where((User.location_level >= get_first_new_world().level)
                                              & (User.get_is_not_arrested_statement_condition())
                                              & (User.is_admin == False)
                                              & (User.id.in_(eligible_leaderboard_user_ids))
                                              & (User.id.not_in(excluded_user_ids)))
                                       .order_by(User.bounty.desc()))

    # Save Pirate King, if available
    for user in new_world_users:
        if user in eligible_pk_users:
            leaderboard_user: LeaderboardUser = save_leaderboard_user(leaderboard, user, position,
                                                                      LeaderboardRank.PIRATE_KING)
            leaderboard_users.append(leaderboard_user)
            position += 1
            break

    # Save Emperors, next 4 users
    added_users_count = 0
    for user in new_world_users:
        if not any(lu for lu in leaderboard_users if lu.user == user):
            leaderboard_user: LeaderboardUser = save_leaderboard_user(leaderboard, user, position,
                                                                      LeaderboardRank.EMPEROR)
            leaderboard_users.append(leaderboard_user)
            position += 1
            added_users_count += 1
            if added_users_count == 4:
                break

    # Save First Mates, next 4 users
    added_users_count = 0
    for user in new_world_users:
        if not any(lu for lu in leaderboard_users if lu.user == user):
            leaderboard_user: LeaderboardUser = save_leaderboard_user(leaderboard, user, position,
                                                                      LeaderboardRank.FIRST_MATE)
            leaderboard_users.append(leaderboard_user)
            position += 1
            added_users_count += 1
            if added_users_count == 4:
                break

    # Get current Paradise users, excluding arrested users and Admins
    paradise_users: list[User] = list(User.select()
                                      .where((User.location_level <= get_last_paradise().level)
                                             & (User.get_is_not_arrested_statement_condition())
                                             & (User.is_admin == False)
                                             & (User.id.in_(eligible_leaderboard_user_ids))
                                             & (User.id.not_in(excluded_user_ids)))
                                      .order_by(User.bounty.desc()))

    # Save Supernovas, next 11 users
    added_users_count = 0
    for user in paradise_users:
        if not any(lu for lu in leaderboard_users if lu.user == user):
            leaderboard_user: LeaderboardUser = save_leaderboard_user(leaderboard, user, position,
                                                                      LeaderboardRank.SUPERNOVA)
            leaderboard_users.append(leaderboard_user)
            position += 1
            added_users_count += 1
            if added_users_count == 11:
                break

    # Save Warlords, if global leaderboard
    if group is None:
        for index, warlord in enumerate(Warlord.get_active_order_by_bounty()):
            leaderboard_user: LeaderboardUser = save_leaderboard_user(leaderboard, warlord.user, index + 1,
                                                                      LeaderboardRank.WARLORD)
            leaderboard_users.append(leaderboard_user)

        return leaderboard_users


def save_leaderboard_user(leaderboard: Leaderboard, user: User, position: int, rank: LeaderboardRank.LeaderboardRank
                          ) -> LeaderboardUser:
    """
    Saves a leaderboard user
    :param leaderboard: The leaderboard
    :param user: The user
    :param position: The position
    :param rank: The rank
    """
    leaderboard_user = LeaderboardUser()
    leaderboard_user.leaderboard = leaderboard
    leaderboard_user.user = user
    leaderboard_user.position = position
    leaderboard_user.rank_index = rank.index
    leaderboard_user.bounty = user.bounty
    leaderboard_user.save()

    return leaderboard_user


def get_leaderboard(index: int = 0, group: Group = None, group_chat: GroupChat = None) -> Leaderboard | None:
    """
    Gets the current leaderboard
    :param index: The index of the leaderboard to get. Higher the index, older the leaderboard.
    :param group: The group to get the leaderboard for
    :param group_chat: The group chat to get the leaderboard for
    :return: The leaderboard
    """

    if group_chat is not None:
        group = group_chat.group

    leaderboard: Leaderboard = (Leaderboard.select()
                                .where(Leaderboard.group == group)
                                .order_by(Leaderboard.year.desc(),
                                          Leaderboard.week.desc())
                                .limit(1)
                                .offset(index)
                                .first())
    return leaderboard


def get_leaderboard_user(user: User, index: int = None, group_chat: GroupChat = None) -> LeaderboardUser | None:
    """
    Gets the leaderboard user for the user
    :param user: The user to get the leaderboard user for
    :param index: The index of the leaderboard to get. Higher the index, older the leaderboard
    :param group_chat: The group chat to get the leaderboard user for
    :return: The leaderboard user
    """

    leaderboard = get_leaderboard(index, group_chat=group_chat)  # Local
    if leaderboard is None and group_chat is not None:
        leaderboard = get_leaderboard(index)

    leaderboard_user: LeaderboardUser = leaderboard.leaderboard_users.where(LeaderboardUser.user == user).first()
    return leaderboard_user


def get_current_leaderboard_user(user: User, group_chat: GroupChat = None) -> LeaderboardUser | None:
    """
    Gets the current leaderboard user for the user
    :param user: The user to get the leaderboard user for
    :param group_chat: The group chat to get the leaderboard user for
    :return: The leaderboard user
    """

    return get_leaderboard_user(user, index=0, group_chat=group_chat)


def get_current_leaderboard_rank(user: User, group_chat: GroupChat = None) -> LeaderboardRank.LeaderboardRank:
    """
    Gets the current leaderboard rank for the user
    :param user: The user to get the leaderboard rank for
    :param group_chat: The group chat to get the leaderboard rank for
    :return: The leaderboard rank
    """

    leaderboard_user: LeaderboardUser = get_current_leaderboard_user(user, group_chat=group_chat)
    return LeaderboardRank.get_rank_by_leaderboard_user(leaderboard_user)


def get_highest_active_rank(user: User, group_chat: GroupChat) -> LeaderboardRank:
    """
    Get the highest active rank for a given user
    If the user has a special rank, the special rank is returned if it's higher than the user's leaderboard rank
    :param user: User
    :param group_chat: Group chat
    :return: Leaderboard rank
    """
    # Get current leaderboard user
    leaderboard_user: LeaderboardUser = get_current_leaderboard_user(user, group_chat=group_chat)

    # Get current leaderboard rank
    leaderboard_rank: LeaderboardRank = LeaderboardRank.get_rank_by_leaderboard_user(leaderboard_user)

    # Get special rank
    special_rank: LeaderboardRank = LeaderboardRank.get_special_rank(user)

    if special_rank is None or leaderboard_rank.is_higher(special_rank):
        return leaderboard_rank

    return special_rank
