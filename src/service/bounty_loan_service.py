from datetime import datetime, timedelta

from telegram.ext import ContextTypes

from src.model.BountyLoan import BountyLoan
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.BountyLoanSource import BountyLoanSource
from src.model.enums.BountyLoanStatus import BountyLoanStatus
from src.model.enums.Notification import BountyLoanExpiredNotification
from src.service.notification_service import send_notification


async def set_expired_bounty_loans(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Set expired bounty loans
    :param context: The context
    :return: None
    """
    # Get all expired bounty loans
    expired_bounty_loans: list[BountyLoan] = BountyLoan.select().where(
        (BountyLoan.status == BountyLoanStatus.ACTIVE)
        & (BountyLoan.deadline_date < datetime.now())
    )

    for expired_bounty_loan in expired_bounty_loans:
        # Set expired
        expired_bounty_loan.status = BountyLoanStatus.EXPIRED
        expired_bounty_loan.save()

        # Send notification to the borrower
        await send_notification(
            context,
            expired_bounty_loan.borrower,
            BountyLoanExpiredNotification(expired_bounty_loan),
        )


def add_loan(
    loaner: User,
    borrower: User,
    amount: int,
    group_chat: GroupChat,
    source: BountyLoanSource,
    message_id: int = None,
    tax_percentage: float = 0,
    repay_amount: int = None,
    duration: int = 0,
    status: BountyLoanStatus = BountyLoanStatus.ACTIVE,
    external_id: int = None,
) -> BountyLoan:
    """
    Create a bounty loan
    :param loaner: The loaner
    :param borrower: The borrower
    :param amount: The amount
    :param group_chat: The group chat
    :param source: The source
    :param message_id: The message id
    :param tax_percentage: The tax percentage
    :param repay_amount: The repay amount
    :param duration: The duration in seconds. If 0, will set status to EXPIRED
    :param status: The status
    :param external_id: The external id
    :return: The bounty loan
    """
    if duration == 0:
        status = BountyLoanStatus.EXPIRED

    if source is not BountyLoanSource.USER and external_id is None:
        raise ValueError("External id is required for non-user source")

    if repay_amount is None:
        repay_amount = amount

    loan: BountyLoan = BountyLoan()
    loan.loaner = loaner
    loan.borrower = borrower
    loan.amount = amount
    loan.tax_percentage = tax_percentage
    loan.repay_amount = repay_amount
    loan.duration = duration
    loan.deadline_date = datetime.now() + timedelta(seconds=duration)
    loan.status = status
    loan.group_chat = group_chat
    loan.message_id = message_id
    loan.source = source.value
    loan.external_id = external_id
    loan.save()

    return loan
