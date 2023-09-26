from telegram import Update, Message
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.model.BountyGift import BountyGift
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.BountyGiftStatus import BountyGiftStatus
from src.model.enums.Command import Command
from src.model.enums.Notification import BountyGiftReceivedNotification
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_amount_from_string, validate_amount, get_belly_formatted, get_transaction_tax
from src.service.devil_fruit_service import get_value
from src.service.math_service import get_value_from_percentage
from src.service.message_service import full_message_send, get_yes_no_keyboard
from src.service.notification_service import send_notification
from src.service.user_service import user_is_boss


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, inbound_keyboard: Keyboard,
                 target_user: User, command: Command, group_chat: GroupChat) -> None:
    """
    Manage the Bounty gift screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :param target_user: The target user in case of a reply
    :param command: The command
    :param group_chat: The group chat
    :return: None
    """

    # Request send a gift
    if inbound_keyboard is None:
        await send_request(update, context, user, target_user, command, group_chat)
        return

    await keyboard_interaction(update, context, user, inbound_keyboard)


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE, sender: User, receiver: User,
                   command: Command = None,
                   bounty_gift: BountyGift = None) -> bool:
    """
    Validate the bounty gift request
    :param update: The update object
    :param context: The context object
    :param sender: The user that wants to send a bounty gift
    :param receiver: The user that wants to receive a bounty gift
    :param command: The command
    :param bounty_gift: The bounty gift object
    :return: True if the request is valid, False otherwise
    """

    # Command does not have wager amount
    if bounty_gift is None:
        if len(command.parameters) == 0:
            await full_message_send(context, phrases.BOUNTY_GIFT_NO_AMOUNT, update=update, add_delete_button=True)
            return False

        # Wager basic validation, error message is sent by validate_wager
        if not await validate_amount(update, context, sender, command.parameters[0],
                                     Env.BOUNTY_GIFT_MIN_AMOUNT.get_int()):
            return False

    # Get the amounts
    amount, tax_percentage, tax_amount, total_amount = await get_amounts(sender, receiver, command, bounty_gift)

    # Sender does not have enough bounty
    if sender.bounty < total_amount:
        # Get max gift amount
        max_amount = int(sender.bounty / (1 + (tax_percentage / 100)))
        ot_text = phrases.BOUNTY_GIFT_NOT_ENOUGH_BOUNTY.format(get_belly_formatted(sender.bounty),
                                                               get_belly_formatted(amount),
                                                               get_belly_formatted(tax_amount),
                                                               tax_percentage,
                                                               get_belly_formatted(total_amount),
                                                               get_belly_formatted(max_amount))
        await full_message_send(context, ot_text, update=update, add_delete_button=True)
        return False

    return True


async def send_request(update: Update, context: ContextTypes.DEFAULT_TYPE, sender: User, receiver: User,
                       command: Command, group_chat: GroupChat) -> None:
    """
    Send request to send a bounty gift
    :param update: The update object
    :param context: The context object
    :param sender: The user that wants to send a bounty gift
    :param receiver: The user to send the bounty gift to
    :param command: The command
    :param group_chat: The group chat
    :return: None
    """

    if not await validate(update, context, sender, receiver, command):
        return

    # Get the amounts
    amount, tax_percentage, tax_amount, total_amount = await get_amounts(sender, receiver, command)

    ot_text = phrases.BOUNTY_GIFT_REQUEST.format(get_belly_formatted(amount), receiver.get_markdown_mention(),
                                                 get_belly_formatted(tax_amount), tax_percentage,
                                                 get_belly_formatted(total_amount))

    # Save
    bounty_gift: BountyGift = BountyGift()
    bounty_gift.sender = sender
    bounty_gift.receiver = receiver
    bounty_gift.amount = amount
    bounty_gift.tax_percentage = tax_percentage
    bounty_gift.group_chat = group_chat
    bounty_gift.save()

    # Keyboard
    # Delete button can't be replaced by add_delete_button because bounty_gift have to be deleted
    inline_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(sender, screen=Screen.GRP_BOUNTY_GIFT,
                                                                 primary_key=bounty_gift.id)]

    message: Message = await full_message_send(context, ot_text, update=update, keyboard=inline_keyboard)
    bounty_gift.message_id = message.message_id
    bounty_gift.save()


async def transaction_is_tax_free(sender: User, receiver: User) -> bool:
    """
    Check if the transaction is tax-free
    :param sender: The sender
    :param receiver: The receiver
    :return: True if the transaction is tax-free, False otherwise
    """

    # Sender and receiver are in the same crew, no tax
    if sender.in_same_crew(receiver):
        return True

    # Sender is a boss, no tax
    if user_is_boss(sender):
        return True

    return False


async def get_amounts(sender: User, receiver: User, command: Command = None, bounty_gift: BountyGift = None
                      ) -> tuple[int, int, int, int]:
    """
    Get the amounts for a bounty gift
    :param sender: The sender
    :param receiver: The receiver
    :param command: The command
    :param bounty_gift: The bounty gift object
    :return: The amount, tax percentage, tax amount, total amount
    """

    if bounty_gift is None:
        amount = get_amount_from_string(command.parameters[0], sender)
    else:
        amount = bounty_gift.amount

    tax_percentage = get_transaction_tax(sender, receiver, sender.bounty_gift_tax)

    # Apply Devil Fruit ability
    if tax_percentage > 0:
        tax_percentage = get_value(sender, DevilFruitAbilityType.TAX, tax_percentage)

    # Parse to int if tax does not have a decimal
    if float(tax_percentage).is_integer():
        tax_percentage = int(tax_percentage)

    tax_amount = int(get_value_from_percentage(amount, tax_percentage))
    total_amount = amount + tax_amount

    return amount, tax_percentage, tax_amount, total_amount


async def keyboard_interaction(update: Update, context: ContextTypes.DEFAULT_TYPE, sender: User,
                               inbound_keyboard: Keyboard) -> None:
    """
    Keyboard interaction
    :param update: The update object
    :param context: The context object
    :param sender: The user that wants to send a bounty gift
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    bounty_gift: BountyGift = BountyGift.get_by_id(inbound_keyboard.get(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY))

    # User cancelled the request
    if not inbound_keyboard.info[ReservedKeyboardKeys.CONFIRM]:
        bounty_gift.delete_instance()
        await full_message_send(context, phrases.BOUNTY_GIFT_CANCELLED, update=update, add_delete_button=True)
        return

    receiver: User = bounty_gift.receiver
    if not await validate(update, context, sender, receiver, bounty_gift=bounty_gift):
        bounty_gift.delete_instance()
        return

    # Get the amounts
    amount, tax_percentage, tax_amount, total_amount = await get_amounts(sender, receiver,
                                                                         bounty_gift=bounty_gift)

    bounty_gift.amount = amount
    bounty_gift.tax_percentage = tax_percentage
    bounty_gift.status = BountyGiftStatus.CONFIRMED
    bounty_gift.save()

    # Update sender
    sender.bounty -= total_amount

    sender.bounty_gift_tax += Env.BOUNTY_GIFT_TAX_INCREASE.get_int()

    # Update receiver
    receiver.bounty += amount
    receiver.save()

    # Send message
    ot_text = phrases.BOUNTY_GIFT_CONFIRMED.format(get_belly_formatted(amount), receiver.get_markdown_mention(),
                                                   get_belly_formatted(tax_amount), tax_percentage,
                                                   get_belly_formatted(total_amount))
    await full_message_send(context, ot_text, update=update, add_delete_button=True)

    # Send notification to receiver
    notification = BountyGiftReceivedNotification(sender, amount)
    await send_notification(context, receiver, notification)
