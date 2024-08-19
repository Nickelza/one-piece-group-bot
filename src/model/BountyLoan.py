from datetime import datetime, timedelta

from peewee import *
from telegram import Update

import resources.Environment as Env
from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.BountyLoanSource import BountyLoanSource
from src.model.enums.BountyLoanStatus import BountyLoanStatus
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen


class BountyLoan(BaseModel):
    """
    BountyLoan class
    """

    loaner = ForeignKeyField(
        User, backref="bounty_loaners", on_delete="CASCADE", on_update="CASCADE"
    )
    borrower = ForeignKeyField(
        User, backref="bounty_borrowers", on_delete="CASCADE", on_update="CASCADE"
    )
    amount = BigIntegerField()
    tax_percentage = FloatField()
    repay_amount = BigIntegerField()
    amount_repaid = BigIntegerField(default=0)
    duration = IntegerField()  # In seconds
    deadline_date = DateTimeField()
    last_payment_date = DateTimeField(null=True)
    forgiven_date = DateTimeField(null=True)
    status = SmallIntegerField(default=BountyLoanStatus.AWAITING_LOANER_CONFIRMATION)
    group_chat = ForeignKeyField(
        GroupChat,
        null=True,
        backref="bounty_loan_groups_chats",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    message_id = IntegerField(null=True)
    source = CharField(max_length=10, null=True)
    external_id: int | IntegerField = IntegerField(null=True)
    is_auto_forgiven: bool | SmallIntegerField = SmallIntegerField(default=0)

    class Meta:
        db_table = "bounty_loan"

    async def pay(self, amount: int, update: Update = None):
        from src.service.bounty_service import add_or_remove_bounty
        from src.service.date_service import datetime_is_before

        """
        Pay the loan
        :param amount: The amount to pay
        :param update: The update object
        :return: None
        """
        if amount > self.get_remaining_amount():
            raise ValueError("Amount is greater than remaining amount")

        self.amount_repaid += amount
        self.last_payment_date = datetime.now()

        if self.amount_repaid == self.repay_amount:
            self.status = BountyLoanStatus.REPAID

        # Subtract from borrower's bounty
        # noinspection PyTypeChecker
        await add_or_remove_bounty(
            self.borrower, amount, add=False, update=update, raise_error_if_negative_bounty=False
        )

        # Add to loaner's bounty
        # noinspection PyTypeChecker
        await add_or_remove_bounty(self.loaner, amount, check_for_loan=False, update=update)

        self.borrower.save()
        self.loaner.save()

        # If N days since expiration and at least double the amount repaid, set forgiven
        if (
            self.status == BountyLoanStatus.EXPIRED
            and datetime_is_before(
                self.deadline_date + timedelta(days=Env.BOUNTY_LOAN_FORGIVENESS_DAYS.get_int())
            )
            and self.amount_repaid >= self.amount * 2
        ):
            self.forgive()
            self.is_auto_forgiven = True

        self.save()

    def get_maximum_payable_amount(self, amount: int) -> int:
        """
        Get the maximum payable amount between the given amount and the remaining amount
        :param amount: The amount
        :return: The maximum payable amount
        """
        return min(amount, (self.repay_amount - self.amount_repaid))

    def is_active(self):
        """
        Whether the loan is active
        :return: Whether the loan is active
        """
        return BountyLoanStatus(self.status).is_active()

    def get_remaining_amount(self):
        """
        Get the remaining amount
        :return: The remaining amount
        """
        return self.repay_amount - self.amount_repaid

    def forgive(self):
        """
        Forgive the loan
        :return: None
        """
        self.status = BountyLoanStatus.FORGIVEN
        self.forgiven_date = datetime.now()

        self.save()

    def get_status(self) -> BountyLoanStatus:
        """
        Get the status
        :return: The status
        """
        return BountyLoanStatus(self.status)

    def get_deeplink(self):
        """
        Get the deeplink
        :return: The deeplink
        """
        from src.service.message_service import get_deeplink

        return get_deeplink(
            info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: self.id},
            screen=Screen.PVT_BOUNTY_LOAN_DETAIL,
        )

    def get_source(self) -> BountyLoanSource:
        """
        Get the source
        :return: The source
        """
        return BountyLoanSource(self.source)

    def get_source_deeplink(self):
        """
        Get the source deeplink
        :return: The source deeplink
        """
        if self.external_id is None:
            raise ValueError("External id is required for deeplink")

        return self.get_source().get_deeplink(self.external_id)


BountyLoan.create_table()
