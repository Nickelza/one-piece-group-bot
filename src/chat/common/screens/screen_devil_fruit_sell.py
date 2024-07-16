from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.model.DevilFruit import DevilFruit
from src.model.DevilFruitTrade import DevilFruitTrade
from src.model.User import User
from src.model.enums.devil_fruit.DevilFruitSource import DevilFruitSource
from src.model.enums.devil_fruit.DevilFruitStatus import DevilFruitStatus
from src.model.enums.income_tax.IncomeTaxEventType import IncomeTaxEventType
from src.model.error.CustomException import DevilFruitTradeValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import add_or_remove_bounty
from src.service.devil_fruit_service import give_devil_fruit_to_user, get_recap_text
from src.service.message_service import full_message_send
from src.utils.string_utils import get_belly_formatted


async def validate_trade(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    devil_fruit: DevilFruit,
    seller: User,
    add_delete_button: bool = False,
    inbound_keyboard: Keyboard = None,
    show_alert: bool = False,
) -> bool:
    """
    Validate the trade
    :param update: The update object
    :param context: The context object
    :param devil_fruit: The Devil Fruit
    :param seller: The seller
    :param add_delete_button: Whether to add the delete button
    :param inbound_keyboard: The inbound keyboard
    :param show_alert: Whether to show an alert
    :return: True if the trade is valid, False otherwise
    """
    try:
        # Seller no longer owns the Devil Fruit
        if devil_fruit.owner != seller:
            raise DevilFruitTradeValidationException(
                phrases.DEVIL_FRUIT_SELL_NO_LONGER_OWN.format(seller.get_markdown_mention())
            )

        # Devil Fruit is no longer sellable
        if devil_fruit.status != DevilFruitStatus.COLLECTED:
            raise DevilFruitTradeValidationException(phrases.DEVIL_FRUIT_SELL_NO_LONGER_SELLABLE)

    except DevilFruitTradeValidationException as e:
        await full_message_send(
            context,
            e.message,
            update=update,
            inbound_keyboard=inbound_keyboard,
            add_delete_button=add_delete_button,
            show_alert=show_alert,
        )
        return False

    return True


async def validate_buy(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    buyer: User,
    devil_fruit_trade: DevilFruitTrade,
) -> bool:
    """
    Validate the buy action
    :param update: The update object
    :param context: The context object
    :param buyer: The buyer
    :param devil_fruit_trade: The Devil Fruit trade
    :return: True if the buy is valid, False otherwise
    """

    try:
        # Buyer does not have enough belly
        if buyer.bounty < devil_fruit_trade.price:
            raise DevilFruitTradeValidationException(phrases.DEVIL_FRUIT_SELL_BUY_NOT_ENOUGH_BELLY)

        # Buyer is the seller
        if devil_fruit_trade.giver == buyer:
            raise DevilFruitTradeValidationException(phrases.DEVIL_FRUIT_SELL_BUY_CANNOT_BUY_OWN)

    except DevilFruitTradeValidationException as e:
        await full_message_send(
            context, e.message, update=update, answer_callback=True, show_alert=True
        )
        return False

    return True


async def buy(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    buyer: User,
    devil_fruit_trade: DevilFruitTrade,
    devil_fruit: DevilFruit,
    source: DevilFruitSource,
) -> str | None:
    """
    Buy the Devil Fruit
    :param update: The update object
    :param context: The context object
    :param buyer: The buyer
    :param devil_fruit_trade: The Devil Fruit trade
    :param devil_fruit: The Devil Fruit
    :param source: The source
    :return: The completed buy text
    """

    # Validate the buy
    if not await validate_buy(update, context, buyer, devil_fruit_trade):
        return

    give_devil_fruit_to_user(devil_fruit, buyer, source, devil_fruit_trade=devil_fruit_trade)

    # Remove the belly from the buyer
    await add_or_remove_bounty(buyer, devil_fruit_trade.price, add=False, update=update)
    buyer.save()

    # Add the belly to the seller
    await add_or_remove_bounty(
        devil_fruit_trade.giver,
        devil_fruit_trade.price,
        update=update,
        tax_event_type=IncomeTaxEventType.DEVIL_FRUIT_SELL,
        event_id=devil_fruit_trade.id,
        should_save=True,
    )

    seller: User = devil_fruit_trade.giver

    return phrases.DEVIL_FRUIT_SELL_BUY_SUCCESS.format(
        buyer.get_you_markdown_mention(),
        seller.get_markdown_mention(),
        get_recap_text(devil_fruit),
        get_belly_formatted(devil_fruit_trade.price),
    )
