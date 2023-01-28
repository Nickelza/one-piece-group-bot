import logging
import random
from datetime import datetime, timedelta

from telegram import Message
from telegram.ext import ContextTypes

import resources.Environment as Env
from resources import phrases
from src.model.DevilFruit import DevilFruit
from src.model.DevilFruitAbility import DevilFruitAbility
from src.model.DevilFruitTrade import DevilFruitTrade
from src.model.Group import Group
from src.model.Leaderboard import Leaderboard
from src.model.LeaderboardUser import LeaderboardUser
from src.model.Topic import Topic
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.Feature import Feature
from src.model.enums.Notification import DevilFruitExpiredNotification, DevilFruitRevokeWarningNotification, \
    DevilFruitRevokeNotification
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType, Sign as DevilFruitAbilityTypeSign
from src.model.enums.devil_fruit.DevilFruitSource import DevilFruitSource
from src.model.enums.devil_fruit.DevilFruitStatus import DevilFruitStatus
from src.model.pojo.Keyboard import Keyboard
from src.service.cron_service import get_datetime_in_future_days, get_random_time_between_by_cron, \
    get_random_time_between_by_hours, get_datetime_in_future_hours
from src.service.group_service import get_main_group, get_topics_with_feature_enabled
from src.service.math_service import add_percentage_to_value, subtract_percentage_from_value
from src.service.message_service import send_admin_error, escape_valid_markdown_chars, full_message_send, delete_message
from src.service.notification_service import send_notification


def give_devil_fruit_to_user(devil_fruit: DevilFruit, receiver: User, source: DevilFruitSource, giver: User = None,
                             reason: str = None, price: int = None) -> None:
    """
    Give a devil fruit to a user
    :param devil_fruit: The devil fruit
    :param receiver: The receiver
    :param source: The source
    :param giver: The giver
    :param reason: The reason
    :param price: The price, in case of trade between users
    """

    # Make sure the devil fruit is not already owned by someone
    if devil_fruit.owner:
        owner: User = devil_fruit.owner
        raise Exception(f"Devil fruit {devil_fruit.get_full_name()} is already owned by {owner.tg_user_id}")

    # If source is ADMIN, a reason must be provided
    if source is DevilFruitSource.ADMIN and not reason:
        raise Exception("A reason must be provided when giving a devil fruit to a user via ADMIN")

    # Save new owner
    devil_fruit.owner = receiver
    devil_fruit.status = DevilFruitStatus.COLLECTED

    # Add collection and expiration date if from ADMIN or BOT
    if source is DevilFruitSource.ADMIN or source is DevilFruitSource.BOT:
        devil_fruit.expiration_date = get_datetime_in_future_days(Env.DEVIL_FRUIT_EXPIRATION_DAYS.get_int())
        devil_fruit.collection_date = datetime.now()

    devil_fruit.save()

    # Save trade
    devil_fruit_trade: DevilFruitTrade = DevilFruitTrade()
    devil_fruit_trade.devil_fruit = devil_fruit
    devil_fruit_trade.giver = giver
    devil_fruit_trade.receiver = receiver
    devil_fruit_trade.price = price
    devil_fruit_trade.source = source
    devil_fruit_trade.reason = reason
    devil_fruit_trade.save()


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


