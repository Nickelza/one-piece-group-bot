import resources.Environment as Env
from src.model.DevilFruitAbility import DevilFruitAbility
from src.model.IncomeTaxEvent import IncomeTaxEvent
from src.model.User import User
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.enums.income_tax.IncomeTaxBracket import IncomeTaxBracket
from src.model.enums.income_tax.IncomeTaxBreakdown import IncomeTaxBreakdown
from src.model.enums.income_tax.IncomeTaxContribution import IncomeTaxContributionType, IncomeTaxContribution
from src.model.enums.income_tax.IncomeTaxDeduction import IncomeTaxDeduction, IncomeTaxDeductionType
from src.service.math_service import get_cumulative_percentage_sum, get_value_from_percentage
from src.service.string_service import object_to_json_string


def get_tax_deductions(user: User) -> list[IncomeTaxDeduction]:
    """
    Get the deductions of a user
    :param user: The user
    :return: The deductions
    """

    deductions: list[IncomeTaxDeduction] = []

    # Admin
    if user.is_admin:
        deductions.append(IncomeTaxDeduction(IncomeTaxDeductionType.ADMIN, 100))
        return deductions

    # Devil Fruit
    tax_ability: DevilFruitAbility = DevilFruitAbility.get_user_ability(user, DevilFruitAbilityType.INCOME_TAX)
    if tax_ability is not None:
        deductions.append(IncomeTaxDeduction(IncomeTaxDeductionType.DEVIL_FRUIT, tax_ability.value))

    return deductions


def get_tax_amount(user: User, amount: int) -> int:
    """
    Get the tax amount for a user
    :param user: The user
    :param amount: The amount
    :return: The tax amount
    """

    tax_breakdown = IncomeTaxBracket.get_tax_breakdown(user.total_gained_bounty, amount)
    total_tax_amount = IncomeTaxBreakdown.get_amount_from_list(tax_breakdown)

    if total_tax_amount == 0:
        return amount

    deductions = get_tax_deductions(user)
    if len(deductions) == 0:
        return total_tax_amount

    # Calculate cumulative deduction percentage
    tax_deduction_percentage = get_cumulative_percentage_sum([deduction.percentage for deduction in deductions])
    total_tax_amount -= get_value_from_percentage(total_tax_amount, tax_deduction_percentage)

    # Apply tax to amount
    return int(total_tax_amount)


def add_contribution(contribution_type: IncomeTaxContributionType, tax_amount: int, tax_event: IncomeTaxEvent = None,
                     user: User = None) -> None:
    """
    Add a tax contribution

    :param contribution_type: The contribution type
    :param tax_amount: The tax amount
    :param tax_event: The tax event
    :param user: The user
    :return: None
    """
    from src.service.crew_service import add_to_crew_chest

    if tax_event is None and user is None:
        raise ValueError('Either tax_event or user must be provided')

    if tax_event is not None and user is None:
        user = tax_event.user

    match contribution_type:
        case IncomeTaxContributionType.CREW_CHEST:
            contribution_percentage = Env.TAX_CREW_CHEST_PERCENTAGE.get_float()
            contribution_amount = get_value_from_percentage(tax_amount, contribution_percentage)
            add_to_crew_chest(user, int(contribution_amount))
        case _:
            raise ValueError(f'Invalid contribution type: {contribution_type}')

    if tax_event is None:
        return

    # Add contribution to tax event
    contribution: IncomeTaxContribution = IncomeTaxContribution(contribution_type, contribution_percentage)

    # Get existing contribution list
    contribution_list: list[IncomeTaxContribution] = IncomeTaxContribution.from_string(tax_event.contribution_list)
    contribution_list.append(contribution)

    # Update tax event
    tax_event.contribution_list = object_to_json_string(contribution_list)
    tax_event.save()
