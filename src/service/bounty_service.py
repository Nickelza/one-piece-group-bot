import datetime
import logging
import traceback
from math import ceil

from peewee import Case
from telegram import Update
from telegram.ext import ContextTypes

import constants as c
import resources.Environment as Env
import resources.phrases as phrases
from src.model.BountyGift import BountyGift
from src.model.BountyLoan import BountyLoan
from src.model.Crew import Crew
from src.model.CrewMemberChestContribution import CrewMemberChestContribution
from src.model.DavyBackFight import DavyBackFight
from src.model.IncomeTaxEvent import IncomeTaxEvent
from src.model.User import User
from src.model.enums.BossType import BossType
from src.model.enums.BountyGiftStatus import BountyGiftStatus
from src.model.enums.BountyLoanStatus import BountyLoanStatus
from src.model.enums.Location import get_first_new_world
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.enums.income_tax.IncomeTaxBracket import IncomeTaxBracket
from src.model.enums.income_tax.IncomeTaxBreakdown import IncomeTaxBreakdown
from src.model.enums.income_tax.IncomeTaxContribution import IncomeTaxContributionType
from src.model.enums.income_tax.IncomeTaxEventType import IncomeTaxEventType
from src.model.error.CommonChatError import CommonChatException
from src.model.error.CustomException import BellyValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.date_service import get_next_run, get_previous_run
from src.service.davy_back_fight_service import add_contribution as add_dbf_contribution
from src.service.devil_fruit_service import get_ability_value
from src.service.income_tax_service import (
    get_tax_amount,
    get_tax_deductions,
    add_contribution,
    user_has_complete_tax_deduction,
)
from src.service.location_service import reset_location
from src.service.message_service import full_message_send, full_message_or_media_send_or_edit
from src.service.user_service import get_boss_type, user_is_boss
from src.utils.math_utils import subtract_percentage_from_value
from src.utils.string_utils import (
    get_unit_value_from_string,
    object_to_json_string,
    get_belly_formatted,
)


