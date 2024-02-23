from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.private.screens.screen_bounty_loan_detail import manage as manage_bounty_loan_detail
from src.model.BountyLoan import BountyLoan
from src.model.User import User
from src.model.enums.Notification import BountyLoanForgivenNotification
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send, get_yes_no_keyboard
from src.service.notification_service import send_notification
from src.utils.string_utils import get_belly_formatted


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the bounty loan detail forgiveness screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    loan: BountyLoan = BountyLoan.get_by_id(
        inbound_keyboard.get(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY)
    )

    if not loan.is_active():
        await full_message_send(
            context,
            phrases.BOUNTY_LOAN_ITEM_NOT_ACTIVE,
            update=update,
            inbound_keyboard=inbound_keyboard,
        )
        return

    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        # Send forgive confirmation request
        ot_text = phrases.BOUNTY_LOAN_ITEM_FORGIVE_CONFIRMATION_REQUEST.format(
            get_belly_formatted(loan.repay_amount),
            get_belly_formatted(loan.amount_repaid),
            get_belly_formatted(loan.get_remaining_amount()),
        )

        inline_keyboard: list[list[Keyboard]] = [
            get_yes_no_keyboard(
                user,
                screen=Screen.PVT_BOUNTY_LOAN_DETAIL_FORGIVE,
                primary_key=loan.id,
                inbound_keyboard=inbound_keyboard,
                no_is_back_button=True,
            )
        ]

        await full_message_send(
            context,
            ot_text,
            update=update,
            keyboard=inline_keyboard,
            inbound_keyboard=inbound_keyboard,
        )
        return

    # Forgive loan
    loan.forgive()

    # Send notification to the borrower
    await send_notification(
        context, loan.borrower, BountyLoanForgivenNotification(loan), update=update
    )

    ot_text = phrases.BOUNTY_LOAN_ITEM_FORGIVE_SUCCESS
    # Show callback alert
    await full_message_send(context, ot_text, update=update, answer_callback=True, show_alert=True)

    # Go back to loan detail
    await manage_bounty_loan_detail(
        update, context, inbound_keyboard, user, called_from_another_screen=True
    )
    return
