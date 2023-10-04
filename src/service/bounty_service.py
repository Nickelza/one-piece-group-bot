import datetime
import logging
from math import ceil

from peewee import Case, fn
from telegram import Update
from telegram.ext import ContextTypes

import constants as c
import resources.Environment as Env
import resources.phrases as phrases
from src.model.BountyGift import BountyGift
from src.model.BountyLoan import BountyLoan
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.BossType import BossType
from src.model.enums.BountyGiftStatus import BountyGiftStatus
from src.model.enums.Location import get_last_paradise, get_first_new_world
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.pojo.Keyboard import Keyboard
from src.service.date_service import get_next_run
from src.service.devil_fruit_service import get_value
from src.service.group_service import allow_unlimited_bounty_from_messages
from src.service.location_service import reset_location
from src.service.math_service import subtract_percentage_from_value
from src.service.message_service import full_message_send
from src.service.string_service import get_unit_value_from_string
from src.service.user_service import get_boss_type, user_is_boss


def get_belly_formatted(belly: int) -> str:
    """
    Returns a formatted string of the belly
    :param belly: The belly to format e.g. 1000000
    :return: The formatted belly e.g. 1,000,000
    """

    return '{0:,}'.format(belly)


def get_message_belly(update: Update, user: User, group_chat: GroupChat) -> int:
    """
    Calculates how much bellys a message is worth
    :param update: Telegram update
    :param user: The user who sent the message
    :param group_chat: The group chat the message was sent in
    :return: How much bellys a message is worth
    """
    should_allow_unlimited_bounty_from_messages = allow_unlimited_bounty_from_messages(group_chat)

    # Unlimited bounty from messages not allowed and user have consumed all their bounty from messages, no belly
    if not should_allow_unlimited_bounty_from_messages and user.bounty_message_limit <= 0:
        return 0

    # New chat members - No belly
    try:
        if len(update.message.new_chat_members) > 0:
            return 0
    except (AttributeError, TypeError):
        pass

    # Left chat member - No belly
    try:
        if update.message.left_chat_member is not None:
            return 0
    except (AttributeError, TypeError):
        pass

    # Command message - No belly
    try:
        if update.message.text[0] in c.COMMAND_PREFIX_ALIASES:
            return 0
    except (AttributeError, TypeError):
        pass

    # Callback query - No belly
    try:
        if update.callback_query.data is not None:
            return 0
    except AttributeError:
        pass

    # Inline Bot - No belly
    try:
        if update.effective_message.via_bot is not None:
            return 0
    except AttributeError:
        pass

    # Edited message - No belly
    try:
        if update.effective_message.edit_date is not None:
            return 0
    except AttributeError:
        pass

    # User on final location - No belly
    if user.has_bounty_gain_limitations():
        return 0

    # Forwarded message - Base belly
    try:
        if update.message.forward_from is not None:
            return Env.BELLY_BASE_MESSAGE.get_int()
    except AttributeError:
        pass

    final_belly: float = Env.BELLY_BASE_MESSAGE.get_int()

    # Char multiplier - Text messages which are not forwarded
    try:
        char_belly = (1 + (len(update.message.text) * Env.BELLY_CHARACTER_MULTIPLIER.get_float()))
        # Cap if it exceeds the max allowed per character count
        max_char_belly = Env.BELLY_CHARACTER_MAX_MULTIPLE.get_float() * Env.BELLY_BASE_MESSAGE.get_int()
        char_belly = char_belly if char_belly <= max_char_belly else max_char_belly
        final_belly += char_belly
    except (AttributeError, TypeError):
        pass

    # Reply to channel post multiplier
    try:
        if update.message.reply_to_message.sender_chat.id == Env.OPD_CHANNEL_ID.get_int():
            final_belly *= Env.BELLY_REPLY_TO_CHANNEL_POST_MULTIPLIER.get_float()
    except AttributeError:
        pass

    # Sticker multiplier
    try:
        if update.message.sticker is not None:
            final_belly *= Env.BELLY_STICKER_MULTIPLIER.get_float()
    except AttributeError:
        pass
    # Animation multiplier
    try:
        if update.message.animation is not None:
            final_belly *= Env.BELLY_ANIMATION_MULTIPLIER.get_float()
    except AttributeError:
        pass

    # Location level multiplier
    location_percentage = Env.BELLY_LOCATION_LEVEL_MULTIPLIER.get_int() * user.location_level

    final_belly += int((final_belly * location_percentage) / 100)

    # Bounty from messages limit
    if not should_allow_unlimited_bounty_from_messages:
        final_belly = min(final_belly, user.bounty_message_limit)

    return round_belly_up(final_belly)


