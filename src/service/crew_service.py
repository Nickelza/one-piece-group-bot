from datetime import datetime

from telegram.ext import ContextTypes

import resources.Environment as Env
from resources import phrases as phrases
from src.model.Crew import Crew
from src.model.CrewAbility import CrewAbility
from src.model.CrewChestSpendingRecord import CrewChestSpendingRecord
from src.model.CrewMemberChestContribution import CrewMemberChestContribution
from src.model.Leaderboard import Leaderboard
from src.model.LeaderboardUser import LeaderboardUser
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.Notification import CrewDisbandNotification, CrewDisbandWarningNotification, \
    CrewLeaveNotification, CrewMemberRemoveNotification, Notification
from src.model.enums.crew.CrewAbilityAcquiredMethod import CrewAbilityAcquiredMethod
from src.model.enums.crew.CrewChestSpendingReason import CrewChestSpendingReason
from src.model.enums.crew.CrewRole import CrewRole
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.date_service import get_remaining_duration, get_datetime_in_future_days
from src.service.location_service import update_location
from src.service.notification_service import send_notification


async def add_member(crew_member: User, crew: Crew, role: CrewRole = None) -> None:
    """
    Adds a member to a crew

    :param crew_member: The user
    :param crew: The crew
    :param role: The role
    """

    crew_member.crew = crew
    crew_member.crew_role = role
    crew_member.crew_join_date = datetime.now()

    await update_location(crew_member, should_passive_update=True)

    crew_member.save()


async def remove_member(crew_member, context: ContextTypes.DEFAULT_TYPE = None,
                        send_notification_to_captain: bool = False, send_notification_to_member: bool = False,
                        disable_user_can_join_crew: bool = False, disable_crew_can_accept_new_members: bool = False
                        ) -> None:
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

    await update_location(crew_member, should_passive_update=True, can_scale_down=True)

    crew_member.save()

    if disable_crew_can_accept_new_members:
        crew.can_accept_new_members = False
        crew.save()

    # User left
    if send_notification_to_captain:
        await send_notification(context, crew.get_captain(), CrewLeaveNotification(crew_member))

    # User was removed
    if send_notification_to_member:
        await send_notification(context, crew_member, CrewMemberRemoveNotification(crew_member))


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


async def disband_crew(context: ContextTypes.DEFAULT_TYPE, captain: User, should_notify_captain: bool = False) -> None:
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
            await remove_member(captain)  # Else user will not be updated
        else:
            await remove_member(member)

        if not is_captain or should_notify_captain:
            await send_notification(context, member, CrewDisbandNotification())

    crew.is_active = False
    crew.disband_date = datetime.now()
    crew.save()


