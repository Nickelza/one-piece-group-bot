from enum import IntEnum, StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
from resources import phrases
from src.model.BountyLoan import BountyLoan
from src.model.User import User
from src.model.enums.ContextDataKey import ContextDataKey
from src.model.enums.Notification import BountyLoanPaymentNotification
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CommonChatError import CommonChatException
from src.model.error.CustomException import BountyLoanValidationException, BellyValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import validate_amount, get_amount_from_string
from src.service.message_service import (
    full_message_send,
    get_create_or_edit_status,
    get_yes_no_keyboard,
)
from src.service.notification_service import send_notification
from src.utils.string_utils import get_belly_formatted


class Step(IntEnum):
    REQUEST_AMOUNT = 0
    REQUEST_CONFIRMATION = 1
    END = 2


class BountyLoanDetailActivateReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    PAY_ALL = "b"


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the bounty loan detail pay screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """
    from src.chat.private.screens.screen_bounty_loan_detail import (
        manage as manage_bounty_loan_detail,
    )

    should_ignore_input, should_create_item, should_validate_input = get_create_or_edit_status(
        user, inbound_keyboard
    )

    if not should_ignore_input:
        # Validate that the user can pay this loan
        if inbound_keyboard is not None:
            loan: BountyLoan = BountyLoan.get_by_id(
                inbound_keyboard.get(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY)
            )
        else:
            loan: BountyLoan = BountyLoan.get_by_id(user.private_screen_in_edit_id)

        step = Step(user.private_screen_step if user.private_screen_step else Step.REQUEST_AMOUNT)
        if not await validate(
            update,
            context,
            user,
            inbound_keyboard,
            loan,
            should_validate_amount=(step is not Step.REQUEST_AMOUNT),
        ):
            return

        user.private_screen_in_edit_id = loan.id

        if user.private_screen_step is None:
            user.private_screen_step = Step.REQUEST_AMOUNT

        inline_keyboard = [[]]
        match step:
            case Step.REQUEST_AMOUNT:
                ot_text = phrases.BOUNTY_LOAN_ITEM_PAY_REQUEST.format(
                    get_belly_formatted(loan.repay_amount),
                    get_belly_formatted(loan.amount_repaid),
                    get_belly_formatted(loan.get_remaining_amount()),
                    user.get_bounty_formatted(),
                )

                # Pay all button
                inline_keyboard.append([
                    Keyboard(
                        phrases.PVT_KEY_BOUNTY_LOAN_DETAIL_PAY_ALL,
                        info={
                            BountyLoanDetailActivateReservedKeys.PAY_ALL: 1,
                            ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_CONFIRMATION,
                        },
                        inbound_info=inbound_keyboard.info,
                    )
                ])

            case Step.REQUEST_CONFIRMATION:
                if (
                    inbound_keyboard is not None
                    and BountyLoanDetailActivateReservedKeys.PAY_ALL in inbound_keyboard.info
                ):
                    amount = loan.get_remaining_amount()
                    if not await validate(update, context, user, None, loan, amount=amount):
                        return
                else:
                    amount = loan.get_maximum_payable_amount(
                        get_amount_from_string(update.message.text, user)
                    )

                ot_text = phrases.BOUNTY_LOAN_ITEM_PAY_CONFIRMATION_REQUEST.format(
                    get_belly_formatted(amount)
                )

                # Save amount to user_data
                user.set_context_data(context, ContextDataKey.BOUNTY_LOAN_REPAY_AMOUNT, amount)

                # Add confirmation buttons
                # Adding no_extra_keys to go back to the request amount step
                # Adding yes_extra_keys to preserve extra step, else it will get erased
                inline_keyboard.append(
                    get_yes_no_keyboard(
                        user,
                        Screen.PVT_BOUNTY_LOAN_DETAIL_PAY,
                        primary_key=loan.id,
                        no_extra_keys={ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_AMOUNT},
                        yes_extra_keys={ReservedKeyboardKeys.SCREEN_STEP: Step.END},
                    )
                )

            case Step.END:
                if inbound_keyboard is None:
                    return

                amount = int(
                    user.get_context_data(context, ContextDataKey.BOUNTY_LOAN_REPAY_AMOUNT)
                )
                await loan.pay(amount, update)

                # Send notification to loaner
                await send_notification(
                    context, loan.loaner, BountyLoanPaymentNotification(loan, amount)
                )

                ot_text = phrases.BOUNTY_LOAN_ITEM_PAY_SUCCESS.format(get_belly_formatted(amount))
                # Show callback alert
                await full_message_send(
                    context, ot_text, update=update, answer_callback=True, show_alert=True
                )

                # Go back to loan detail
                user.reset_private_screen()
                # Remove step
                if ReservedKeyboardKeys.SCREEN_STEP in inbound_keyboard.info:
                    inbound_keyboard.info.pop(ReservedKeyboardKeys.SCREEN_STEP)

                await manage_bounty_loan_detail(
                    update, context, inbound_keyboard, user, called_from_another_screen=True
                )
                return

            case _:
                raise ValueError(f"Invalid step: {step}")

        if user.private_screen_step is not None:
            user.private_screen_step += 1

        # Send message
        previous_screens = user.get_private_screen_list()[:-1]
        previous_screen_list_keyboard_info = {ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: loan.id}
        if step > 0:
            previous_screen_list_keyboard_info[ReservedKeyboardKeys.SCREEN_STEP] = step - 1

        await full_message_send(
            context,
            str(ot_text),
            update=update,
            inbound_keyboard=inbound_keyboard,
            keyboard=inline_keyboard,
            previous_screens=previous_screens,
            previous_screen_list_keyboard_info=previous_screen_list_keyboard_info,
            user=user,
        )


async def validate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    inbound_keyboard: Keyboard | None,
    loan: BountyLoan,
    amount: int = None,
    should_validate_amount: bool = True,
) -> bool:
    """
    Validate the bounty loan pay

    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param loan: The loan
    :param inbound_keyboard: The inbound keyboard
    :param amount: The amount
    :param should_validate_amount: Whether to validate the amount
    :return: True if validation succeeded, False otherwise
    """

    try:
        # Loan not active
        if not loan.is_active():
            raise BountyLoanValidationException(phrases.BOUNTY_LOAN_ITEM_NOT_ACTIVE)

        # Validate amount:
        if amount is None:
            if inbound_keyboard is None:
                try:
                    amount = update.message.text
                except AttributeError:
                    raise BountyLoanValidationException(phrases.ACTION_INVALID_WAGER_AMOUNT)
            else:
                try:
                    amount = user.get_context_data(
                        context, ContextDataKey.BOUNTY_LOAN_REPAY_AMOUNT
                    )
                except CommonChatException:
                    pass

        if amount is not None and should_validate_amount:
            minimum_required = min(
                loan.get_remaining_amount(), Env.BOUNTY_LOAN_MIN_AMOUNT.get_int()
            )
            await validate_amount(
                update,
                context,
                user,
                amount,
                required_belly=minimum_required,
                send_error_message=False,
                raise_belly_validation_exception=True,
            )

    except (BountyLoanValidationException, BellyValidationException) as e:
        # Show alert if callback else send a message
        await full_message_send(
            context,
            str(e),
            update=update,
            answer_callback=True,
            show_alert=True,
            inbound_keyboard=inbound_keyboard,
        )
        return False

    return True
