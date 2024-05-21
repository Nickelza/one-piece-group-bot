from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.model.BountyLoan import BountyLoan
from src.model.User import User
from src.model.enums.BountyLoanSource import BountyLoanSource
from src.model.enums.BountyLoanStatus import BountyLoanStatus
from src.model.enums.Emoji import Emoji
from src.model.enums.ListPage import ListPage, EmojiLegend
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.date_service import convert_seconds_to_duration, default_datetime_format
from src.service.list_service import get_items_text_keyboard
from src.service.message_service import full_message_send
from src.utils.math_utils import get_value_from_percentage
from src.utils.string_utils import get_belly_formatted


class BountyLoanListPage(ListPage):
    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.object: BountyLoan = BountyLoan()
        self.other_user: User = User()
        self.user_is_loaner = False

    def set_object(self, object_id: int) -> None:
        self.object = BountyLoan.get(BountyLoan.id == object_id)
        self.user_is_loaner = self.object.loaner == self.user
        self.other_user = self.object.borrower if self.user_is_loaner else self.object.loaner
        self.legend = self.get_emoji_legend()

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[BountyLoan]:
        """Get bounty loans that are in confirmed or paid status"""

        return (
            self.object.select()
            .where(
                (BountyLoan.status.not_in(BountyLoanStatus.get_not_confirmed_statuses()))
                & ((BountyLoan.loaner == self.user) | (BountyLoan.borrower == self.user))
                & (self.get_active_filter_list_condition())
            )
            .order_by(BountyLoan.date.desc())
            .paginate(page, limit)
        )

    def get_item_text(self) -> str:
        to_text = phrases.TEXT_TO if self.user_is_loaner else phrases.TEXT_FROM
        return phrases.BOUNTY_LOAN_ITEM_TEXT.format(
            self.legend.emoji,
            get_belly_formatted(self.object.amount),
            to_text,
            self.other_user.get_markdown_mention(),
        )

    def get_item_detail_text(self) -> str:
        super().get_item_detail_text()

        ot_text = ""
        # Loaner or borrower
        loaner_text = (
            phrases.BOUNTY_LOAN_BORROWER if self.user_is_loaner else phrases.BOUNTY_LOAN_LOANER
        )
        ot_text += loaner_text.format(self.other_user.get_markdown_mention()).strip()

        # Source if not user
        source: BountyLoanSource = self.object.get_source()
        if source is not BountyLoanSource.USER:
            ot_text += phrases.BOUNTY_LOAN_SOURCE.format(
                source.get_description(), self.object.get_source_deeplink()
            )

        # Amounts
        ot_text += "\n"
        ot_text += phrases.BOUNTY_LOAN_AMOUNT.format(get_belly_formatted(self.object.amount))

        if self.object.get_source() is not BountyLoanSource.PLUNDER:
            ot_text += phrases.BOUNTY_LOAN_REPAY_AMOUNT.format(
                get_belly_formatted(self.object.repay_amount)
            )

        if self.object.get_status() is not BountyLoanStatus.REPAID:
            ot_text += phrases.BOUNTY_LOAN_AMOUNT_REPAID.format(
                get_belly_formatted(self.object.amount_repaid)
            )
            ot_text += phrases.BOUNTY_LOAN_AMOUNT_REMAINING.format(
                get_belly_formatted(self.object.get_remaining_amount())
            )

        # Dates
        ot_text += "\n"
        ot_text += phrases.BOUNTY_LOAN_DATE.format(
            default_datetime_format(self.object.date, self.user)
        )

        if self.object.get_source() is not BountyLoanSource.PLUNDER:
            ot_text += phrases.BOUNTY_LOAN_DURATION.format(
                convert_seconds_to_duration(self.object.duration)
            )
            ot_text += phrases.BOUNTY_LOAN_DEADLINE_DATE.format(
                default_datetime_format(self.object.deadline_date, self.user)
            )

            # Taxes (if loaner)
            if self.user_is_loaner:
                ot_text += "\n"
                tax_amount = int(
                    get_value_from_percentage(self.object.amount, self.object.tax_percentage)
                )
                total_amount = self.object.amount + tax_amount
                ot_text += phrases.BOUNTY_LOAN_TAX.format(
                    get_belly_formatted(tax_amount), self.object.tax_percentage
                )
                ot_text += phrases.BOUNTY_LOAN_TOTAL.format(get_belly_formatted(total_amount))

        # Status
        ot_text += phrases.BOUNTY_LOAN_STATUS.format(
            self.legend.emoji, BountyLoanStatus(self.object.status).get_description()
        )

        # If expired, show warning that all new gained bounty will be transferred to the loaner
        if self.object.status == BountyLoanStatus.EXPIRED:
            if self.user_is_loaner:
                action_text = phrases.BOUNTY_LOAN_EXPIRED_ACTION_LOANER.format(
                    Env.BOUNTY_LOAN_GARNISH_PERCENTAGE.get(),
                    self.other_user.get_markdown_mention(),
                )
            else:
                action_text = phrases.BOUNTY_LOAN_EXPIRED_ACTION_BORROWER.format(
                    Env.BOUNTY_LOAN_GARNISH_PERCENTAGE.get(),
                    self.other_user.get_markdown_mention(),
                )

            ot_text += phrases.BOUNTY_LOAN_EXPIRED_ACTION_PREFIX + action_text

        return ot_text

    def get_emoji_legend_list(self) -> list[EmojiLegend]:
        """
        Get the emoji legend list

        :return: The emoji legend list
        """

        return [
            EmojiLegend(
                Emoji.LOG_NEUTRAL,
                phrases.BOUNTY_LOAN_STATUS_ACTIVE,
                (BountyLoan.status == BountyLoanStatus.ACTIVE),
            ),
            EmojiLegend(
                Emoji.LOG_POSITIVE,
                phrases.BOUNTY_LOAN_STATUS_REPAID,
                (BountyLoan.status == BountyLoanStatus.REPAID),
            ),
            EmojiLegend(
                Emoji.LOG_NEGATIVE,
                phrases.BOUNTY_LOAN_STATUS_EXPIRED,
                (BountyLoan.status == BountyLoanStatus.EXPIRED),
            ),
            EmojiLegend(
                Emoji.LOG_BLUE,
                phrases.BOUNTY_LOAN_STATUS_FORGIVEN,
                (BountyLoan.status == BountyLoanStatus.FORGIVEN),
            ),
        ]


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the bounty loan list screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    bounty_loan_list_page: BountyLoanListPage = BountyLoanListPage()
    bounty_loan_list_page.user = user

    ot_text, items_keyboard = get_items_text_keyboard(
        inbound_keyboard,
        bounty_loan_list_page,
        ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY,
        Screen.PVT_BOUNTY_LOAN_DETAIL,
        text_fill_in=phrases.BOUNTY_LOAN_ITEM_TEXT_FILL_IN,
        context=context,
        user=user,
    )

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=items_keyboard,
        inbound_keyboard=inbound_keyboard,
        excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE],
    )
