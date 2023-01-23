from datetime import datetime

import resources.Environment as Env
from resources import phrases
from src.model.DevilFruit import DevilFruit
from src.model.DevilFruitAbility import DevilFruitAbility
from src.model.DevilFruitTrade import DevilFruitTrade
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.enums.devil_fruit.DevilFruitSource import DevilFruitSource
from src.model.enums.devil_fruit.DevilFruitStatus import DevilFruitStatus
from src.service.cron_service import get_datetime_in_future_days


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


def get_devil_fruit_abilities_text(devil_fruit: DevilFruit, add_header: bool = True) -> str:
    """
    Get devil fruit abilities text
    :param devil_fruit: The devil fruit
    :param add_header: Whether to add the header
    :return: The text
    """

    abilities: list[DevilFruitAbility] = get_devil_fruit_abilities(devil_fruit)

    abilities_text: str = phrases.DEVIL_FRUIT_ABILITY_TEXT if add_header else ""
    for ability in abilities:
        ability_type: DevilFruitAbilityType = DevilFruitAbilityType(ability.ability_type)

        abilities_text += phrases.DEVIL_FRUIT_ABILITY_TEXT_LINE.format(
            Emoji.LOG_POSITIVE, ability_type.get_description(), ability_type.get_sign(), ability.value)

    return abilities_text
