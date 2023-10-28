import json
from enum import StrEnum

from resources import phrases


class IncomeTaxContributionType(StrEnum):
    CREW_CHEST = 'crew_chest'


class IncomeTaxContribution:
    def __init__(self, contribution_type: IncomeTaxContributionType, percentage: float):
        self.contribution_type = contribution_type
        self.percentage = percentage

    @staticmethod
    def from_string(contribution_list: str) -> list['IncomeTaxContribution']:
        """
        Get the tax contribution list from a string
        :param contribution_list: The string
        :return: The tax contribution list
        """
        if not contribution_list:
            return []

        deduction_list_json = json.loads(contribution_list)
        return [IncomeTaxContribution(**contribution) for contribution in deduction_list_json]

    def get_description(self) -> str:
        """
        Get the description
        :return: The description
        """
        return INCOME_TAX_CONTRIBUTION_TYPE_DESCRIPTIONS[self.contribution_type]


INCOME_TAX_CONTRIBUTION_TYPE_DESCRIPTIONS = {
    IncomeTaxContributionType.CREW_CHEST: phrases.INCOME_TAX_CONTRIBUTION_TYPE_CREW_CHEST
}
