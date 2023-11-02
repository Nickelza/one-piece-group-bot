import json
from enum import StrEnum

from resources import phrases


class IncomeTaxDeductionType(StrEnum):
    ADMIN = 'admin'
    CREW_ability = 'crew'
    DEVIL_FRUIT = 'devil_fruit'


class IncomeTaxDeduction:
    def __init__(self, deduction_type: IncomeTaxDeductionType, percentage: float):
        self.deduction_type = deduction_type
        self.percentage = percentage

    @staticmethod
    def from_string(deduction_list: str) -> list['IncomeTaxDeduction']:
        """
        Get the tax deduction list from a string
        :param deduction_list: The string
        :return: The tax deduction list
        """
        if not deduction_list:
            return []

        deduction_list_json = json.loads(deduction_list)
        return [IncomeTaxDeduction(**deduction) for deduction in deduction_list_json]

    @staticmethod
    def get_percentage_from_list(deduction_list: list['IncomeTaxDeduction']) -> float:
        """
        Get the total deduction percentage from a list
        :param deduction_list: The list
        :return: The total deduction percentage
        """

        from src.service.math_service import get_cumulative_percentage_sum
        return get_cumulative_percentage_sum([deduction.percentage for deduction in deduction_list])

    def get_description(self) -> str:
        """
        Get the description
        :return: The description
        """
        return INCOME_TAX_DEDUCTION_TYPE_DESCRIPTIONS[self.deduction_type]


INCOME_TAX_DEDUCTION_TYPE_DESCRIPTIONS = {
    IncomeTaxDeductionType.ADMIN: phrases.INCOME_TAX_DEDUCTION_TYPE_ADMIN,
    IncomeTaxDeductionType.CREW_ability: phrases.INCOME_TAX_DEDUCTION_TYPE_CREW_ABILITY,
    IncomeTaxDeductionType.DEVIL_FRUIT: phrases.INCOME_TAX_DEDUCTION_TYPE_DEVIL_FRUIT
}
