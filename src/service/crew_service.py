from datetime import datetime

from telegram.ext import ContextTypes

from resources import phrases as phrases, Environment as Env
from src.model.Crew import Crew
from src.model.CrewAbility import CrewAbility
from src.model.CrewChestSpendingRecord import CrewChestSpendingRecord
from src.model.CrewMemberChestContribution import CrewMemberChestContribution
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.Notification import (
    CrewDisbandNotification,
    CrewDisbandWarningNotification,
    CrewLeaveNotification,
    CrewMemberRemoveNotification,
    Notification,
    CrewAbilityActivatedNotification,
)
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.enums.crew.CrewAbilityAcquiredMethod import CrewAbilityAcquiredMethod
from src.model.enums.crew.CrewChestSpendingReason import CrewChestSpendingReason
from src.model.enums.crew.CrewRole import CrewRole
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_belly_formatted
from src.service.date_service import (
    get_remaining_duration,
    get_datetime_in_future_days,
    get_elapsed_duration,
)
from src.service.location_service import update_location
from src.service.message_service import get_deeplink
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
    crew.set_is_full()


async def remove_member(
    crew_member,
    context: ContextTypes.DEFAULT_TYPE = None,
    send_notification_to_captain: bool = False,
    send_notification_to_member: bool = False,
    disable_user_can_join_crew: bool = False,
    disable_crew_can_accept_new_members: bool = False,
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
    crew.set_is_full()

    if disable_crew_can_accept_new_members:
        crew.can_accept_new_members = False
        crew.save()

    # User left
    if send_notification_to_captain:
        await send_notification(context, crew.get_captain(), CrewLeaveNotification(crew_member))

        # Send notification to first mate
        first_mate = crew.get_first_mate()
        if first_mate is not None:
            await send_notification(context, first_mate, CrewLeaveNotification(crew_member))

    # User was removed
    if send_notification_to_member:
        await send_notification(context, crew_member, CrewMemberRemoveNotification(crew_member))


def get_crew(
    user: User = None,
    crew_id: int = None,
    inbound_keyboard: Keyboard = None,
    crew_id_key: str = None,
    validate_against_crew: Crew = None,
) -> Crew:
    """
    Get crew

    :param user: The target user
    :param crew_id: The crew id
    :param inbound_keyboard: The inbound keyboard
    :param crew_id_key: The crew id key
    :param validate_against_crew: The crew to validate against and make sure the user is in the
    same crew

    :return: The crew
    """

    if user is None and crew_id is None and inbound_keyboard is None:
        raise ValueError("Either user or crew_id or inbound_keyboard must be provided")

    if inbound_keyboard is not None and crew_id_key is None:
        raise ValueError("crew_id_key must be provided if inbound_keyboard is provided")

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


async def disband_crew(
    context: ContextTypes.DEFAULT_TYPE, captain: User, should_notify_captain: bool = False
) -> None:
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
        is_captain = member.id == captain.id

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
    inactive_crew_captains = get_inactive_captains()

    # Disband inactive crews
    for captain in inactive_crew_captains:
        await disband_crew(context, captain, should_notify_captain=True)


async def warn_inactive_captains(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Warns inactive captains which Crew will be disbanded in the next leaderboard

    :param context: The context object
    :return: None
    """

    inactive_captains = get_inactive_captains()

    for captain in inactive_captains:
        await send_notification(context, captain, CrewDisbandWarningNotification())


def get_inactive_captains() -> list[User]:
    """
    Find captains of a Crew that have not been active since the last bounty reset
    :return: The inactive captains
    """
    from src.service.bounty_service import get_previous_bounty_reset_time

    previous_bounty_reset: datetime = get_previous_bounty_reset_time()
    inactive_captains = User.select().where(
        (User.crew_role == CrewRole.CAPTAIN)
        & (User.last_system_interaction_date < previous_bounty_reset)
        & (User.is_admin == False)
        & (User.is_exempt_from_global_leaderboard_requirements == False)
    )

    return inactive_captains


def add_to_crew_chest(user: User, amount: int) -> None:
    """
    Adds to the crew chest

    :param user: The user
    :param amount: The amount
    :return: None
    """

    if not user.is_crew_member():
        raise ValueError("User is not a crew member")

    crew: Crew = user.crew
    crew.chest_amount += amount
    crew.total_gained_chest_amount += amount
    crew.save()

    # Save contribution
    contribution: CrewMemberChestContribution = CrewMemberChestContribution.get_or_none(
        (CrewMemberChestContribution.crew == crew) & (CrewMemberChestContribution.user == user)
    )

    if contribution is None:
        contribution = CrewMemberChestContribution()
        contribution.crew = crew
        contribution.user = user

    contribution.amount += amount
    contribution.last_contribution_date = datetime.now()
    contribution.save()


def get_crew_abilities_text(
    crew: Crew = None,
    active_abilities: list[CrewAbility] = None,
    add_duration: bool = False,
    add_emoji: bool = False,
):
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
        emoji_text = Emoji.LOG_POSITIVE.value if add_emoji else ""
        for ability in active_abilities:
            text = phrases.CREW_ABILITY_ITEM_TEXT.format(
                emoji_text, ability.get_description(), ability.get_value_with_sign()
            )
            if add_duration:
                text += phrases.CREW_ABILITY_ITEM_TEXT_DURATION.format(
                    get_remaining_duration(ability.expiration_date)
                )

            active_abilities_text_list.append(text)

        abilities_text = ("\n" if add_duration else "").join(active_abilities_text_list)

    return abilities_text


async def notify_crew_members(
    context: ContextTypes.DEFAULT_TYPE,
    crew: Crew,
    notification: Notification,
    exclude_user: User = None,
) -> None:
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
            await send_notification(context, member, notification)


async def add_crew_ability(
    context: ContextTypes.DEFAULT_TYPE,
    crew: Crew,
    ability_type: DevilFruitAbilityType,
    ability_value: int,
    acquired_method: CrewAbilityAcquiredMethod,
    acquired_user: User,
) -> None:
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

    now = datetime.now()
    ability: CrewAbility = CrewAbility()
    ability.crew = crew
    ability.ability_type = ability_type
    ability.value = ability_value
    ability.acquired_method = acquired_method
    ability.acquired_user = acquired_user
    ability.acquired_date = now
    ability.expiration_date = get_datetime_in_future_days(
        Env.CREW_ABILITY_DURATION_DAYS.get_int(), start_time=now
    )
    ability.save()

    # Notify crew members
    await notify_crew_members(
        context, crew, CrewAbilityActivatedNotification(ability), exclude_user=acquired_user
    )


def add_powerup(
    crew: Crew, acquired_user: User, reason: CrewChestSpendingReason, price: int
) -> None:
    """
    Adds a powerup to a crew

    :param crew: The crew
    :param acquired_user: The user who acquired the powerup
    :param reason: The reason
    :param price: The price
    :return: None
    """

    # Level up
    if reason is CrewChestSpendingReason.LEVEL_UP:
        crew.level_up()

        # Reduce tax bracket
        for member in crew.get_members():
            member.reduce_tax_bracket()

    crew.chest_amount -= price
    crew.save()

    # Add spending record
    add_chest_spending_record(crew, price, reason, acquired_user)


def add_chest_spending_record(
    crew: Crew, amount: int, reason: CrewChestSpendingReason, by_user: User, to_user: User = None
) -> None:
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


def get_crew_overview_text(crew: Crew, user: User, from_search: bool = True) -> str:
    """
    Get the crew overview text

    :param crew: The crew
    :param user: The user
    :param from_search: Whether the crew overview is from search, if so show basic info only
    :return: The crew overview text
    """
    from src.service.leaderboard_service import get_remaining_time_to_next_leaderboard

    # If from search
    active_abilities_count_text = ""

    # If not from search
    first_mate_text = ""
    treasure_chest_text = ""
    active_abilities_text = ""
    no_new_members_allowed_text = ""

    if from_search:
        if not crew.allow_view_in_search:
            return phrases.CREW_SEARCH_NOT_ALLOWED_TO_VIEW

        active_abilities_count_text = phrases.CREW_OVERVIEW_ACTIVE_ABILITIES_COUNT.format(
            len(crew.get_active_abilities()), crew.max_abilities
        )
    else:
        first_mate: User = crew.get_first_mate()
        if first_mate is not None:
            first_mate_text = phrases.CREW_OVERVIEW_FIRST_MATE.format(
                first_mate.get_markdown_mention()
            )

        treasure_chest_text = phrases.CREW_OVERVIEW_TREASURE_CHEST.format(
            get_belly_formatted(crew.chest_amount)
        )
        active_abilities_text = phrases.CREW_OVERVIEW_ACTIVE_ABILITIES.format(
            get_crew_abilities_text(crew=crew)
        )

        # No new members allowed
        if not crew.can_accept_new_members:
            no_new_members_allowed_text = phrases.CREW_OVERVIEW_NO_NEW_MEMBERS_ALLOWED.format(
                get_remaining_time_to_next_leaderboard()
            )

    captain: User = crew.get_captain()

    ot_text = phrases.CREW_OVERVIEW.format(
        crew.get_name_escaped(),
        crew.level,
        (
            crew.get_description_escaped()
            if crew.description is not None
            else phrases.CREW_OVERVIEW_DESCRIPTION_NOT_SET
        ),
        captain.get_markdown_mention(),
        first_mate_text,
        user.get_date_formatted(crew.creation_date),
        get_elapsed_duration(crew.creation_date),
        len(crew.get_members()),
        crew.max_members,
        active_abilities_count_text,
        treasure_chest_text,
        active_abilities_text,
        no_new_members_allowed_text,
    )

    return ot_text


def get_crew_name_with_deeplink(crew: Crew) -> str:
    """
    Get the crew name with deeplink

    :param crew: The crew
    :return: The crew name with deeplink
    """
    return phrases.CREW_NAME_WITH_LEVEL_DEEPLINK.format(
        crew.get_name_escaped(),
        get_deeplink(
            info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: crew.id},
            screen=Screen.PVT_CREW_SEARCH_DETAIL,
        ),
        crew.level,
    )
