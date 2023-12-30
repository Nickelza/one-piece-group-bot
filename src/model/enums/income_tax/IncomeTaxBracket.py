import resources.Environment as Env
from src.model.enums.income_tax.IncomeTaxBreakdown import IncomeTaxBreakdown
from src.service.math_service import get_value_from_percentage


class IncomeTaxBracket:
    def __init__(self, min_amount: int, percentage: float):
        self.min_amount = min_amount
        self.percentage = percentage

    @staticmethod
    def get_bracket(amount: int) -> "IncomeTaxBracket":
        """
        Get the tax bracket
        :param amount: The amount
        :return: The tax bracket
        """

        for tax_bracket in reversed(TAX_BRACKETS):
            if amount >= tax_bracket.min_amount:
                return tax_bracket

    @staticmethod
    def get_tax_breakdown(starting_amount: int, amount: int) -> list[IncomeTaxBreakdown]:
        """
        Calculate a tax breakdown for the given amount, showing the taxable amounts, tax brackets, and tax amounts for
        each tier.

        :param starting_amount: The starting amount
        :param amount: The total amount
        :return: A list of tax breakdown tuples
        """

        tax_info: list[IncomeTaxBreakdown] = []
        remaining_amount = amount

        while remaining_amount > 0:
            current_bracket = IncomeTaxBracket.get_bracket(starting_amount)
            next_bracket = IncomeTaxBracket.get_next_bracket(starting_amount)

            taxable_amount = min(next_bracket.min_amount - starting_amount, remaining_amount)

            if taxable_amount <= 0:  # Last bracket
                taxable_amount = remaining_amount

            tax_amount = get_value_from_percentage(taxable_amount, current_bracket.percentage)

            tax_info.append(
                IncomeTaxBreakdown(taxable_amount, current_bracket.percentage, int(tax_amount))
            )

            remaining_amount -= taxable_amount
            starting_amount = next_bracket.min_amount if next_bracket else 0

        return tax_info

    @staticmethod
    def get_next_bracket(amount: int) -> "IncomeTaxBracket":
        """
        Get the next tax bracket
        :param amount: The amount
        :return: The next tax bracket
        """

        for i, tax_bracket in enumerate(TAX_BRACKETS):
            if amount <= tax_bracket.min_amount:
                try:
                    return TAX_BRACKETS[i + 1]
                except IndexError:
                    return tax_bracket

        return TAX_BRACKETS[-1]  # Return last bracket

    @staticmethod
    def get_tax(starting_amount: int, amount: int) -> int:
        """
        Get the tax
        :param starting_amount: The starting amount
        :param amount: The amount
        :return: The tax
        """
        return sum(
            [tax.tax_amount for tax in IncomeTaxBracket.get_tax_breakdown(starting_amount, amount)]
        )


# noinspection DuplicatedCode
TAX_BRACKET_0 = IncomeTaxBracket(
    Env.TAX_BRACKET_0_TOTAL_BOUNTY.get_int(), Env.TAX_BRACKET_0_PERCENTAGE.get_float()
)
TAX_BRACKET_1 = IncomeTaxBracket(
    Env.TAX_BRACKET_1_TOTAL_BOUNTY.get_int(), Env.TAX_BRACKET_1_PERCENTAGE.get_float()
)
TAX_BRACKET_2 = IncomeTaxBracket(
    Env.TAX_BRACKET_2_TOTAL_BOUNTY.get_int(), Env.TAX_BRACKET_2_PERCENTAGE.get_float()
)
TAX_BRACKET_3 = IncomeTaxBracket(
    Env.TAX_BRACKET_3_TOTAL_BOUNTY.get_int(), Env.TAX_BRACKET_3_PERCENTAGE.get_float()
)
TAX_BRACKET_4 = IncomeTaxBracket(
    Env.TAX_BRACKET_4_TOTAL_BOUNTY.get_int(), Env.TAX_BRACKET_4_PERCENTAGE.get_float()
)
TAX_BRACKET_5 = IncomeTaxBracket(
    Env.TAX_BRACKET_5_TOTAL_BOUNTY.get_int(), Env.TAX_BRACKET_5_PERCENTAGE.get_float()
)
# noinspection DuplicatedCode
TAX_BRACKET_6 = IncomeTaxBracket(
    Env.TAX_BRACKET_6_TOTAL_BOUNTY.get_int(), Env.TAX_BRACKET_6_PERCENTAGE.get_float()
)
TAX_BRACKET_7 = IncomeTaxBracket(
    Env.TAX_BRACKET_7_TOTAL_BOUNTY.get_int(), Env.TAX_BRACKET_7_PERCENTAGE.get_float()
)
TAX_BRACKET_8 = IncomeTaxBracket(
    Env.TAX_BRACKET_8_TOTAL_BOUNTY.get_int(), Env.TAX_BRACKET_8_PERCENTAGE.get_float()
)
TAX_BRACKET_9 = IncomeTaxBracket(
    Env.TAX_BRACKET_9_TOTAL_BOUNTY.get_int(), Env.TAX_BRACKET_9_PERCENTAGE.get_float()
)
TAX_BRACKET_10 = IncomeTaxBracket(
    Env.TAX_BRACKET_10_TOTAL_BOUNTY.get_int(), Env.TAX_BRACKET_10_PERCENTAGE.get_float()
)
TAX_BRACKET_11 = IncomeTaxBracket(
    Env.TAX_BRACKET_11_TOTAL_BOUNTY.get_int(), Env.TAX_BRACKET_11_PERCENTAGE.get_float()
)

TAX_BRACKETS = [
    TAX_BRACKET_0,
    TAX_BRACKET_1,
    TAX_BRACKET_2,
    TAX_BRACKET_3,
    TAX_BRACKET_4,
    TAX_BRACKET_5,
    TAX_BRACKET_6,
    TAX_BRACKET_7,
    TAX_BRACKET_8,
    TAX_BRACKET_9,
    TAX_BRACKET_10,
    TAX_BRACKET_11,
]
