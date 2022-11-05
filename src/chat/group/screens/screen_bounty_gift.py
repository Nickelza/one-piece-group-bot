from telegram import Update, Message
from telegram.ext import CallbackContext

import resources.Environment as Env
import resources.phrases as phrases
from src.model.BountyGift import BountyGift
from src.model.User import User
from src.model.enums.BountyGiftStatus import BountyGiftStatus
from src.model.enums.Command import Command
from src.model.enums.Notification import BountyGiftReceivedNotification
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_amount_from_command, validate_amount, get_belly_formatted
from src.service.math_service import get_value_from_percentage
from src.service.message_service import full_message_send, get_yes_no_keyboard
from src.service.notification_service import send_notification
from src.service.user_service import user_is_boss


def manage(update: Update, context: CallbackContext, user: User, inbound_keyboard: Keyboard, target_user: User,
           command: Command) -> None:
    """
    Manage the Bounty gift screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :param target_user: The target user in case of a reply
    :param command: The command
    :return: None
    """

    # Request send a gift
    if inbound_keyboard is None:
        send_request(update, context, user, target_user, command)
        return

    keyboard_interaction(update, context, user, inbound_keyboard)


def validate(update: Update, context: CallbackContext, sender: User, receiver: User, command: Command = None,
             bounty_gift: BountyGift = None) -> bool:
    """
    Validate the fight request
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
            full_message_send(context, phrases.BOUNTY_GIFT_NO_AMOUNT, update=update, add_delete_button=True)
            return False

        # Wager basic validation, error message is sent by validate_wager
        if not validate_amount(update, context, sender, command.parameters[0], Env.BOUNTY_GIFT_MIN_AMOUNT.get_int()):
            return False

    # Get the amounts
    amount, tax_percentage, tax_amount, total_amount = get_amounts(update, sender, receiver, command, bounty_gift)

    # Sender does not have enough bounty
    if sender.bounty < total_amount:
        ot_text = phrases.BOUNTY_GIFT_NOT_ENOUGH_BOUNTY.format(get_belly_formatted(sender.bounty),
                                                               get_belly_formatted(amount),
                                                               get_belly_formatted(tax_amount),
                                                               tax_percentage,
                                                               get_belly_formatted(total_amount))
        full_message_send(context, ot_text, update=update, add_delete_button=True)
        return False

    return True


def send_request(update: Update, context: CallbackContext, sender: User, receiver: User, command: Command) -> None:
    """
    Send request to send a bounty gift
    :param update: The update object
    :param context: The context object
    :param sender: The user that wants to send a bounty gift
    :param receiver: The user to send the bounty gift to
    :param command: The command
    :return: None
    """

    if not validate(update, context, sender, receiver, command):
        return

    # Get the amounts
    amount, tax_percentage, tax_amount, total_amount = get_amounts(update, sender, receiver, command)

    ot_text = phrases.BOUNTY_GIFT_REQUEST.format(get_belly_formatted(amount), receiver.get_markdown_mention(),
                                                 get_belly_formatted(tax_amount), tax_percentage,
                                                 get_belly_formatted(total_amount))

    # Save
    bounty_gift: BountyGift = BountyGift()
    bounty_gift.sender = sender
    bounty_gift.receiver = receiver
    bounty_gift.amount = amount
    bounty_gift.tax_percentage = tax_percentage
    bounty_gift.save()

    # Keyboard
    # Delete button can't be replaced by add_delete_button because bounty_gift have to be deleted
    inline_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(sender, screen=Screen.GRP_BOUNTY_GIFT,
                                                                 primary_key=bounty_gift.id)]

    message: Message = full_message_send(context, ot_text, update=update, keyboard=inline_keyboard)
    bounty_gift.message_id = message.message_id
    bounty_gift.save()


def get_tax_percentage(sender: User, receiver: User, update: Update) -> int:
    """
    Get the tax to pay for a bounty gift
    :param sender: The sender
    :param receiver: The receiver
    :param update: The update object
    :return: The tax
    """

    # Sender and receiver are in the same crew, no tax
    if sender.in_same_crew(receiver):
        return 0

    # Sender is a boss, no tax
    if user_is_boss(sender, update):
        return 0

    return sender.bounty_gift_tax


def get_amounts(update: Update, user: User, target_user: User, command: Command = None, bounty_gift: BountyGift = None
                ) -> tuple[int, int, int, int]:
    """
    Get the amounts for a bounty gift
    :param update: The update object
    :param user: The user object
    :param target_user: The target user
    :param command: The command
    :param bounty_gift: The bounty gift object
    :return: The amount, tax percentage, tax amount, total amount
    """

    if bounty_gift is None:
        amount = get_amount_from_command(command.parameters[0])
    else:
        amount = bounty_gift.amount

    tax_percentage = get_tax_percentage(user, target_user, update)
    tax_amount = int(get_value_from_percentage(amount, tax_percentage))
    total_amount = amount + tax_amount

    return amount, tax_percentage, tax_amount, total_amount


def keyboard_interaction(update: Update, context: CallbackContext, sender: User, inbound_keyboard: Keyboard) -> None:
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
        full_message_send(context, phrases.BOUNTY_GIFT_CANCELLED, update=update, add_delete_button=True)
        return

    receiver: User = bounty_gift.receiver
    if not validate(update, context, sender, receiver, bounty_gift=bounty_gift):
        bounty_gift.delete_instance()
        return

    # Get the amounts
    amount, tax_percentage, tax_amount, total_amount = get_amounts(update, sender, receiver, bounty_gift=bounty_gift)

    bounty_gift.amount = amount
    bounty_gift.tax_percentage = tax_percentage
    bounty_gift.status = BountyGiftStatus.CONFIRMED
    bounty_gift.save()

    # Update sender
    sender.bounty -= total_amount

    if tax_percentage > 0:
        sender.bounty_gift_tax += Env.BOUNTY_GIFT_TAX_INCREASE.get_int()

    # Update receiver
    receiver.bounty += amount
    receiver.save()

    # Send message
    ot_text = phrases.BOUNTY_GIFT_CONFIRMED.format(get_belly_formatted(amount), receiver.get_markdown_mention(),
                                                   get_belly_formatted(tax_amount), tax_percentage,
                                                   get_belly_formatted(total_amount))
    full_message_send(context, ot_text, update=update, add_delete_button=True)

    # Send notification to receiver
    notification = BountyGiftReceivedNotification(sender, amount)
    send_notification(context, receiver, notification)
