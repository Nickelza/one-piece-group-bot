from enum import StrEnum, IntEnum

from peewee import DoesNotExist
from telegram import Update, Message
from telegram.ext import ContextTypes

from resources import phrases
from src.model.DevilFruit import DevilFruit
from src.model.DevilFruitTrade import DevilFruitTrade
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.Command import Command
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitSource import DevilFruitSource
from src.model.enums.devil_fruit.DevilFruitStatus import DevilFruitStatus
from src.model.enums.income_tax.IncomeTaxEventType import IncomeTaxEventType
from src.model.error.CustomException import (
    DevilFruitTradeValidationException,
)
from src.model.error.PrivateChatError import PrivateChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import (
    validate_amount,
    get_amount_from_string,
    add_or_remove_bounty,
)
from src.service.devil_fruit_service import give_devil_fruit_to_user, get_recap_text
from src.service.message_service import full_message_send
from src.service.string_service import get_belly_formatted


class DevilFruitSellReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    ITEM_ID = "a"
    DEVIL_FRUIT_ID = "b"
    STEP = "c"


class Step(IntEnum):
    """
    The steps for this screen
    """

    SELECT_FRUIT = 0
    BUY = 1


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    inbound_keyboard: Keyboard,
    target_user: User,
    command: Command,
    group_chat: GroupChat,
) -> None:
    """
    Manage the Devil Fruit sell screen
    :param update: The update object
    :param context: The context object
    :param user: The user
    :param inbound_keyboard: The inbound keyboard
    :param target_user: The target user
    :param command: The command
    :param group_chat: The group chat
    :return: None
    """

    if inbound_keyboard is None:  # Send the list of Devil Fruits and save trade
        return await send_list_of_fruits(update, context, user, target_user, command, group_chat)

    # Get the Devil Fruit trade
    try:
        devil_fruit_trade: DevilFruitTrade = DevilFruitTrade.get(
            DevilFruitTrade.id == inbound_keyboard.get(DevilFruitSellReservedKeys.ITEM_ID)
        )
    except DoesNotExist:
        # Custom exception to avoid logging
        raise PrivateChatException(text=phrases.ITEM_NOT_FOUND)

    if devil_fruit_trade.devil_fruit is None:
        devil_fruit_trade.devil_fruit = DevilFruit.get(
            DevilFruit.id == inbound_keyboard.get(DevilFruitSellReservedKeys.DEVIL_FRUIT_ID)
        )
        devil_fruit_trade.save()

    devil_fruit: DevilFruit = devil_fruit_trade.devil_fruit
    if not await validate_trade(
        update, context, devil_fruit, devil_fruit_trade.giver, add_delete_button=True
    ):
        devil_fruit_trade.delete_instance()
        return

    match inbound_keyboard.get(DevilFruitSellReservedKeys.STEP):
        case Step.SELECT_FRUIT:
            return await send_sell_proposal(update, context, user, devil_fruit_trade, devil_fruit)

        case Step.BUY:
            ot_text = await buy(
                update, context, user, devil_fruit_trade, devil_fruit, DevilFruitSource.USER
            )
            if ot_text:
                # Add deeplink button
                info = {ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: devil_fruit.id}
                inline_keyboard: list[list[Keyboard]] = [[
                    Keyboard(
                        phrases.KEY_MANAGE,
                        screen=Screen.PVT_DEVIL_FRUIT_DETAIL,
                        info=info,
                        is_deeplink=True,
                    )
                ]]
                await full_message_send(
                    context,
                    ot_text,
                    update=update,
                    keyboard=inline_keyboard,
                    add_delete_button=True,
                )

        case _:
            raise ValueError(
                f"Invalid step: {inbound_keyboard.get(DevilFruitSellReservedKeys.STEP)}"
            )


async def validate_new_request(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, command: Command
) -> bool:
    """
    Validate a new request
    :param update: The update object
    :param context: The context object
    :param user: The user
    :param command: The command
    :return: True if the request is valid, False otherwise
    """

    try:
        # Command does not have sell amount
        if len(command.parameters) == 0:
            raise DevilFruitTradeValidationException(phrases.DEVIL_FRUIT_SELL_NO_AMOUNT)

        # Amount basic validation, error message is sent by validate_wager
        if not await validate_amount(
            update,
            context,
            user,
            command.parameters[0],
            should_validate_user_has_amount=False,
        ):
            raise DevilFruitTradeValidationException()

        # User has no Devil Fruits that can be sold
        sellable_devil_fruit: list[DevilFruit] = DevilFruit.get_or_none(
            DevilFruit.owner == user, DevilFruit.status == DevilFruitStatus.COLLECTED
        )
        if sellable_devil_fruit is None:
            raise DevilFruitTradeValidationException(phrases.DEVIL_FRUIT_SELL_NO_FRUITS)

    except DevilFruitTradeValidationException as e:
        if e.message is not None:
            await full_message_send(context, e.message, update=update, add_delete_button=True)
        return False

    return True


