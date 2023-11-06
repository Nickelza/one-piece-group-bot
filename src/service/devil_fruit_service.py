import logging
from datetime import datetime

from telegram import Update, Message
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import resources.Environment as Env
from resources import phrases
from src.model.Crew import Crew
from src.model.DevilFruit import DevilFruit
from src.model.DevilFruitAbility import DevilFruitAbility
from src.model.DevilFruitTrade import DevilFruitTrade
from src.model.GroupChat import GroupChat
from src.model.Leaderboard import Leaderboard
from src.model.LeaderboardUser import LeaderboardUser
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.Notification import DevilFruitExpiredNotification, DevilFruitRevokeWarningNotification, \
    DevilFruitRevokeNotification
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType, Sign as DevilFruitAbilityTypeSign
from src.model.enums.devil_fruit.DevilFruitCategory import DevilFruitCategory
from src.model.enums.devil_fruit.DevilFruitSource import DevilFruitSource
from src.model.enums.devil_fruit.DevilFruitStatus import DevilFruitStatus
from src.model.enums.devil_fruit.DevilFruitTradeStatus import DevilFruitTradeStatus
from src.model.error.CustomException import DevilFruitValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.date_service import get_datetime_in_future_days, get_random_time_between_by_cron, \
    get_random_time_between_by_hours, get_datetime_in_future_hours, get_remaining_time_in_minutes, \
    datetime_is_before
from src.service.math_service import add_percentage_to_value, subtract_percentage_from_value, get_random_win, \
    get_cumulative_percentage_sum, format_percentage_value
from src.service.message_service import log_error, escape_valid_markdown_chars, full_media_send
from src.service.notification_service import send_notification


def give_devil_fruit_to_user(devil_fruit: DevilFruit, receiver: User, source: DevilFruitSource, reason: str = None,
                             devil_fruit_trade: DevilFruitTrade = None) -> None:
    """
    Give a devil fruit to a user
    :param devil_fruit: The devil fruit
    :param receiver: The receiver
    :param source: The source
    :param reason: The reason
    :param devil_fruit_trade: The devil fruit trade already created
    """

    # Make sure the devil fruit is not already owned by someone
    if devil_fruit.owner and source is not DevilFruitSource.USER:
        owner: User = devil_fruit.owner
        raise DevilFruitValidationException(
            f"Devil fruit {devil_fruit.get_full_name()} is already owned by {owner.tg_user_id}")

    # If source is ADMIN, a reason must be provided
    if source is DevilFruitSource.ADMIN and not reason:
        raise DevilFruitValidationException("A reason must be provided when giving a devil fruit to a user via ADMIN")

    # Save new owner
    devil_fruit.owner = receiver
    devil_fruit.status = DevilFruitStatus.COLLECTED

    # Add collection and expiration date if from ADMIN or BOT
    if source is DevilFruitSource.ADMIN or source is DevilFruitSource.BOT:
        devil_fruit.expiration_date = get_datetime_in_future_days(Env.DEVIL_FRUIT_EXPIRATION_DAYS.get_int())
        devil_fruit.collection_date = datetime.now()

    devil_fruit.save()

    # Save trade
    if devil_fruit_trade is None:
        devil_fruit_trade: DevilFruitTrade = DevilFruitTrade()

    devil_fruit_trade.devil_fruit = devil_fruit
    devil_fruit_trade.receiver = receiver
    devil_fruit_trade.source = source
    devil_fruit_trade.reason = reason
    devil_fruit_trade.status = DevilFruitTradeStatus.COMPLETED
    devil_fruit_trade.save()

    # Delete all pending trades
    DevilFruitTrade.delete().where(DevilFruitTrade.devil_fruit == devil_fruit,
                                   DevilFruitTrade.status == DevilFruitTradeStatus.PENDING).execute()


def get_devil_fruit_abilities(devil_fruit: DevilFruit) -> list[DevilFruitAbility]:
    """
    Get the devil fruit abilities
    :param devil_fruit: The devil fruit
    :return: The abilities
    """
    return DevilFruitAbility.select().where(DevilFruitAbility.devil_fruit == devil_fruit)


