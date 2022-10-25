import datetime
from math import ceil

from peewee import Case, fn
from telegram import Update
from telegram.ext import CallbackContext

import constants as c
import resources.Environment as Env
import resources.phrases as phrases
from src.model.User import User
from src.model.enums.Location import get_last_paradise, get_first_new_world
from src.service.cron_service import get_next_run
from src.service.location_service import reset_location
from src.service.message_service import full_message_send


def get_belly_formatted(belly: int) -> str:
    """
    Returns a formatted string of the belly
    :param belly: The belly to format e.g. 1000000
    :return: The formatted belly e.g. 1,000,000
    """

    return '{0:,}'.format(belly)


def get_message_belly(update: Update, user: User) -> int:
    """
    Calculates how much bellys a message is worth
    :param update: Telegram update
    :param user: The user who sent the message
    :return: How much bellys a message is worth
    """
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

    return round_belly_up(final_belly)


def reset_bounty(context: CallbackContext) -> None:
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
    remove_all_bets(context)

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

    if Env.SEND_MESSAGE_BOUNTY_RESET.get_bool():
        ot_text = phrases.BOUNTY_RESET
        full_message_send(context, ot_text, chat_id=Env.OPD_GROUP_ID.get_int())


def add_bounty(user: User, amount: float, context: CallbackContext = None, update: Update = None,
               should_update_location: bool = False, pending_belly_amount: int = 0) -> None:
    """
    Adds a bounty to a user
    :param context: Telegram context
    :param user: The user to add the bounty to
    :param amount: The amount to add to the bounty
    :param update: Telegram update
    :param should_update_location: Whether to update the user's location
    :param pending_belly_amount: How much of the amount is from pending belly, so not newly acquired. Will be used to
                                 calculate eventual taxes
    :return: The updated user
    """
    from src.service.location_service import update_location

    if amount <= 0:
        return

    # User is arrested, no bounty is gained
    if user.is_arrested():
        return

    user.bounty += amount

    # Update the user's location
    if should_update_location:
        if context is None:
            raise ValueError('Context is required when updating the location')
        update_location(user, context, update)


def add_region_bounty_bonus() -> None:
    """
    Adds a bounty percentage to all users based on their region

    :return: None
    """

    conditions: list[tuple[bool, int]] = [(User.location_level <= get_last_paradise().level,
                                           User.bounty +
                                           ((User.bounty * Env.PARADISE_BOUNTY_BONUS.get_float()) / 100)),
                                          (User.location_level >= get_first_new_world().level,
                                           User.bounty +
                                           ((User.bounty * Env.NEW_WORLD_BOUNTY_BONUS.get_float()) / 100))]
    case_stmt = Case(None, conditions)
    User.update(bounty=case_stmt).execute()


def add_crew_bounty_bonus() -> None:
    """
    Adds a bounty percentage to users in a crew with bounty higher than the crew average
    """

    condition: tuple[bool, int] = (
        User.bounty > (User.select(fn.Avg(User.bounty)).where(User.crew == User.crew).scalar()),
        User.bounty + ((User.bounty * Env.CREW_BOUNTY_BONUS.get_float()) / 100))

    case_stmt = Case(None, [condition], User.bounty)
    User.update(bounty=case_stmt).execute()


def get_wager_amount(amount_str: str) -> int:
    """
    Get the wager amount
    :param amount_str: The wager amount
    :return: The wager amount
    """
    amount_str = amount_str.strip().replace(',', '').replace('.', '')
    return int(amount_str)


def validate_wager(update: Update, context: CallbackContext, user: User, wager_str: str, required_belly: int) -> bool:
    """
    Validates the wager. Checks if the wager is a valid number, the user has enough belly, and if the wager is
    higher than the required belly
    :param update: Telegram update
    :param context: Telegram context
    :param user: The user to validate the wager for
    :param wager_str: The wager string
    :param required_belly: The required belly
    :return: Whether the wager is valid
    """

    try:
        wager: int = get_wager_amount(wager_str)
    except ValueError:
        full_message_send(context, phrases.ACTION_INVALID_WAGER_AMOUNT, update=update, add_delete_button=True)
        return False

    # User does not have enough bounty
    if user.bounty < wager:
        full_message_send(context, phrases.ACTION_INSUFFICIENT_BOUNTY, update=update, add_delete_button=True)
        return False

    # Wager less than minimum required
    if wager < required_belly:
        ot_text = phrases.ACTION_WAGER_LESS_THAN_MIN.format(get_belly_formatted(required_belly))
        full_message_send(context, ot_text, update=update, add_delete_button=True)
        return False

    return True


def round_belly_up(belly: float) -> int:
    """
    Rounds the belly up to the nearest given defined amount
    :param belly: The belly to round up
    :return: The rounded belly
    """
    return ceil(belly / Env.BELLY_UPPER_ROUND_AMOUNT.get_int()) * Env.BELLY_UPPER_ROUND_AMOUNT.get_int()


def get_next_bounty_reset_time() -> datetime:
    """
    Get the next bounty reset time
    :return: The next bounty reset time
    """

    start_datetime = datetime.datetime.now(datetime.timezone.utc)
    current_run_time = get_next_run(Env.CRON_SEND_LEADERBOARD.get())
    while True:
        # Get next execution of leaderboard
        next_run_time = get_next_run(Env.CRON_SEND_LEADERBOARD.get(), start_datetime=start_datetime)

        if should_reset_bounty(run_time=next_run_time):
            return current_run_time

        current_run_time = next_run_time
        start_datetime = next_run_time + datetime.timedelta(seconds=1)


def should_reset_bounty(run_time: datetime = None) -> bool:
    """
    Checks if the bounty should be reset given the run time
    :param run_time: The run time
    :return: Whether the bounty should be reset
    """

    if run_time is None:
        run_time = get_next_run(Env.CRON_SEND_LEADERBOARD.get())

    # Reset if this is the last leaderboard of the month
    return datetime.datetime.now().month != run_time.month
