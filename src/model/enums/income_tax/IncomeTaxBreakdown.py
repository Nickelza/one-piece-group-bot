import json

from src.model.enums.income_tax.IncomeTaxDeduction import IncomeTaxDeduction


class IncomeTaxBreakdown:
    def __init__(self, taxable_amount: int, tax_percentage: float, tax_amount: int):
        self.taxable_amount = taxable_amount
        self.tax_percentage = tax_percentage
        self.tax_amount = tax_amount

    @staticmethod
    def from_string(breakdown_list: str) -> list['IncomeTaxBreakdown']:
        """
        Get the tax breakdown list from a string
        :param breakdown_list: The string
        :return: The tax breakdown list
        """
        if not breakdown_list:
            return []

        breakdown_list_json = json.loads(breakdown_list)
        return [IncomeTaxBreakdown(**breakdown) for breakdown in breakdown_list_json]

    @staticmethod
    def get_amount_from_list(tax_breakdown: list['IncomeTaxBreakdown']) -> int:
        """
        Get the tax from a tax breakdown

        :param tax_breakdown: The tax breakdown
        :return: The tax
        """
        return sum([tax.tax_amount for tax in tax_breakdown])

    @staticmethod
    def get_amount_with_deduction_from_list(tax_breakdown: list['IncomeTaxBreakdown'],
                                            deduction_list: list[IncomeTaxDeduction]) -> int:
        """
        Get the tax from a tax breakdown

        :param tax_breakdown: The tax breakdown
        :param deduction_list: The deduction list
        :return: The tax
        """
        from src.service.math_service import get_value_from_percentage

        amount = IncomeTaxBreakdown.get_amount_from_list(tax_breakdown)
        deduction_percentage = IncomeTaxDeduction.get_percentage_from_list(deduction_list)

        return int(get_value_from_percentage(amount, 100 - deduction_percentage))