def get_devil_fruit_abilities_text(devil_fruit: DevilFruit, add_header: bool = True, always_show_abilities=True) -> str:
    """
    Get devil fruit abilities text
    :param devil_fruit: The devil fruit
    :param add_header: Whether to add the header
    :param always_show_abilities: Whether to always show the abilities, even if the Devil Fruit has never been eaten
    :return: The text
    """

    abilities: list[DevilFruitAbility] = get_devil_fruit_abilities(devil_fruit)

    abilities_text: str = phrases.DEVIL_FRUIT_ABILITY_TEXT if add_header else ""

    if always_show_abilities or devil_fruit.should_show_abilities:
        for ability in abilities:
            ability_type: DevilFruitAbilityType = DevilFruitAbilityType(ability.ability_type)

            abilities_text += phrases.DEVIL_FRUIT_ABILITY_TEXT_LINE.format(
                Emoji.LOG_POSITIVE, ability_type.get_description(), ability_type.get_sign(), ability.value)
    else:
        abilities_text += phrases.DEVIL_FRUIT_ABILITY_UNKNOWN

    return abilities_text


def get_devil_fruits_in_circulation(category: DevilFruitCategory = None) -> list[DevilFruit]:
    """
    Get all devil fruits in circulation
    :param category: The category (optional)
    :return: The devil fruits
    """

    query = DevilFruit.select().where(DevilFruit.status.in_(DevilFruitStatus.get_released_statuses()))
    if category:
        query = query.where(DevilFruit.category == category)

    return list(query)


def should_release_devil_fruit() -> bool:
    """
    Checks if a Devil Fruit should be released based on the number of Devil Fruits in circulation and the number of
    active users
    :return: Whether a Devil Fruit should be released
    """

    # Get count of all devil fruits in circulation
    devil_fruits_in_circulation_count = len(get_devil_fruits_in_circulation())
    # Get count of active users
    active_users_count = len(User.get_active_interactive_users())

    if active_users_count == 0:
        return False

    max_devil_fruits_in_circulation = int(
        active_users_count / Env.DEVIL_FRUIT_MIN_ACTIVE_USERS_PER_DEVIL_FRUIT.get_int())

    return devil_fruits_in_circulation_count < max_devil_fruits_in_circulation