async def disband_inactive_crews(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Disbands inactive crews

    :param context: The context object
    :return: None
    """

    # Find captains of a Crew that have not been in the latest required leaderboards
    inactive_crew_captains = get_inactive_captains(Env.CREW_MAINTAIN_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int())

    # Disband inactive crews
    for captain in inactive_crew_captains:
        await disband_crew(context, captain, should_notify_captain=True)


async def warn_inactive_captains(context: ContextTypes.DEFAULT_TYPE, users: list[User] = None
                                 ) -> None:
    """
    Warns inactive captains which Crew will be disbanded in the next leaderboard

    :param context: The context object
    :param users: The users to warn, if None, all inactive captains will be warned
    :return: None
    """

    inactive_captains = get_inactive_captains(Env.CREW_MAINTAIN_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int() - 1)

    for captain in inactive_captains:
        if users is None or captain in users:
            await send_notification(context, captain, CrewDisbandWarningNotification())


def get_inactive_captains(latest_leaderboard_appearance: int) -> list[User]:
    """
    Find captains of a Crew that have not been in the latest N leaderboards in the required rank

    :param latest_leaderboard_appearance: The latest leaderboard appearance
    :return: The inactive captains
    """

    # Latest N leaderboards
    latest_leaderboards: list[Leaderboard] = Leaderboard.get_latest_n(n=latest_leaderboard_appearance)

    # Captains of Crews that appeared in the latest N leaderboards in the required role
    query: list[User] = (User.select()
                         .join(LeaderboardUser)
                         .join(Leaderboard)
                         .where((User.crew_role == CrewRole.CAPTAIN)
                                & (Leaderboard.id.in_(latest_leaderboards)))
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


def add_to_crew_chest(user: User, amount: int) -> None:
    """
    Adds to the crew chest

    :param user: The user
    :param amount: The amount
    :return: None
    """

    if not user.is_crew_member():
        raise ValueError('User is not a crew member')

    crew: Crew = user.crew
    crew.chest_amount += amount
    crew.save()

    # Save contribution
    contribution: CrewMemberChestContribution = CrewMemberChestContribution.get_or_none(
        (CrewMemberChestContribution.crew == crew) & (CrewMemberChestContribution.user == user))

    if contribution is None:
        contribution = CrewMemberChestContribution()
        contribution.crew = crew
        contribution.user = user

    contribution.amount += amount
    contribution.last_contribution_date = datetime.now()
    contribution.save()


def get_crew_abilities_text(crew: Crew = None, active_abilities: list[CrewAbility] = None,
                            add_duration: bool = False, add_emoji: bool = False):
    """
    Returns the crew abilities text
    :param crew: The crew
    :param active_abilities: The active abilities
    :param add_duration: Whether to add the duration
    :param add_emoji: Whether to add the positive log emoji
    :return: The crew abilities text
    """

    if active_abilities is None:
        active_abilities = crew.get_active_abilities()

    if len(active_abilities) == 0:
        abilities_text = phrases.CREW_ABILITY_NO_ABILITIES
    else:  # Recap
        active_abilities_text_list = []
        emoji_text = Emoji.LOG_POSITIVE.value if add_emoji else ''
        for ability in active_abilities:
            text = phrases.CREW_ABILITY_ITEM_TEXT.format(emoji_text, ability.get_description(),
                                                         ability.get_value_with_sign())
            if add_duration:
                text += phrases.CREW_ABILITY_ITEM_TEXT_DURATION.format(get_remaining_duration(ability.expiration_date))

            active_abilities_text_list.append(text)

        abilities_text = ('\n' if add_duration else '').join(active_abilities_text_list)

    return abilities_text


def notify_crew_members(context: ContextTypes.DEFAULT_TYPE, crew: Crew, notification: Notification,
                        exclude_user: User = None) -> None:
    """
    Notifies crew members

    :param context: The context
    :param crew: The crew
    :param notification: The notification
    :param exclude_user: The user to exclude
    :return: None
    """

    for member in crew.get_members():
        if member.id != exclude_user.id:
            send_notification(context, member, notification)


async def add_crew_ability(context: ContextTypes.DEFAULT_TYPE, crew: Crew, ability_type: DevilFruitAbilityType,
                           ability_value: int, acquired_method: CrewAbilityAcquiredMethod, acquired_user: User) -> None:
    """
    Adds a crew ability

    :param context: The context
    :param crew: The crew
    :param ability_type: The ability type
    :param ability_value: The ability value
    :param acquired_method: The acquired method
    :param acquired_user: The acquired user
    :return: The crew ability
    """

    ability: CrewAbility = CrewAbility()
    ability.crew = crew
    ability.ability_type = ability_type
    ability.value = ability_value
    ability.acquired_method = acquired_method
    ability.acquired_user = acquired_user
    ability.expiration_date = get_datetime_in_future_days(Env.CREW_ABILITY_DURATION_DAYS.get_int())
    ability.save()

    # Notify crew members
    # TODO build notification


async def remove_crew_ability(context: ContextTypes.DEFAULT_TYPE, crew_ability: CrewAbility) -> None:
    """
    Removes a crew ability

    :param context: The context
    :param crew_ability: The crew ability
    :return: None
    """

    crew_ability.expiration_date = datetime.now()
    crew_ability.was_removed = True
    crew_ability.save()

    # TODO build notification


def add_powerup(crew: Crew, acquired_user: User) -> None:
    """
    Adds a powerup to a crew

    :param crew: The crew
    :param acquired_user: The user who acquired the powerup
    :return: None
    """

    powerup_price = crew.get_powerup_price()
    crew.chest_amount -= powerup_price
    crew.powerup_counter += 1
    crew.save()

    # Add spending record
    add_chest_spending_record(crew, powerup_price, CrewChestSpendingReason.ABILITY, acquired_user)


def add_chest_spending_record(crew: Crew, amount: int, reason: CrewChestSpendingReason, by_user: User,
                              to_user: User = None) -> None:
    """
    Adds a chest spending record

    :param crew: The crew
    :param amount: The amount
    :param reason: The reason
    :param by_user: User who spent the amount
    :param to_user: User who received the amount, in case of a transfer
    :return: None
    """

    record: CrewChestSpendingRecord = CrewChestSpendingRecord()
    record.crew = crew
    record.amount = amount
    record.reason = reason
    record.by_user = by_user
    record.to_user = to_user
    record.save()
