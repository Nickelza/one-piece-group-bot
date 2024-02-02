from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.private.screens.screen_bounty_loan import BountyLoanListPage
from src.chat.private.screens.screen_bounty_loan_detail_pay import Step as StepPay
from src.model.BountyLoan import BountyLoan
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
    user: User,
    called_from_another_screen: bool = False,
) -> None:
    """
    Manage the bounty loan detail screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :param called_from_another_screen: Whether this screen was called from another screen
    (pay confirmation or forgive)
    :return: None
    """

    if called_from_another_screen:
        # Set this screen as the current screen
        inbound_keyboard.screen = Screen.PVT_BOUNTY_LOAN_DETAIL
        inbound_keyboard.previous_screen_list.pop()

    bounty_loan_list_page = BountyLoanListPage()

    bounty_loan_list_page.user = user
    bounty_loan_list_page.init_legend_filter_results()
    bounty_loan_list_page.set_object(
        inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY)
    )

    loan: BountyLoan = bounty_loan_list_page.object
    inline_keyboard: list[list[Keyboard]] = []

    if loan.is_active():
        # If borrower, show pay button
        if not bounty_loan_list_page.user_is_loaner:
            button_info = {
                ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: loan.id,
                ReservedKeyboardKeys.SCREEN_STEP: StepPay.REQUEST_AMOUNT,
            }
            inline_keyboard.append([
                Keyboard(
                    phrases.PVT_KEY_BOUNTY_LOAN_DETAIL_PAY,
                    screen=Screen.PVT_BOUNTY_LOAN_DETAIL_PAY,
                    info=button_info,
                )
            ])

        # If loaner, show forgive button
        if bounty_loan_list_page.user_is_loaner:
            button_info = {ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: loan.id}
            inline_keyboard.append([
                Keyboard(
                    phrases.PVT_KEY_BOUNTY_LOAN_DETAIL_FORGIVE,
                    screen=Screen.PVT_BOUNTY_LOAN_DETAIL_FORGIVE,
                    info=button_info,
                )
            ])

    await full_message_send(
        context,
        bounty_loan_list_page.get_item_detail_text(),
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )
