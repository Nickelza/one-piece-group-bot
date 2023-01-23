from resources import phrases
from src.model.DevilFruit import DevilFruit
from src.model.DevilFruitAbility import DevilFruitAbility
from src.model.DevilFruitTrade import DevilFruitTrade
from src.model.User import User
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.enums.devil_fruit.DevilFruitSource import DevilFruitSource
from src.model.enums.devil_fruit.DevilFruitStatus import DevilFruitStatus


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


def get_devil_fruit_abilities_text(devil_fruit: DevilFruit) -> str:
    """
    Get devil fruit abilities text

    :param devil_fruit: The devil fruit
    :return: The text
    """

    abilities: list[DevilFruitAbility] = get_devil_fruit_abilities(devil_fruit)

    abilities_text: str = phrases.DEVIL_FRUIT_ABILITY_TEXT
    for ability in abilities:
        ability_type: DevilFruitAbilityType = DevilFruitAbilityType(ability.ability_type)

        abilities_text += phrases.DEVIL_FRUIT_ABILITY_TEXT_LINE.format(
            ability_type.get_description(), ability_type.get_sign(), ability.value)

    return abilities_text
