import datetime
import logging

from telegram import Update, Message
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.model.BountyLoan import BountyLoan
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.BountyLoanStatus import BountyLoanStatus
from src.model.enums.Command import Command
from src.model.enums.Emoji import Emoji
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.enums.income_tax.IncomeTaxEventType import IncomeTaxEventType
from src.model.error.GroupChatError import GroupChatException, GroupChatError
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import (
    get_amount_from_string,
    validate_amount,
    get_belly_formatted,
    get_transaction_tax,
    add_or_remove_bounty,
)
from src.service.date_service import (
    validate_duration,
    get_duration_from_string,
    convert_seconds_to_duration,
    datetime_is_before,
    get_datetime_in_future_hours,
)
from src.service.devil_fruit_service import get_ability_value
from src.service.math_service import get_value_from_percentage, get_interest_percentage_from_value
from src.service.message_service import full_message_send, get_yes_no_keyboard, get_deeplink


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
    Manage the Bounty loan screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :param target_user: The target user in case of a reply
    :param command: The command
    :param group_chat: The group chat
    :return: None
    """

    # Request initiate a loan
    if inbound_keyboard is None:
        await send_request(update, context, user, target_user, command, group_chat)
        return

    await keyboard_interaction(update, context, inbound_keyboard, user)


async def validate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    loaner: User,
    borrower: User,
    command: Command = None,
    loan: BountyLoan = None,
) -> bool:
    """
    Validate the bounty loan request
    :param update: The update object
    :param context: The context object
    :param loaner: The user that wants to loan
    :param borrower: The user that wants to borrow
    :param command: The command
    :param loan: The bounty loan object
    :return: True if the request is valid, False otherwise
    """

    # Command does not have correct parameters
    if loan is None:
        if len(command.parameters) != 3:
            await full_message_send(
                context, phrases.BOUNTY_LOAN_INVALID_COMMAND, update=update, add_delete_button=True
            )
            return False

        # Loan amount validation, error message is sent by validate_wager
        if not await validate_amount(
            update, context, loaner, command.parameters[0], Env.BOUNTY_LOAN_MIN_AMOUNT.get_int()
        ):
            return False

        # Repayment amount validation, error message is sent by validate_wager
        if not await validate_amount(
            update, context, loaner, command.parameters[1], should_validate_user_has_amount=False
        ):
            return False

        # Deadline validation, error message is sent by validate_duration
        if not await validate_duration(update, context, command.parameters[2]):
            return False

    # Get the amounts
    amount, tax_percentage, tax_amount, total_amount, repay_amount, duration = await get_amounts(
        loaner, borrower, command, loan
    )

    # Sender does not have enough bounty
    if loaner.bounty < total_amount:
        # Get max loan amount
        max_amount = int(loaner.bounty / (1 + (tax_percentage / 100)))
        ot_text = phrases.BOUNTY_LOAN_NOT_ENOUGH_BOUNTY.format(
            get_belly_formatted(loaner.bounty),
            get_belly_formatted(amount),
            get_belly_formatted(tax_amount),
            tax_percentage,
            get_belly_formatted(total_amount),
            get_belly_formatted(max_amount),
        )
        await full_message_send(context, ot_text, update=update, add_delete_button=True)
        return False

    # Sender in cooldown
    if not datetime_is_before(loaner.bounty_loan_issue_cool_down_end_date):
        remaining_time = convert_seconds_to_duration(
            (loaner.bounty_loan_issue_cool_down_end_date - datetime.datetime.now()).total_seconds()
        )
        await full_message_send(
            context,
            phrases.BOUNTY_LOAN_ISSUE_COOLDOWN_ACTIVE.format(remaining_time),
            update=update,
            add_delete_button=True,
        )
        return False

    # Exceeds max allowed duration
    duration_days = int(duration / 86400)
    if duration_days > Env.BOUNTY_LOAN_MAX_DURATION_DAYS.get_int():
        await full_message_send(
            context,
            phrases.BOUNTY_LOAN_MAX_DURATION_EXCEEDED,
            update=update,
            add_delete_button=True,
        )
        return False

    # Wrong status
    if loan is not None and loan.get_status() not in BountyLoanStatus.get_not_confirmed_statuses():
        raise GroupChatException(GroupChatError.ITEM_IN_WRONG_STATUS)

    return True


async def send_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    loaner: User,
    borrower: User,
    command: Command,
    group_chat: GroupChat,
) -> None:
    """
    Send request to initiate a loan
    :param update: The update object
    :param context: The context object
    :param loaner: The user that wants to loan
    :param borrower: The user  that wants to borrow
    :param command: The command
    :param group_chat: The group chat
    :return: None
    """

    if not await validate(update, context, loaner, borrower, command):
        return

    # Get the amounts
    amount, tax_percentage, tax_amount, total_amount, repay_amount, duration = await get_amounts(
        loaner, borrower, command
    )

    # Save
    loan: BountyLoan = BountyLoan()
    loan.loaner = loaner
    loan.borrower = borrower
    loan.amount = amount
    loan.tax_percentage = tax_percentage
    loan.repay_amount = repay_amount
    loan.duration = duration
    loan.status = BountyLoanStatus.AWAITING_LOANER_CONFIRMATION
    loan.group_chat = group_chat
    loan.save()

    # Keyboard
    inline_keyboard: list[list[Keyboard]] = [
        get_yes_no_keyboard(loaner, screen=Screen.GRP_BOUNTY_LOAN, primary_key=loan.id)
    ]

    ot_text = get_text(loan, tax_amount, total_amount)

    try:
        message: Message = await full_message_send(
            context, ot_text, update=update, keyboard=inline_keyboard, add_delete_button=True
        )
        loan.message_id = message.message_id
        loan.save()
    except TelegramError as e:
        loan.delete_instance()
        logging.error(f"Error sending bounty loan request message: {e}")
        raise e


def get_text(loan: BountyLoan, tax_amount: int, total_amount: int) -> str:
    """
    Get the text for a bounty loan
    :param loan: The bounty loan
    :param tax_amount: The tax amount
    :param total_amount: The total amount
    :return: The text for the bounty loan
    """

    loaner: User = loan.loaner
    borrower: User = loan.borrower

    match loan.get_status():
        case BountyLoanStatus.AWAITING_LOANER_CONFIRMATION:
            status_emoji = Emoji.RED
        case BountyLoanStatus.AWAITING_BORROWER_CONFIRMATION:
            status_emoji = Emoji.YELLOW
        case _:
            status_emoji = Emoji.GREEN

    ot_text = phrases.BOUNTY_LOAN_REQUEST.format(
        loaner.get_markdown_mention(),
        borrower.get_markdown_mention(),
        get_belly_formatted(loan.amount),
        get_belly_formatted(loan.repay_amount),
        convert_seconds_to_duration(loan.duration),
        get_belly_formatted(tax_amount),
        loan.tax_percentage,
        get_belly_formatted(total_amount),
        status_emoji,
        loan.get_status().get_description(),
        Env.BOUNTY_LOAN_GARNISH_PERCENTAGE.get(),
        borrower.get_markdown_mention(),
        loaner.get_markdown_mention(),
    )

    # Add predatory warning
    loan_interest = get_interest_percentage_from_value(
        loan.repay_amount, loan.amount, add_decimal=False
    )
    if loan_interest > Env.BOUNTY_LOAN_PREDATORY_INTEREST_THRESHOLD.get_int():
        ot_text += phrases.BOUNTY_LOAN_REQUEST_PREDATORY_WARNING.format(loan_interest)

    # Add manage link
    if loan.get_status() is BountyLoanStatus.ACTIVE:
        ot_text += phrases.BOUNTY_LOAN_REQUEST_MANAGE_TEXT.format(
            get_deeplink(
                info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: loan.id},
                screen=Screen.PVT_BOUNTY_LOAN_DETAIL,
            )
        )

    return ot_text


async def get_amounts(
    sender: User, receiver: User, command: Command = None, loan: BountyLoan = None
) -> tuple[int, int, int, int, int, int]:
    """
    Get the amounts for a bounty loan
    :param sender: The sender
    :param receiver: The receiver
    :param command: The command
    :param loan: The bounty loan object
    :return: The amount, tax percentage, tax amount, total amount
    """

    if loan is None:
        amount = get_amount_from_string(command.parameters[0], sender)
        repay_amount = get_amount_from_string(command.parameters[1], sender)
        duration = get_duration_from_string(command.parameters[2])
    else:
        amount = loan.amount
        repay_amount = loan.repay_amount
        duration = loan.duration

    tax_percentage = get_transaction_tax(sender, receiver, sender.bounty_gift_tax)

    # Apply Devil Fruit ability
    if tax_percentage > 0:
        tax_percentage = get_ability_value(
            sender, DevilFruitAbilityType.GIFT_LOAN_TAX, tax_percentage
        )

    # Parse to int if tax does not have a decimal
    if float(tax_percentage).is_integer():
        tax_percentage = int(tax_percentage)

    tax_amount = int(get_value_from_percentage(amount, tax_percentage))
    total_amount = amount + tax_amount

    return amount, tax_percentage, tax_amount, total_amount, repay_amount, duration


async def keyboard_interaction(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Keyboard interaction
    :param update: The update object
    :param context: The context object
    :param inbound_keyboard: The inbound keyboard
    :param user: The user object
    :return: None
    """

    loan: BountyLoan = BountyLoan.get_by_id(
        inbound_keyboard.get(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY)
    )

    # User cancelled the request
    if not inbound_keyboard.info[ReservedKeyboardKeys.CONFIRM]:
        loan.delete_instance()
        await full_message_send(
            context, phrases.BOUNTY_LOAN_CANCELLED, update=update, add_delete_button=True
        )
        return

    loaner: User = loan.loaner
    borrower: User = loan.borrower
    if not await validate(update, context, loaner, borrower, loan=loan):
        loan.delete_instance()
        return

    # Get the amounts
    amount, tax_percentage, tax_amount, total_amount, repay_amount, duration = await get_amounts(
        loaner, borrower, loan=loan
    )

    loan.tax_percentage = tax_percentage

    if BountyLoanStatus(loan.status) is BountyLoanStatus.AWAITING_LOANER_CONFIRMATION:
        loan.status = BountyLoanStatus.AWAITING_BORROWER_CONFIRMATION
        loan.save()
        ot_text = get_text(loan, tax_amount, total_amount)

        inline_keyboard: list[list[Keyboard]] = [
            get_yes_no_keyboard(borrower, screen=Screen.GRP_BOUNTY_LOAN, primary_key=loan.id)
        ]
        await full_message_send(
            context, ot_text, update=update, keyboard=inline_keyboard, add_delete_button=True
        )
        return

    loan.status = BountyLoanStatus.ACTIVE
    loan.deadline_date = datetime.datetime.now() + datetime.timedelta(seconds=duration)
    loan.save()

    # Update loaner
    loaner.bounty_gift_tax += Env.BOUNTY_GIFT_TAX_INCREASE.get_int()
    loaner.bounty_loan_issue_cool_down_end_date = get_datetime_in_future_hours(
        Env.BOUNTY_LOAN_ISSUE_COOLDOWN_DURATION.get_int()
    )
    await add_or_remove_bounty(loaner, total_amount, add=False, update=update, should_save=True)

    # Update receiver
    await add_or_remove_bounty(
        user,
        amount,
        update=update,
        tax_event_type=IncomeTaxEventType.BOUNTY_LOAN,
        event_id=loan.id,
        should_save=True,
    )

    # 0 repay amount, pay immediately
    if repay_amount == 0:
        await loan.pay(0, update=update)

    # Send message
    ot_text = get_text(loan, tax_amount, total_amount)
    await full_message_send(context, ot_text, update=update)