async def reset_bounty(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Resets the bounty for all users
    :return: None
    """
    # Avoid circular import
    from src.service.game_service import force_end_all_active as force_end_all_active_games
    from src.service.prediction_service import remove_all_bets_from_active_predictions as remove_all_bets

    # End all active games
    force_end_all_active_games()

    # Remove bets from all prediction which result have not been set
    await remove_all_bets(context)

    # Return all pending bounty
    User.update(bounty=User.bounty + User.pending_bounty, pending_bounty=0).execute()

    # If the bounty / 2 is higher than the required bounty for the first new world location, cap it
    # If the bounty / 2 is lower than base message belly, set it to 0
    # Else divide by 2
    conditions: list[tuple[bool, int]] = [((User.bounty / 2) > get_first_new_world().required_bounty,
                                           get_first_new_world().required_bounty),
                                          ((User.bounty / 2) < Env.BELLY_BASE_MESSAGE.get_int(), 0)]
    case_stmt = Case(None, conditions, User.bounty / 2)
    User.update(bounty=case_stmt).execute()

    # Reset location
    reset_location()

    # Reset can create crew flag
    User.update(can_create_crew=True).execute()

    # Delete all pending bounty gifts
    BountyGift.delete().where(BountyGift.status == BountyGiftStatus.AWAITING_CONFIRMATION).execute()

    # Reset bounty gift tax
    User.update(bounty_gift_tax=0).execute()

    if Env.SEND_MESSAGE_BOUNTY_RESET.get_bool():
        ot_text = phrases.BOUNTY_RESET
        await full_message_send(context, ot_text, chat_id=Env.OPD_GROUP_ID.get_int())


async def add_or_remove_bounty(user: User, amount: int = None, context: ContextTypes.DEFAULT_TYPE = None,
                               update: Update = None, should_update_location: bool = False,
                               pending_belly_amount: int = None, from_message: bool = False, add: bool = True,
                               should_save: bool = False, should_affect_pending_bounty: bool = False,
                               check_for_loan: bool = True) -> None:
    """
    Adds a bounty to a user
    :param context: Telegram context
    :param user: The user to add the bounty to
    :param amount: The amount to add to the bounty
    :param update: Telegram update
    :param should_update_location: Whether to update the user's location
    :param pending_belly_amount: How much of the amount is from pending belly, so not newly acquired. Will be used to
                                 calculate eventual taxes
    :param from_message: Whether the bounty is gained from a message
    :param add: Whether to add or remove the bounty
    :param should_save: Whether to save the user
    :param should_affect_pending_bounty: Whether to affect the pending bounty
    :param check_for_loan: Whether to check for an expired bounty loan when adding bounty
    :return: The updated user
    """
    from src.service.location_service import update_location

    if amount is None and pending_belly_amount is None:
        raise ValueError('Amount or pending belly amount must be specified')

    previous_bounty = user.bounty
    previous_pending_bounty = user.pending_bounty

    if pending_belly_amount is not None and pending_belly_amount > 0:
        should_affect_pending_bounty = True
    elif should_affect_pending_bounty:
        pending_belly_amount = amount

    # Should remove bounty
    if not add:
        user.bounty -= amount
        if should_affect_pending_bounty:
            user.pending_bounty += (amount if pending_belly_amount is None else pending_belly_amount)

        if user.bounty < 0 and previous_bounty >= 0:
            try:
                raise ValueError(f'User {user.id} has negative bounty: {user.bounty} after removing '
                                 f'{amount} bounty in event '
                                 f'{update.to_dict() if update is not None else "None"}')
            except ValueError as ve:
                logging.exception(ve)

        if should_save:
            user.save()
        return

    if should_affect_pending_bounty:
        user.pending_bounty -= (amount if pending_belly_amount is None else pending_belly_amount)

        if user.pending_bounty < 0 and previous_pending_bounty >= 0:
            try:
                raise ValueError(f'User {user.id} has negative pending bounty: {user.pending_bounty} after removing '
                                 f'{amount} pending bounty in event '
                                 f'{update.to_dict() if update is not None else "None"}')
            except ValueError as ve:
                logging.exception(ve)

        if should_save:
            user.save()

    if amount <= 0 and not should_update_location:
        return

    # User is arrested, no bounty is gained
    if user.is_arrested():
        return

    # Amount that will be used to calculate eventual taxes
    effective_amount = amount - (pending_belly_amount if pending_belly_amount is not None else 0)

    amount_to_add = amount
    if check_for_loan:
        # If user has an expired bounty loan, use n% of the bounty to repay the loan
        expired_loans = user.get_expired_bounty_loans()
        if len(expired_loans) > 0:
            expired_loan: BountyLoan = expired_loans[0]

            amount_for_repay = subtract_percentage_from_value(effective_amount,
                                                              Env.BOUNTY_LOAN_GARNISH_PERCENTAGE.get_float())
            # Cap to remaining amount
            amount_for_repay = expired_loan.get_maximum_payable_amount(int(amount_for_repay))

            # Pay loan
            await expired_loan.pay(amount_for_repay, update)

            # Subtract from amount
            amount_to_add -= amount_for_repay

    user.bounty += amount_to_add

    # If the bounty is gained from a message, subtract the amount from the bounty message limit
    if from_message:
        user.bounty_message_limit -= amount

    if should_save:
        user.save()

    # Update the user's location
    if should_update_location:
        if context is None:
            raise ValueError('Context is required when updating the location')
        await update_location(user, context, update)


def add_region_bounty_bonus() -> None:
    """
    Adds a bounty percentage to all users based on their region

    :return: None
    """

    conditions: list[tuple[bool, int]] = [((User.location_level <= get_last_paradise().level)
                                           & (User.get_is_not_arrested_statement_condition())
                                           & ~(User.get_has_bounty_gain_limitations_statement_condition()),
                                           User.bounty +
                                           ((User.bounty * Env.PARADISE_BOUNTY_BONUS.get_float()) / 100)),
                                          ((User.location_level >= get_first_new_world().level)
                                           & (User.get_is_not_arrested_statement_condition())
                                           & ~(User.get_has_bounty_gain_limitations_statement_condition()),
                                           User.bounty +
                                           ((User.bounty * Env.NEW_WORLD_BOUNTY_BONUS.get_float()) / 100))]
    case_stmt = Case(None, conditions, User.bounty)
    User.update(bounty=case_stmt).execute()


def add_crew_bounty_bonus() -> None:
    """
    Adds a bounty percentage to users in a crew
    """

    (User.update(bounty=(User.bounty + ((User.bounty * Env.CREW_BOUNTY_BONUS.get_float()) / 100)))
     .where((User.crew.is_null(False))
            & ~(User.get_has_bounty_gain_limitations_statement_condition()))
     .execute())


def add_crew_mvp_bounty_bonus() -> None:
    """
    Adds a bounty percentage to users in a crew with bounty higher than the crew average
    """

    condition: tuple[bool, int] = (
        ((User.bounty > (User.select(fn.Avg(User.bounty)).where(User.crew == User.crew).scalar()))
         & (User.get_is_not_arrested_statement_condition())
         & ~(User.get_has_bounty_gain_limitations_statement_condition())),
        User.bounty + ((User.bounty * Env.CREW_MVP_BOUNTY_BONUS.get_float()) / 100))

    case_stmt = Case(None, [condition], User.bounty)
    User.update(bounty=case_stmt).execute()


def get_amount_from_string(amount: str, user: User) -> int:
    """
    Get the wager amount
    :param amount: The wager amount
    :param user: The user
    :return: The wager amount
    """

    # If amount is *, return user's bounty
    if amount == '*':
        return user.bounty

    try:
        return int(amount.strip().replace(',', '').replace('.', ''))
    except ValueError:
        return get_unit_value_from_string(amount, c.MAGNITUDE_AMOUNT_TO_NUMBER)


async def validate_amount(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, wager_str: str,
                          required_belly: int = None, add_delete_button: bool = True, inbound_keyboard: Keyboard = None,
                          previous_screens: list[Screen] = None, previous_screen_list_keyboard_info: dict = None,
                          should_validate_user_has_amount: bool = True) -> bool:
    """
    Validates the wager. Checks if the wager is a valid number, the user has enough belly, and if the wager is
    higher than the required belly
    :param update: Telegram update
    :param context: Telegram context
    :param user: The user to validate the wager for
    :param wager_str: The wager string
    :param required_belly: The required belly
    :param add_delete_button: Whether to add a delete button to the keyboard
    :param inbound_keyboard: The inbound keyboard
    :param previous_screens: The previous screens, for the back button if in private chat
    :param previous_screen_list_keyboard_info: The previous screen list keyboard info, for the back button if in private
    :param should_validate_user_has_amount: Whether to validate that the user has the amount
    :return: Whether the wager is valid
    """

    if isinstance(wager_str, int):
        wager = wager_str
    else:
        try:
            wager: int = get_amount_from_string(wager_str, user)
        except ValueError:
            await full_message_send(context, phrases.ACTION_INVALID_WAGER_AMOUNT, update=update,
                                    add_delete_button=add_delete_button, inbound_keyboard=inbound_keyboard,
                                    previous_screens=previous_screens,
                                    previous_screen_list_keyboard_info=previous_screen_list_keyboard_info)
            return False

    # User does not have enough bounty
    if should_validate_user_has_amount and user.bounty < wager:
        await full_message_send(context, phrases.ACTION_INSUFFICIENT_BOUNTY, update=update,
                                add_delete_button=add_delete_button, inbound_keyboard=inbound_keyboard,
                                previous_screens=previous_screens,
                                previous_screen_list_keyboard_info=previous_screen_list_keyboard_info)
        return False

    # Wager less than minimum required
    if required_belly is not None and wager < required_belly:
        ot_text = phrases.ACTION_WAGER_LESS_THAN_MIN.format(get_belly_formatted(required_belly))
        await full_message_send(context, ot_text, update=update, add_delete_button=add_delete_button,
                                inbound_keyboard=inbound_keyboard, previous_screens=previous_screens,
                                previous_screen_list_keyboard_info=previous_screen_list_keyboard_info)
        return False

    return True


def round_belly_up(belly: float) -> int:
    """
    Rounds the belly up to the nearest given defined amount
    :param belly: The belly to round up
    :return: The rounded belly
    """
    return ceil(belly / Env.BELLY_UPPER_ROUND_AMOUNT.get_int()) * Env.BELLY_UPPER_ROUND_AMOUNT.get_int()


def get_next_bounty_reset_time() -> datetime.datetime:
    """
    Get the next bounty reset time
    :return: The next bounty reset time
    """

    start_datetime = datetime.datetime.now(datetime.timezone.utc)
    while True:
        # Get next execution of leaderboard
        next_run_time = get_next_run(Env.CRON_SEND_LEADERBOARD.get(), start_datetime=start_datetime)

        if should_reset_bounty(next_run_time):
            return next_run_time

        start_datetime = next_run_time + datetime.timedelta(seconds=1)


def should_reset_bounty(run_time: datetime) -> bool:
    """
    Checks if the bounty should be reset given the run time.
    Bounties are reset on the last leaderboard of every even month.

    :param run_time: The run time
    :return: Whether the bounty should be reset
    """

    # Adding 1 millisecond in case it's exactly midnight, else the next leaderboard will be considered as the
    # current one
    next_run_time = get_next_run(Env.CRON_SEND_LEADERBOARD.get(),
                                 start_datetime=run_time + datetime.timedelta(milliseconds=1))

    # Reset if this is the last leaderboard of the month and the month before was odd
    # or today is the first, and the month before was even
    return ((run_time.month != next_run_time.month and (run_time.month - 1) % 2 == 1)
            or (run_time.day == 1 and (run_time.month - 1) % 2 == 0))


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
        boss_type: BossType = get_boss_type(sender) if user_is_boss(sender) else get_boss_type(receiver)

        # Admins and legendary pirates, no tax
        if boss_type in (BossType.ADMIN, BossType.LEGENDARY_PIRATE):
            return 0
        elif boss_type is BossType.PIRATE_KING and user_is_boss(sender):
            tax = subtract_percentage_from_value(base_tax, Env.PIRATE_KING_TRANSACTION_TAX_DISCOUNT.get_float())

    # Send and receiver in same crew, percentage deduction
    if receiver is not None and sender.in_same_crew(receiver):
        tax = subtract_percentage_from_value(tax, Env.CREW_TRANSACTION_TAX_DISCOUNT.get_float())

    # Apply Devil Fruit ability
    tax = get_value(sender, DevilFruitAbilityType.TAX, tax)

    return tax


def reset_bounty_message_limit() -> None:
    """
    Reset the amount of bounty a user can gain from messages in a day
    """

    # If user location level is higher than 0, set their bounty_message_limit to Env.BELLY_DAILY_BASE_LIMIT +
    # a percentage corresponding to their location level (e.g. 10% for location level 1, 20% for location level 2, etc.)
    belly_daily_base_limit = Env.BELLY_DAILY_BASE_LIMIT.get_int()
    condition: tuple[bool, int] = (
        (User.location_level > 0),
        belly_daily_base_limit + (belly_daily_base_limit * User.location_level * 0.1))

    case_stmt = Case(None, [condition], belly_daily_base_limit)
    User.update(bounty_message_limit=case_stmt).execute()
