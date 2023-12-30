from enum import IntEnum

from resources import phrases


class BountyLoanStatus(IntEnum):
    AWAITING_LOANER_CONFIRMATION = 1
    AWAITING_BORROWER_CONFIRMATION = 2
    ACTIVE = 3
    EXPIRED = 4
    REPAID = 5
    FORGIVEN = 6

    def get_description(self) -> str:
        """
        Get the description of the status.
        :return: The description
        """
        return BOUNTY_LOAN_STATUS_DESCRIPTIONS[self]

    def is_active(self) -> bool:
        """
        Check if the status is active.
        :return: True if active, False otherwise
        """
        return self == BountyLoanStatus.ACTIVE or self == BountyLoanStatus.EXPIRED

    @staticmethod
    def get_not_confirmed_statuses() -> list["BountyLoanStatus"]:
        """
        Get the statuses that are not confirmed.
        :return: The statuses
        """

        return [
            BountyLoanStatus.AWAITING_LOANER_CONFIRMATION,
            BountyLoanStatus.AWAITING_BORROWER_CONFIRMATION,
        ]

    @staticmethod
    def get_ended_statuses() -> list["BountyLoanStatus"]:
        """
        Get the statuses that are ended.
        :return: The statuses
        """

        return [BountyLoanStatus.REPAID, BountyLoanStatus.FORGIVEN]

    def has_ended(self) -> bool:
        """
        Check if the status has is ended.
        :return: True if ended, False otherwise
        """

        return self in self.get_ended_statuses()


BOUNTY_LOAN_STATUS_DESCRIPTIONS = {
    BountyLoanStatus.AWAITING_LOANER_CONFIRMATION: (
        phrases.BOUNTY_LOAN_STATUS_AWAITING_LOANER_CONFIRMATION
    ),
    BountyLoanStatus.AWAITING_BORROWER_CONFIRMATION: (
        phrases.BOUNTY_LOAN_STATUS_AWAITING_BORROWER_CONFIRMATION
    ),
    BountyLoanStatus.ACTIVE: phrases.BOUNTY_LOAN_STATUS_ACTIVE,
    BountyLoanStatus.EXPIRED: phrases.BOUNTY_LOAN_STATUS_EXPIRED,
    BountyLoanStatus.REPAID: phrases.BOUNTY_LOAN_STATUS_REPAID,
    BountyLoanStatus.FORGIVEN: phrases.BOUNTY_LOAN_STATUS_FORGIVEN,
}