async def schedule_devil_fruit_release(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Schedule devil fruit release
    :param context: The context
    """

    # Get all devil fruits that are not released yet
    devil_fruit: DevilFruit = (DevilFruit.select()
                               .where(DevilFruit.status == DevilFruitStatus.ENABLED)
                               .order_by(DevilFruit.id.asc())
                               .get_or_none())

    # If there are no devil fruits to release, send error message to admin chat
    if not devil_fruit:
        await send_admin_error(context, phrases.NO_DEVIL_FRUIT_TO_SCHEDULE)
        logging.error(phrases.NO_DEVIL_FRUIT_TO_SCHEDULE)
        return

    set_devil_fruit_release_date(devil_fruit, is_new_release=True)


async def release_scheduled_devil_fruit(context: ContextTypes.DEFAULT_TYPE, devil_fruit: DevilFruit = None) -> None:
    """
    Release Devil Fruits that are scheduled to be released
    :param context: The context
    :param devil_fruit: The Devil Fruit to release
    :return: None
    """
    from src.chat.group.screens.screen_devil_fruit_collect import DevilFruitCollectReservedKeys

    # Get all Devil Fruits that are scheduled to be released and have a release date in the past
    if not devil_fruit:
        devil_fruits: list[DevilFruit] = (DevilFruit.select()
                                          .where((DevilFruit.status == DevilFruitStatus.SCHEDULED)
                                                 & (DevilFruit.release_date <= datetime.now()))
                                          .order_by(DevilFruit.id.asc()))
    else:
        devil_fruits = [devil_fruit]

    for devil_fruit in devil_fruits:
        # Send to chat
        ot_text = phrases.DEVIL_FRUIT_RELEASED.format(
            escape_valid_markdown_chars(devil_fruit.get_full_name()),
            get_devil_fruit_abilities_text(devil_fruit, always_show_abilities=False))

        # Add collect button
        button_info = {DevilFruitCollectReservedKeys.DEVIL_FRUIT_ID: devil_fruit.id}
        inline_keyboard: list[list[Keyboard]] = [
            [Keyboard(phrases.GRP_KEY_DEVIL_FRUIT_COLLECT, screen=Screen.GRP_DEVIL_FRUIT_COLLECT, info=button_info)]]

        release_group: Group = devil_fruit.release_group
        release_topic: Topic = devil_fruit.release_topic
        message: Message = await full_message_send(
            context, ot_text, keyboard=inline_keyboard, chat_id=release_group.tg_group_id,
            topic_id=release_topic.tg_topic_id)

        devil_fruit.release_date = datetime.now()
        devil_fruit.release_message_id = message.message_id
        devil_fruit.status = DevilFruitStatus.RELEASED
        devil_fruit.save()


def set_devil_fruit_release_date(devil_fruit: DevilFruit, is_new_release: bool = False) -> None:
    """
    Set the release date of a devil fruit
    :param devil_fruit: The devil fruit
    :param is_new_release: Whether this is a new release
    :return: None
    """

    # If it's a new release, set the release date to random time between now and next release
    if is_new_release:
        release_date = get_random_time_between_by_cron(Env.CRON_SCHEDULE_DEVIL_FRUIT_RELEASE.get())
    else:  # If it's a re-release, set the release date to random time between now and next n hours
        release_date = get_random_time_between_by_hours(Env.DEVIL_FRUIT_RESPAWN_HOURS.get_int())

    devil_fruit.owner = None
    devil_fruit.eaten_date = None
    devil_fruit.expiration_date = None
    devil_fruit.collection_date = None
    set_devil_fruit_release_chat(devil_fruit)
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

    # Get all devil fruits that were released more than n hours ago and have not been collected yet
    limit_date: datetime = datetime.now() - timedelta(hours=Env.DEVIL_FRUIT_RESPAWN_HOURS.get_int())
    devil_fruits: list[DevilFruit] = (DevilFruit.select()
                                      .where((DevilFruit.status == DevilFruitStatus.RELEASED)
                                             & (DevilFruit.release_date <= limit_date)))
    for devil_fruit in devil_fruits:
        # Try to delete previous message
        await delete_message(
            context=context, chat_id=Env.OPD_GROUP_ID.get_int(), message_id=devil_fruit.release_message_id)

        # Release
        set_devil_fruit_release_chat(devil_fruit)
        await release_scheduled_devil_fruit(context, devil_fruit=devil_fruit)

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


def get_value(user: User, ability_type: DevilFruitAbilityType, value: int, add_to_value: bool = False) -> float:
    """
    Given a value, gets the updated value if user has eaten a Devil Fruit that modifies it
    :param user: The user
    :param ability_type: The ability type
    :param value: The value
    :param add_to_value: Whether to add to the value
    :return: The value
    """

    # Get Devil Fruit eaten by user that has the ability
    devil_fruit: DevilFruit = (DevilFruit.select()
                               .join(DevilFruitAbility)
                               .where((DevilFruit.owner == user)
                                      & (DevilFruit.status == DevilFruitStatus.EATEN)
                                      & (DevilFruitAbility.ability_type == ability_type))
                               .get_or_none())

    # User has no Devil Fruit with the ability
    if not devil_fruit:
        return value

    # Get ability
    ability: DevilFruitAbility = (DevilFruitAbility.select()
                                  .where((DevilFruitAbility.devil_fruit == devil_fruit)
                                         & (DevilFruitAbility.ability_type == ability_type))
                                  .get_or_none())

    ability_type_sign: DevilFruitAbilityTypeSign = ability_type.get_sign()

    # Positive sign
    if ability_type_sign == DevilFruitAbilityTypeSign.POSITIVE:
        if add_to_value:
            return value + ability.value
        else:
            return add_percentage_to_value(value, ability.value)

    # Negative sign
    if add_to_value:
        return value - ability.value

    return subtract_percentage_from_value(value, ability.value)


def get_datetime(user: User, ability_type: DevilFruitAbilityType, hours: int) -> int:
    """
    Given a value, get the updated datetime if user has eaten a Devil Fruit that modifies it
    :param user: The user
    :param ability_type: The ability type
    :param hours: The hours
    :return: The value
    """

    new_hours: float = get_value(user, ability_type, hours)
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


async def warn_inactive_users_with_eaten_devil_fruit(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Warn inactive users with eaten Devil Fruits

    :param context: The context object
    :return: None
    """

    inactive_users_devil_fruits = get_inactive_users_with_eaten_devil_fruits(
        Env.DEVIL_FRUIT_MAINTAIN_MIN_LATEST_LEADERBOARD_APPEARANCE.get_int() - 1)

    for devil_fruit in inactive_users_devil_fruits:
        await send_notification(
            context, devil_fruit.owner, DevilFruitRevokeWarningNotification(devil_fruit=devil_fruit))


def get_inactive_users_with_eaten_devil_fruits(latest_leaderboard_appearance: int) -> list[DevilFruit]:
    """
    Find Devil Fruits eaten by users that have not appeared in the latest N leaderboards

    :param latest_leaderboard_appearance: The latest leaderboard appearance
    :return: The inactive captains
    """

    # Latest N leaderboards
    query: list[Leaderboard] = (Leaderboard.select()
                                .order_by(Leaderboard.year.desc(), Leaderboard.week.desc())
                                .limit(latest_leaderboard_appearance)
                                .execute())
    latest_leaderboards: list[Leaderboard] = list(query)

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


def set_devil_fruit_release_chat(devil_fruit: DevilFruit) -> None:
    """
    Set Devil Fruit release group and topic

    :param devil_fruit: The Devil Fruit
    :return: None
    """

    # Get main group
    main_group: Group = get_main_group()
    devil_fruit.release_group = main_group

    # If is forum, get all topics where Devil Fruit feature is enabled
    if main_group.is_forum:
        enabled_topics: list[Topic] = get_topics_with_feature_enabled(Feature.DEVIL_FRUIT_APPEARANCE, main_group)
        if len(enabled_topics) > 0:
            devil_fruit.release_topic = random.choice(enabled_topics)

    # Object passed by reference, no need to return