async def reset_bounty(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Resets the bounty for all users
    :return: None
    """
    # Avoid circular import
    from src.service.game_service import force_end_all_active as force_end_all_active_games
    from src.service.prediction_service import (
        remove_all_bets_from_active_predictions as remove_all_bets,
    )
    from src.service.crew_service import disband_inactive_crews

    # End all active games
    force_end_all_active_games()

    # Remove bets from all prediction which result have not been set
    await remove_all_bets(context)

    # Return all pending bounty
    User.update(bounty=User.bounty + User.pending_bounty, pending_bounty=0).execute()

    # If the bounty / 2 is higher than the required bounty for the first new world location, cap it
    # If the bounty / 2 is lower than base daily belly reward, set it to 0
    # Else divide by 2
    conditions: list[tuple[bool, int]] = [
        (
            (User.bounty / 2) > get_first_new_world().required_bounty,
            get_first_new_world().required_bounty,
        ),
        ((User.bounty / 2) < Env.DAILY_REWARD_BONUS_BASE_AMOUNT.get_int(), 0),
    ]
    case_stmt = Case(None, conditions, User.bounty / 2)
    User.update(bounty=case_stmt).execute()

    # Reset location
    reset_location()

    # Reset can create crew flag
    User.update(can_create_crew=True).execute()

    # Delete all pending bounty gifts
    BountyGift.delete().where(
        BountyGift.status == BountyGiftStatus.AWAITING_CONFIRMATION
    ).execute()

    # Delete all pending bounty loans
    BountyLoan.delete().where(
        BountyLoan.status.in_(BountyLoanStatus.get_not_confirmed_statuses())
    ).execute()

    # Reset bounty gift tax
    User.update(bounty_gift_tax=0).execute()

    # Reset total gained bounty
    User.update(total_gained_bounty=0).execute()

    # Delete tax events
    IncomeTaxEvent.delete().execute()

    # Erase all crew chests and delete all contributions from previous crew members
    # For some reason a direct delete query does not work, had to first get all valid contributions
    # and then delete
    Crew.update(chest_amount=0, total_gained_chest_amount=0).execute()

    # Still valid contributions
    valid_contributions = CrewMemberChestContribution.select().where(
        CrewMemberChestContribution.crew
        == User.select(User.crew).where(User.id == CrewMemberChestContribution.user)
    )

    # Delete all contributions that are not valid
    CrewMemberChestContribution.delete().where((
        CrewMemberChestContribution.id.not_in(
            [contribution.id for contribution in valid_contributions]
        )
    )).execute()

    # Reset level
    Crew.reset_level()

    if Env.SEND_MESSAGE_BOUNTY_RESET.get_bool():
        ot_text = phrases.BOUNTY_RESET
        await full_message_send(context, ot_text, chat_id=Env.OPD_GROUP_ID.get_int())

    # Disband inactive crews
    context.application.create_task(disband_inactive_crews(context))


async def add_or_remove_bounty(
    user: User,
    amount: int = None,
    context: ContextTypes.DEFAULT_TYPE = None,
    update: Update = None,
    should_update_location: bool = False,
    pending_belly_amount: int = None,
    add: bool = True,
    should_save: bool = False,
    should_affect_pending_bounty: bool = False,
    check_for_loan: bool = True,
    tax_event_type: IncomeTaxEventType = None,
    event_id: int = None,
    raise_error_if_negative_bounty: bool = True,
    opponent: User = None,
    should_tax: bool = True,
) -> None:
    """
    Adds a bounty to a user
    :param context: Telegram context
    :param user: The user to add the bounty to
    :param amount: The amount to add to the bounty
    :param update: Telegram update
    :param should_update_location: Whether to update the user's location
    :param pending_belly_amount: How much of the amount is from pending belly, so not newly
    acquired. Will be used to calculate eventual taxes
    :param add: Whether to add or remove the bounty
    :param should_save: Whether to save the user
    :param should_affect_pending_bounty: Whether to affect the pending bounty
    :param check_for_loan: Whether to check for an expired bounty loan when adding bounty
    :param tax_event_type: The tax event type
    :param event_id: The event id
    :param raise_error_if_negative_bounty: Whether to raise an error if the user has negative
    :param opponent: The opponent from which the bounty is being taken
    contribution if there is an active challenge
    bounty after the update
    :param should_tax: Whether to tax the bounty

    :return: The updated user
    """
    from src.service.location_service import update_location

    if amount is None and pending_belly_amount is None:
        raise ValueError("Amount or pending belly amount must be specified")

    if (tax_event_type is not None or event_id is not None) and (
        tax_event_type is None or event_id is None
    ):
        raise ValueError("Tax event type and event id must be specified together")

    if pending_belly_amount is not None and pending_belly_amount > 0:
        should_affect_pending_bounty = True
    elif should_affect_pending_bounty:
        pending_belly_amount = amount

    from src.chat.manage_message import init

    db = init()

    with db.atomic():
        # Refresh user, only bounty and pending bounty is needed
        refreshed_user: User = User.get_by_id(user.id)
        user.bounty = refreshed_user.bounty
        user.pending_bounty = refreshed_user.pending_bounty
        user.total_gained_bounty = refreshed_user.total_gained_bounty
        user.total_gained_bounty_unmodified = refreshed_user.total_gained_bounty_unmodified
        previous_pending_bounty = user.pending_bounty

        # Should remove bounty
        if not add:
            user.bounty -= amount
            if should_affect_pending_bounty:
                user.pending_bounty += (
                    amount if pending_belly_amount is None else pending_belly_amount
                )

            if user.bounty < 0 and raise_error_if_negative_bounty:
                logging.exception(
                    f"User {user.id} has negative bounty: {user.bounty} after removing "
                    f"{amount} bounty in event "
                    f"{update.to_dict() if update is not None else 'None'}"
                    f"\n{traceback.print_stack()}"
                )

                raise CommonChatException("Negative bounty after requested action")

            if should_save:
                user.save()
            return

        if should_affect_pending_bounty:
            user.pending_bounty -= amount if pending_belly_amount is None else pending_belly_amount

            if user.pending_bounty < 0 and previous_pending_bounty >= 0:
                logging.exception(
                    f"User {user.id} has negative pending bounty: {user.pending_bounty}"
                    f"(previous was {previous_pending_bounty} after removing"
                    f" {amount} pending bounty in event "
                    f"{update.to_dict() if update is not None else 'None'}"
                    f"\n{traceback.print_stack()}"
                )

            if should_save:
                user.save()

        if amount <= 0 and not should_update_location:
            return

        # User is arrested, no bounty is gained
        if user.is_arrested():
            return

        if amount > 0:
            # Amount that will be used to calculate eventual taxes
            net_amount_without_pending = amount - (
                pending_belly_amount if pending_belly_amount is not None else 0
            )
            net_amount_after_tax = net_amount_without_pending
            amount_to_add = amount

            # Get net amount after taxes
            tax_breakdown: list[IncomeTaxBreakdown] = IncomeTaxBracket.get_tax_breakdown(
                user.total_gained_bounty, net_amount_without_pending
            )
            if should_tax:
                tax_amount = IncomeTaxBreakdown.get_amount_from_list(tax_breakdown)
                if tax_amount > 0 and not user_has_complete_tax_deduction(user):
                    tax_amount = get_tax_amount(
                        user, net_amount_without_pending
                    )  # Recalculate with eventual deductions
                    net_amount_after_tax = net_amount_without_pending - tax_amount
                    amount_to_add -= tax_amount

                    # Create tax event
                    tax_event: IncomeTaxEvent | None = None
                    if tax_event_type is not None:
                        tax_event: IncomeTaxEvent = IncomeTaxEvent()
                        tax_event.user = user
                        tax_event.event_type = tax_event_type.value
                        tax_event.event_id = event_id
                        tax_event.starting_amount = user.total_gained_bounty
                        tax_event.amount = net_amount_without_pending
                        tax_event.breakdown_list = object_to_json_string(tax_breakdown)
                        tax_event.deduction_list = object_to_json_string(get_tax_deductions(user))
                        tax_event.save()

                    # Add tax to crew chest
                    if user.is_crew_member():
                        # Add crew chest contribution
                        add_contribution(
                            IncomeTaxContributionType.CREW_CHEST,
                            tax_amount,
                            tax_event=tax_event,
                            user=user,
                        )

            user.total_gained_bounty += net_amount_after_tax
            user.total_gained_bounty_unmodified += net_amount_after_tax

            if check_for_loan:
                # If user has an expired bounty loan, use n% of the bounty to repay the loan
                expired_loans = user.get_expired_bounty_loans()
                amount_for_loans = net_amount_after_tax
                for loan in expired_loans:
                    amount_for_repay = subtract_percentage_from_value(
                        amount_for_loans, Env.BOUNTY_LOAN_GARNISH_PERCENTAGE.get_float()
                    )
                    # Cap to remaining amount
                    amount_for_repay = loan.get_maximum_payable_amount(int(amount_for_repay))

                    # Pay loan
                    await loan.pay(amount_for_repay, update)

                    # Subtract from amount
                    amount_to_add -= amount_for_repay
                    amount_for_loans -= amount_for_repay

            user.bounty += amount_to_add

            if should_save:
                user.save()

            # Active Davy Back Fight, add net amount to participant contribution
            if tax_event_type in DavyBackFight.get_contribution_events():
                context.application.create_task(
                    add_dbf_contribution(user, net_amount_without_pending, opponent)
                )

    # Update the user's location
    if should_update_location:
        if context is None:
            raise ValueError("Context is required when updating the location")
        await update_location(user, context, update)


def get_amount_from_string(amount: str, user: User) -> int:
    """
    Get the wager amount
    :param amount: The wager amount
    :param user: The user
    :return: The wager amount
    """

    # If amount is *, return user's bounty
    if amount == "*":
        return user.bounty

    try:
        return int(amount.strip().replace(",", "").replace(".", ""))
    except ValueError:
        return get_unit_value_from_string(amount, c.MAGNITUDE_AMOUNT_TO_NUMBER)


async def validate_amount(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    wager_str: str | int,
    required_belly: int = None,
    add_delete_button: bool = True,
    inbound_keyboard: Keyboard = None,
    previous_screens: list[Screen] = None,
    previous_screen_list_keyboard_info: dict = None,
    should_validate_user_has_amount: bool = True,
    send_error_message: bool = True,
    raise_belly_validation_exception: bool = False,
) -> bool:
    """
    Validates the wager. Checks if the wager is a valid number, the user has enough belly, and if
    the wager is
    higher than the required belly
    :param update: Telegram update
    :param context: Telegram context
    :param user: The user to validate the wager for
    :param wager_str: The wager string
    :param required_belly: The required belly
    :param add_delete_button: Whether to add a delete button to the keyboard
    :param inbound_keyboard: The inbound keyboard
    :param previous_screens: The previous screens, for the back button if in private chat
    :param previous_screen_list_keyboard_info: The previous screen list keyboard info, for the back
    button if in private
    :param should_validate_user_has_amount: Whether to validate that the user has the amount
    :param send_error_message: Whether to send an error message if the wager is invalid
    :param raise_belly_validation_exception: Whether to raise a BellyValidationException if the
    wager is invalid
    :return: Whether the wager is valid
    """

    try:
        if isinstance(wager_str, int):
            wager = wager_str
        else:
            try:
                wager: int = get_amount_from_string(wager_str, user)
            except (AttributeError, ValueError):
                raise BellyValidationException(phrases.ACTION_INVALID_WAGER_AMOUNT)

        # User does not have enough bounty
        if should_validate_user_has_amount and user.bounty < wager:
            raise BellyValidationException(
                phrases.ACTION_INSUFFICIENT_BOUNTY.format(get_belly_formatted(wager))
            )

        # Wager less than minimum required
        if required_belly is not None and wager < required_belly:
            raise BellyValidationException(
                phrases.ACTION_WAGER_LESS_THAN_MIN.format(get_belly_formatted(required_belly))
            )
    except BellyValidationException as e:
        if send_error_message:
            await full_message_or_media_send_or_edit(
                context,
                e.message,
                update=update,
                add_delete_button=add_delete_button,
                inbound_keyboard=inbound_keyboard,
                previous_screens=previous_screens,
                previous_screen_list_keyboard_info=previous_screen_list_keyboard_info,
            )

        if raise_belly_validation_exception:
            raise e

        return False

    return True


def round_belly_up(belly: float) -> int:
    """
    Rounds the belly up to the nearest given defined amount
    :param belly: The belly to round up
    :return: The rounded belly
    """
    return (
        ceil(belly / Env.BELLY_UPPER_ROUND_AMOUNT.get_int())
        * Env.BELLY_UPPER_ROUND_AMOUNT.get_int()
    )


def get_next_bounty_reset_time() -> datetime.datetime:
    """
    Get the next bounty reset time
    :return: The next bounty reset time
    """

    start_datetime = datetime.datetime.now(datetime.timezone.utc)
    while True:
        # Get next execution of leaderboard
        next_run_time = get_next_run(
            Env.CRON_SEND_LEADERBOARD.get(), start_datetime=start_datetime
        )

        if should_reset_bounty(next_run_time):
            return next_run_time

        start_datetime = next_run_time + datetime.timedelta(seconds=1)


def get_previous_bounty_reset_time() -> datetime.datetime:
    """
    Get the previous bounty reset time
    :return: The previous bounty reset time
    """

    start_datetime = datetime.datetime.now(datetime.timezone.utc)
    while True:
        # Get next previous of leaderboard
        previous_run_time = get_previous_run(
            Env.CRON_SEND_LEADERBOARD.get(), start_datetime=start_datetime
        )

        if should_reset_bounty(previous_run_time):
            return previous_run_time

        start_datetime = previous_run_time - datetime.timedelta(seconds=1)


def should_reset_bounty(run_time: datetime) -> bool:
    """
    Checks if the bounty should be reset given the run time.
    Bounties are reset on the last leaderboard of every even month.

    :param run_time: The run time
    :return: Whether the bounty should be reset
    """
    # Adding 1 millisecond in case it's exactly midnight, else the next leaderboard will be
    # considered as the current one
    next_run_time = get_next_run(
        Env.CRON_SEND_LEADERBOARD.get(),
        start_datetime=run_time + datetime.timedelta(milliseconds=1),
    )

    # Reset if this is the last leaderboard of the month and the month before was odd
    # or today is the first, and the month before was even
    return (run_time.month != next_run_time.month and (run_time.month - 1) % 2 == 1) or (
        run_time.day == 1 and (run_time.month - 1) % 2 == 0
    )


def get_transaction_tax(sender: User, receiver: User, base_tax: float) -> float:
    """
    Get the transaction tax
    :param base_tax: The base tax
    :param sender: The sender
    :param receiver: The receiver
    :return: The transaction tax
    """

    tax = base_tax

    if user_is_boss(sender) or (receiver is not None and user_is_boss(receiver)):
        boss_type: BossType = (
            get_boss_type(sender) if user_is_boss(sender) else get_boss_type(receiver)
        )

        # Admins and legendary pirates, no tax
        if boss_type in (BossType.ADMIN, BossType.LEGENDARY_PIRATE):
            return 0
        # Pirate King and Warlord
        elif boss_type in [BossType.PIRATE_KING, BossType.WARLORD] and user_is_boss(sender):
            tax = subtract_percentage_from_value(
                base_tax, Env.PIRATE_KING_TRANSACTION_TAX_DISCOUNT.get_float()
            )

    # Send and receiver in same crew, percentage deduction
    if receiver is not None and sender.in_same_crew(receiver):
        tax = subtract_percentage_from_value(tax, Env.CREW_TRANSACTION_TAX_DISCOUNT.get_float())

    # Apply Devil Fruit ability
    tax = get_ability_value(sender, DevilFruitAbilityType.GIFT_LOAN_TAX, tax)

    return tax
