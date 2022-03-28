from peewee import Case
from telegram import Update
from telegram.ext import CallbackContext

import constants as c
import resources.Environment as Env
import resources.phrases as phrases
from src.model.User import User
from src.model.enums.Location import get_last_paradise, get_first_new_world
from src.service.location_service import reset_location
from src.service.message_service import full_message_send


def get_bounty_formatted(bounty: int) -> str:
    """
    Returns a formatted string of the bounty
    :param bounty: The bounty to format e.g. 1000000
    :return: The formatted string e.g. 1,000,000
    """

    return '{0:,}'.format(bounty)


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

    return round(int(final_belly), -3)  # Round to the nearest thousandth


def reset_bounty(context: CallbackContext) -> None:
    """
    Resets the bounty to 0 for all users
    :return: None
    """
    User.update(bounty=0).execute()

    # Reset location
    reset_location()

    ot_text = phrases.BOUNTY_RESET
    full_message_send(context, ot_text, chat_id=Env.OPD_GROUP_ID.get_int())


def add_bounty(context: CallbackContext, user: User, amount: float, update: Update = None,
               should_update_location: bool = True) -> User:
    """
    Adds a bounty to a user
    :param context: Telegram context
    :param user: The user to add the bounty to
    :param amount: The amount to add to the bounty
    :param update: Telegram update
    :param should_update_location: Whether to update the user's location
    :return: The updated user
    """
    from src.service.location_service import update_location

    if amount <= 0:
        return user

    user.bounty += amount

    # Update the user's location
    if should_update_location:
        update_location(context, user, update, send_update_message=True)

    return user


def add_region_bounty(context: CallbackContext) -> None:
    """
    Adds a bounty percentage to all users based on their region
    :param context: Telegram context
    :return: None
    """

    conditions: list[tuple[bool, int]] = [(User.location_level <= get_last_paradise().level,
                                           User.bounty +
                                           ((User.bounty * Env.LOCATION_PARADISE_BOUNTY_INCREMENT.get_float()) / 100)),
                                          (User.location_level >= get_first_new_world().level,
                                           User.bounty +
                                           ((User.bounty * Env.LOCATION_NEW_WORLD_BOUNTY_INCREMENT.get_float()) / 100))]
    case_stmt = Case(None, conditions)
    User.update(bounty=case_stmt).execute()
