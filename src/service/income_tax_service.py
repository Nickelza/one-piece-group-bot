from src.model.DevilFruitAbility import DevilFruitAbility
from src.model.User import User
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.enums.income_tax.IncomeTaxBracket import IncomeTaxBracket
from src.model.enums.income_tax.IncomeTaxReduction import IncomeTaxReduction, IncomeTaxReductionType
from src.service.math_service import get_cumulative_percentage_sum, get_value_from_percentage


def get_tax_reductions(user: User) -> list[IncomeTaxReduction]:
    """
    Get the reductions of a user
    :param user: The user
    :return: The reductions
    """

    reductions: list[IncomeTaxReduction] = []

    # Admin
    if user.is_admin:
        reductions.append(IncomeTaxReduction(IncomeTaxReductionType.ADMIN, 100))
        return reductions

    # Devil Fruit
    tax_ability: DevilFruitAbility = DevilFruitAbility.get_user_ability(user, DevilFruitAbilityType.INCOME_TAX)
    if tax_ability is not None:
        reductions.append(IncomeTaxReduction(IncomeTaxReductionType.DEVIL_FRUIT, tax_ability.value))

    return reductions


def get_tax_amount(user: User, amount: int) -> int:
    """
    Get the tax amount for a user
    :param user: The user
    :param amount: The amount
    :return: The tax amount
    """

    tax_breakdown = IncomeTaxBracket.get_tax_breakdown(user.total_gained_bounty, amount)
    total_tax_amount = IncomeTaxBracket.get_tax_amount_from_breakdown(tax_breakdown)

    if total_tax_amount == 0:
        return amount

    reductions = get_tax_reductions(user)
    if len(reductions) == 0:
        return total_tax_amount

    # Calculate cumulative reduction percentage
    tax_reduction_percentage = get_cumulative_percentage_sum([reduction.amount for reduction in reductions])
    total_tax_amount -= get_value_from_percentage(total_tax_amount, tax_reduction_percentage)

    # Apply tax to amount
    return int(total_tax_amount)
