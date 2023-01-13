from datetime import datetime

from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.Leaderboard import Leaderboard
from src.model.LeaderboardUser import LeaderboardUser
from src.model.User import User
from src.model.enums import LeaderboardRank
from src.model.enums.CrewRole import CrewRole
from src.model.enums.Notification import CrewDisbandNotification, CrewDisbandWarningNotification, \
    CrewLeaveNotification, CrewMemberRemoveNotification
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.location_service import update_location
from src.service.notification_service import send_notification


def add_member(crew_member: User, crew: Crew, role: CrewRole = None) -> None:
    """
    Adds a member to a crew

    :param crew_member: The user
    :param crew: The crew
    :param role: The role
    """

    crew_member.crew = crew
    crew_member.crew_role = role
    crew_member.crew_join_date = datetime.now()

    update_location(crew_member, should_passive_update=True)

    crew_member.save()


def remove_member(crew_member, context: ContextTypes.DEFAULT_TYPE = None, send_notification_to_captain: bool = False,
                  send_notification_to_member: bool = False, disable_user_can_join_crew: bool = False,
                  disable_crew_can_accept_new_members: bool = False) -> None:
    """
    Removes a member from a crew

    :param context: The context
    :param crew_member: The user
    :param send_notification_to_captain: Whether to send a notification to the captain
    :param send_notification_to_member: Whether to send a notification to the member
    :param disable_user_can_join_crew: Whether to set user can_join_crew to False
    :param disable_crew_can_accept_new_members: Whether to set crew can_accept_new_members to False
    :return: None
    """

    crew: Crew = crew_member.crew

    crew_member.crew = None
    crew_member.crew_role = None
    crew_member.crew_join_date = None

    if disable_user_can_join_crew:
        crew_member.can_join_crew = False

    update_location(crew_member, should_passive_update=True, can_scale_down=True)

    crew_member.save()

    if disable_crew_can_accept_new_members:
        crew.can_accept_new_members = False
        crew.save()

    # User left
    if send_notification_to_captain:
        send_notification(context, crew.get_captain(), CrewLeaveNotification(crew_member))

    # User was removed
    if send_notification_to_member:
        send_notification(context, crew_member, CrewMemberRemoveNotification(crew_member))


def get_crew(user: User = None, crew_id: int = None, inbound_keyboard: Keyboard = None, crew_id_key: str = None,
             validate_against_crew: Crew = None) -> Crew:
    """
    Get crew
    :param user: The target user
    :param crew_id: The crew id
    :param inbound_keyboard: The inbound keyboard
    :param crew_id_key: The crew id key
    :param validate_against_crew: The crew to validate against and make sure the user is in the same crew
    :return: The crew
    """

    if user is None and crew_id is None and inbound_keyboard is None:
        raise ValueError('Either user or crew_id or inbound_keyboard must be provided')

    if inbound_keyboard is not None and crew_id_key is None:
        raise ValueError('crew_id_key must be provided if inbound_keyboard is provided')

    if inbound_keyboard is not None:  # Can use "else", used "elif" to avoid IDE warning
        crew: Crew = Crew.logical_get(inbound_keyboard.info[crew_id_key])
    elif user is not None:
        crew: Crew = user.crew
    else:
        crew: Crew = Crew.logical_get(crew_id)

    # Crew is not found or is not active
    if crew is None or not crew.is_active:
        raise CrewValidationException(phrases.CREW_NOT_FOUND)

    # Crew is not the same
    if validate_against_crew is not None and crew != validate_against_crew:
        raise CrewValidationException(phrases.CREW_NOT_SAME)

    return crew


def disband_crew(context: ContextTypes.DEFAULT_TYPE, captain: User, should_notify_captain: bool = False) -> None:
    """
    Disbands a crew

    :param context: The context
    :param captain: The captain, necessary to directly update the user object
    :param should_notify_captain: Whether to notify the captain
    :return: None
    """

    crew: Crew = captain.crew
    crew_members: list[User] = crew.get_members()
    for member in crew_members:
        is_captain = (member.id == captain.id)

        if is_captain:
            captain.can_create_crew = False
            remove_member(captain)  # Else user will not be updated
        else:
            remove_member(member)

        if not is_captain or should_notify_captain:
            send_notification(context, member, CrewDisbandNotification())

    crew.is_active = False
    crew.save()


async def disband_inactive_crews(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Disbands inactive crews

    :param context: The context object
    :return: None
    """

    # Find captains of a Crew that have not been in the latest required leaderboards
    inactive_crew_captains = get_inactive_captains(Env.CREW_CREATE_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int())

    # Disband inactive crews
    for captain in inactive_crew_captains:
        disband_crew(context, captain, should_notify_captain=True)


async def warn_inactive_captains(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Warns inactive captains which Crew will be disbanded in the next leaderboard

    :param context: The context object
    :return: None
    """

    inactive_captains = get_inactive_captains(Env.CREW_CREATE_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int() - 1)

    for captain in inactive_captains:
        await send_notification(context, captain, CrewDisbandWarningNotification())


def get_inactive_captains(latest_leaderboard_appearance: int) -> list[User]:
    """
    Find captains of a Crew that have not been in the latest N leaderboards in the required rank

    :param latest_leaderboard_appearance: The latest leaderboard appearance
    :return: The inactive captains
    """

    # Latest N leaderboards
    query: list[Leaderboard] = (Leaderboard.select()
                                .order_by(Leaderboard.year.desc(), Leaderboard.week.desc())
                                .limit(latest_leaderboard_appearance)
                                .execute())
    latest_leaderboards: list[Leaderboard] = list(query)

    # Captains of Crews that appeared in the latest N leaderboards in the required role
    required_rank = LeaderboardRank.get_rank_by_index(Env.CREW_MAINTAIN_MIN_LATEST_LEADERBOARD_RANK.get_int())
    query: list[User] = (User.select()
                         .join(LeaderboardUser)
                         .join(Leaderboard)
                         .where((User.crew_role == CrewRole.CAPTAIN)
                                & (Leaderboard.id.in_(latest_leaderboards))
                                & (LeaderboardUser.rank_index <= required_rank.index))
                         .execute())
    active_captains: list[User] = list(query)

    # Inactive captains
    # Have to first get inactive ones else, by using "not in", it will return records for previous leaderboards too
    # since the user might have been in a leaderboard before N, so it will not be in the latest N leaderboards
    # Exclude admins
    inactive_captains = (User.select()
                         .where((User.crew_role == CrewRole.CAPTAIN) &
                                (User.id.not_in([captain.id for captain in active_captains]))
                                & (User.is_admin == False)))

    return inactive_captains