async def send_list_of_fruits(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    target_user: User,
    command: Command,
    group_chat: GroupChat,
) -> None:
    """
    Send the list of fruits
    :param update: The update object
    :param context: The context object
    :param user: The user
    :param target_user: The target user
    :param command: The command
    :param group_chat: The group chat
    :return: None
    """

    if not await validate_new_request(update, context, user, command):
        return

    # Save the trade
    trade: DevilFruitTrade = DevilFruitTrade()
    trade.giver = user
    trade.receiver = target_user
    trade.source = DevilFruitSource.USER
    trade.price = get_amount_from_string(command.parameters[0], user)
    trade.group_chat = group_chat
    trade.save()

    # Get list of sellable Devil Fruits
    sellable_devil_fruits: list[DevilFruit] = DevilFruit.select().where(
        DevilFruit.owner == user, DevilFruit.status == DevilFruitStatus.COLLECTED
    )

    # Create the keyboard
    outbound_keyboard: list[list[Keyboard]] = []
    for devil_fruit in sellable_devil_fruits:
        info = {
            DevilFruitSellReservedKeys.ITEM_ID: trade.id,
            DevilFruitSellReservedKeys.DEVIL_FRUIT_ID: devil_fruit.id,
            DevilFruitSellReservedKeys.STEP: Step.SELECT_FRUIT,
        }
        button: Keyboard = Keyboard(
            devil_fruit.get_full_name(), info=info, screen=Screen.GRP_DEVIL_FRUIT_SELL
        )
        outbound_keyboard.append([button])

    ot_text = phrases.DEVIL_FRUIT_SELL_SELECT_FRUIT

    # Send the message
    message: Message = await full_message_send(
        context, ot_text, update=update, keyboard=outbound_keyboard, add_delete_button=True
    )

    trade.message_id = message.id
    trade.save()


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


async def send_sell_proposal(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    devil_fruit_trade: DevilFruitTrade,
    devil_fruit: DevilFruit,
) -> None:
    """
    Send the sell proposal
    :param update: The update object
    :param context: The context object
    :param user: The user
    :param devil_fruit_trade: The Devil Fruit trade
    :param devil_fruit: The Devil Fruit
    :return: None
    """

    # Create the keyboard
    outbound_keyboard: list[list[Keyboard]] = []
    info = {
        DevilFruitSellReservedKeys.ITEM_ID: devil_fruit_trade.id,
        DevilFruitSellReservedKeys.DEVIL_FRUIT_ID: devil_fruit.id,
        DevilFruitSellReservedKeys.STEP: Step.BUY,
    }

    # Delete all pending trades of this fruit in the group
    DevilFruitTrade.delete_pending_trades_in_group(
        devil_fruit, devil_fruit_trade.group_chat, devil_fruit_trade.id
    )

    receiver: User = devil_fruit_trade.receiver

    if receiver is not None:
        only_authorized_users_can_interact = True
        authorized_users = [user, receiver]
    else:
        only_authorized_users_can_interact = False
        authorized_users = None

    button: Keyboard = Keyboard(
        phrases.GRP_KEY_DEVIL_FRUIT_BUY,
        info=info,
        screen=Screen.GRP_DEVIL_FRUIT_SELL,
        inherit_authorized_users=False,
        authorized_users=authorized_users,
        only_authorized_users_can_interact=only_authorized_users_can_interact,
    )

    outbound_keyboard.append([button])

    ot_text_addendum = (
        phrases.DEVIL_FRUIT_SELL_BUY_ONLY_BY_USER_ADDENDUM.format(receiver.get_markdown_mention())
        if receiver is not None
        else ""
    )

    ot_text = phrases.DEVIL_FRUIT_SELL_BUY.format(
        user.get_markdown_mention(),
        get_recap_text(devil_fruit),
        get_belly_formatted(devil_fruit_trade.price),
        ot_text_addendum,
    )

    await full_message_send(
        context, ot_text, update=update, keyboard=outbound_keyboard, add_delete_button=True
    )


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
