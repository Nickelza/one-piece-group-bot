from datetime import datetime

from peewee import *
from telegram import Update

from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.BountyLoanStatus import BountyLoanStatus


class BountyLoan(BaseModel):
    id = PrimaryKeyField()
    """
    BountyLoan class
    """
    loaner = ForeignKeyField(User, backref='bounty_loaners', on_delete='CASCADE', on_update='CASCADE')
    borrower = ForeignKeyField(User, backref='bounty_borrowers', on_delete='CASCADE', on_update='CASCADE')
    amount = BigIntegerField()
    tax_percentage = FloatField()
    repay_amount = BigIntegerField()
    amount_repaid = BigIntegerField(default=0)
    duration = IntegerField()
    deadline_date = DateTimeField()
    last_payment_date = DateTimeField(null=True)
    forgiven_date = DateTimeField(null=True)
    date = DateTimeField(default=datetime.now)
    status = SmallIntegerField(default=BountyLoanStatus.AWAITING_LOANER_CONFIRMATION)
    group_chat = ForeignKeyField(GroupChat, null=True, backref='bounty_loan_groups_chats', on_delete='RESTRICT',
                                 on_update='CASCADE')
    message_id = IntegerField(null=True)

    class Meta:
        db_table = 'bounty_loan'

    def pay(self, amount: int, update: Update = None):
        from src.service.bounty_service import add_or_remove_bounty

        """
        Pay the loan
        :param amount: The amount to pay
        :param update: The update object
        :return: None
        """
        self.amount_repaid += amount
        self.last_payment_date = datetime.now()

        if self.amount_repaid == self.repay_amount:
            self.status = BountyLoanStatus.REPAID

        # Subtract from borrower's bounty
        # noinspection PyTypeChecker
        add_or_remove_bounty(self.borrower, amount, add=False, update=update)

        # Add to loaner's bounty
        # noinspection PyTypeChecker
        add_or_remove_bounty(self.loaner, amount, check_for_loan=False, update=update)

        self.borrower.save()
        self.loaner.save()
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


BountyLoan.create_table()