async def schedule_devil_fruit_release(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Schedule devil fruit release
    :param context: The context
    """

    if not should_release_devil_fruit():
        return

    # Get all regular zoans in circulation count
    active_regular_zoans: int = len(get_devil_fruits_in_circulation(category=DevilFruitCategory.ZOAN))
    # Get all ancient zoans in circulation count
    active_ancient_zoans: int = len(get_devil_fruits_in_circulation(category=DevilFruitCategory.ANCIENT_ZOAN))

    # Check if we should release a regular zoan or an ancient zoan based on the ratio
    try:
        current_ratio: int = int(active_regular_zoans / active_ancient_zoans)
        category: DevilFruitCategory = (DevilFruitCategory.ZOAN
                                        if current_ratio < Env.DEVIL_FRUIT_REGULAR_ZOAN_TO_ANCIENT_ZOAN_RATIO.get_int()
                                        else DevilFruitCategory.ANCIENT_ZOAN)
    except ZeroDivisionError:
        category = DevilFruitCategory.ZOAN

    # Get a fruit to release
    devil_fruit: DevilFruit = (DevilFruit.select()
                               .where((DevilFruit.status == DevilFruitStatus.ENABLED)
                                      & (DevilFruit.category == category))
                               .order_by(DevilFruit.id.asc())
                               .get_or_none())

    # If there are no devil fruits to release, send error message to admin chat
    if not devil_fruit:
        ot_text = phrases.NO_DEVIL_FRUIT_TO_SCHEDULE.format(category.get_description())
        await log_error(context, ot_text)
        logging.error(ot_text)
        return

    set_devil_fruit_release_date(devil_fruit, is_new_release=True)


async def release_devil_fruit_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User,
                                      group_chat: GroupChat) -> None:
    """
    Release a Devil Fruit to a user
    :param update: The update
    :param context: The context
    :param user: The user
    :param group_chat: The group chat
    :return: None
    """

    from src.chat.manage_message import init
    from src.service.bounty_service import get_next_bounty_reset_time

    db = init()

    if not datetime_is_before(user.devil_fruit_collection_cooldown_end_date):
        return

    with db.atomic() as transaction:
        # Check if there are any Devil Fruits to release, lock the row
        devil_fruit: DevilFruit = (DevilFruit.select()
                                   .where(DevilFruit.status == DevilFruitStatus.SCHEDULED)
                                   .for_update()
                                   .order_by(DevilFruit.release_date.asc())
                                   .get_or_none())

        if not devil_fruit:
            return

        minutes_to_release: int = get_remaining_time_in_minutes(devil_fruit.release_date)

        # Probability of releasing the Devil Fruit
        try:
            probability: float = (1 / minutes_to_release) * 100
        except ZeroDivisionError:
            probability = 100

        if not get_random_win(probability):
            user.devil_fruit_collection_cooldown_end_date = get_datetime_in_future_hours(
                Env.DEVIL_FRUIT_COLLECT_COOLDOWN_DURATION.get_int())
            return

        # Release the Devil Fruit to the user
        text = phrases.DEVIL_FRUIT_RELEASE_MESSAGE_INFO.format(
            user.get_markdown_mention(),
            escape_valid_markdown_chars(devil_fruit.get_full_name()),
            DevilFruitCategory(devil_fruit.category).get_description(),
            get_devil_fruit_abilities_text(devil_fruit, always_show_abilities=False))

        # Add deeplink button
        info = {ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: devil_fruit.id}
        inline_keyboard: list[list[Keyboard]] = [[Keyboard(phrases.KEY_MANAGE, screen=Screen.PVT_DEVIL_FRUIT_DETAIL,
                                                           info=info, is_deeplink=True)]]

        try:
            # Send release message
            message: Message = await full_media_send(
                context, saved_media_name=SavedMediaName.DEVIL_FRUIT_NEW, caption=text, keyboard=inline_keyboard,
                update=update, new_message=True, quote_if_group=False)

            devil_fruit.release_group_chat = group_chat
            devil_fruit.release_message_id = message.message_id

            give_devil_fruit_to_user(devil_fruit, user, DevilFruitSource.BOT)
            user.devil_fruit_collection_cooldown_end_date = get_next_bounty_reset_time()
        except (TelegramError, DevilFruitValidationException) as e:
            transaction.rollback()
            logging.error(f"Error giving devil fruit to user {user.tg_user_id}: {e}")


def set_devil_fruit_release_date(devil_fruit: DevilFruit, is_new_release: bool = False) -> None:
    """
    Set the release date of a devil fruit
    :param devil_fruit: The devil fruit
    :param is_new_release: Whether this is a new release
    :return: None
    """

    if not should_release_devil_fruit():
        devil_fruit.status = DevilFruitStatus.ENABLED
        devil_fruit.save()
        return

    # If it's a new release, set the release date to random time between now and next release
    if is_new_release:
        release_date = get_random_time_between_by_cron(Env.CRON_SCHEDULE_DEVIL_FRUIT_ZOAN_RELEASE.get())
    else:  # If it's a re-release, set the release date to random time between now and next n hours
        release_date = get_random_time_between_by_hours(Env.DEVIL_FRUIT_RESPAWN_HOURS.get_int())

    devil_fruit.owner = None
    devil_fruit.eaten_date = None
    devil_fruit.expiration_date = None
    devil_fruit.collection_date = None
    devil_fruit.release_date = release_date
    devil_fruit.release_message_id = None
    devil_fruit.status = DevilFruitStatus.SCHEDULED
    devil_fruit.save()


async def respawn_devil_fruit(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Respawn Devil Fruit
    :param context: The context
    :return: None
    """

    # Get all Devil Fruits that have expired and have not been eaten yet
    devil_fruits: list[DevilFruit] = (DevilFruit.select()
                                      .where((DevilFruit.status == DevilFruitStatus.COLLECTED)
                                             & (DevilFruit.expiration_date <= datetime.now())))
    for devil_fruit in devil_fruits:
        # Release
        owner: User = devil_fruit.owner
        set_devil_fruit_release_date(devil_fruit)

        # Send notification to owner
        notification = DevilFruitExpiredNotification(devil_fruit)
        await send_notification(context, owner, notification)


def get_ability_value(user: User, ability_type: DevilFruitAbilityType, value: float,
                      add_to_value: bool = False) -> float:
    """
    Given a value, gets the updated value if user has eaten a Devil Fruit that modifies it
    :param user: The user
    :param ability_type: The ability type
    :param value: The value
    :param add_to_value: Whether to add to the value
    :return: The value
    """

    abilities: list[DevilFruitAbility] = []

    # Get ability from a Devil Fruit eaten by user that has the ability
    devil_fruit_ability: DevilFruitAbility = DevilFruitAbility.get_user_ability(user, ability_type)
    if devil_fruit_ability is not None:
        abilities.append(devil_fruit_ability)

    # Get ability from user's crew abilities
    if user.is_crew_member():
        crew: Crew = user.crew
        abilities.extend(crew.get_active_ability(ability_type))

    if len(abilities) == 0:
        return value

    ability_type_sign: DevilFruitAbilityTypeSign = ability_type.get_sign()
    ability_value = format_percentage_value(get_cumulative_percentage_sum([ability.value for ability in abilities]))

    # Positive sign
    if ability_type_sign == DevilFruitAbilityTypeSign.POSITIVE:
        if add_to_value:
            return value + ability_value
        else:
            return add_percentage_to_value(value, ability_value)

    # Negative sign
    if add_to_value:
        return value - ability_value

    return subtract_percentage_from_value(value, ability_value)


def get_ability_adjusted_datetime(user: User, ability_type: DevilFruitAbilityType, hours: int) -> int:
    """
    Given a value, get the updated datetime if user has eaten a Devil Fruit that modifies it
    :param user: The user
    :param ability_type: The ability type
    :param hours: The hours
    :return: The value
    """

    new_hours: float = get_ability_value(user, ability_type, hours)
    return get_datetime_in_future_hours(new_hours)


def user_has_eaten_devil_fruit(user: User) -> bool:
    """
    Check if user has eaten a Devil Fruit
    :param user: The user
    :return: Whether user has eaten a Devil Fruit
    """

    return (DevilFruit.select()
            .where((DevilFruit.owner == user) & (DevilFruit.status == DevilFruitStatus.EATEN))
            .exists())


async def warn_inactive_users_with_eaten_devil_fruit(context: ContextTypes.DEFAULT_TYPE, users: list[User] = None
                                                     ) -> None:
    """
    Warn inactive users with eaten Devil Fruits

    :param context: The context object
    :param users: The users to warn. If provided, it will only warn these users, else it will warn all inactive users
    :return: None
    """

    inactive_users_devil_fruits = get_inactive_users_with_eaten_devil_fruits(
        Env.DEVIL_FRUIT_MAINTAIN_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int() - 1)

    for devil_fruit in inactive_users_devil_fruits:
        if users is None or (users is not None and devil_fruit.owner in users):
            await send_notification(
                context, devil_fruit.owner, DevilFruitRevokeWarningNotification(devil_fruit=devil_fruit))


def get_inactive_users_with_eaten_devil_fruits(latest_leaderboard_appearance: int) -> list[DevilFruit]:
    """
    Find Devil Fruits eaten by users that have not appeared in the latest N leaderboards

    :param latest_leaderboard_appearance: The latest leaderboard appearance
    :return: The inactive captains
    """

    latest_leaderboards: list[Leaderboard] = Leaderboard.get_latest_n(n=latest_leaderboard_appearance)

    # Eaten Devil Fruits with owners that have appeared in the latest N leaderboards
    query: list[DevilFruit] = (DevilFruit.select().distinct()
                               .join(User)
                               .join(LeaderboardUser)
                               .join(Leaderboard)
                               .where((DevilFruit.status == DevilFruitStatus.EATEN)
                                      & (Leaderboard.id.in_(latest_leaderboards)))
                               .execute())
    eaten_active_devil_fruits: list[DevilFruit] = list(query)

    # Inactive Devil Fruits
    # Have to first get inactive ones else, by using "not in", it will return records for previous leaderboards too
    # since the user might have been in a leaderboard before N, so it will not be in the latest N leaderboards
    # Exclude admins
    inactive_devil_fruits: list[DevilFruit] = (
        DevilFruit.select().distinct()
        .join(User)
        .where((DevilFruit.status == DevilFruitStatus.EATEN)
               & (User.is_admin == 0)
               & (DevilFruit.id.not_in([df.id for df in eaten_active_devil_fruits])))
        .execute())

    return list(inactive_devil_fruits)


async def revoke_devil_fruit_from_inactive_users(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Revoke Devil Fruits from inactive users

    :param context: The context object
    :return: None
    """

    inactive_users_devil_fruits = get_inactive_users_with_eaten_devil_fruits(
        Env.DEVIL_FRUIT_MAINTAIN_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int())

    for devil_fruit in inactive_users_devil_fruits:
        owner: User = devil_fruit.owner
        # Revoke
        set_devil_fruit_release_date(devil_fruit)

        # Send notification to owner
        await send_notification(context, owner, DevilFruitRevokeNotification(devil_fruit=devil_fruit))
