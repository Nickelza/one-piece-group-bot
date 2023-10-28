from datetime import datetime

from telegram.ext import ContextTypes

from src.model.BountyLoan import BountyLoan
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
        & (BountyLoan.deadline_date < datetime.now()))

    for expired_bounty_loan in expired_bounty_loans:
        # Set expired
        expired_bounty_loan.status = BountyLoanStatus.EXPIRED
        expired_bounty_loan.save()

        # Send notification to the borrower
        await send_notification(context, expired_bounty_loan.borrower,
                                BountyLoanExpiredNotification(expired_bounty_loan))
