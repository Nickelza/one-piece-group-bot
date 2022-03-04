from telegram import Update

import constants as c
import resources.Environment as Env


def get_bounty_formatted(bounty: int) -> str:
    """
    Returns a formatted string of the bounty
    :param bounty: The bounty to format e.g. 1000000
    :return: The formatted string e.g. 1,000,000
    """

    return '{0:,}'.format(bounty)


def get_message_belly(update: Update) -> int:
    """
    Calculates how much bellys a message is worth
    :param update: Telegram update
    :return: How much bellys a message is worth
    """

    # Command message - No belly
    try:
        if update.message.text[0] in c.COMMAND_PREFIX_ALIASES:
            return 0
    except AttributeError:
        pass
    except TypeError:
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
            return int(Env.BELLY_BASE_MESSAGE.get())
    except AttributeError:
        pass

    final_belly: float = int(Env.BELLY_BASE_MESSAGE.get())

    # Char multiplier - Text messages which are not forwarded
    try:
        char_belly = (1 + (len(update.message.text) * float(Env.BELLY_CHARACTER_MULTIPLIER.get())))
        # Cap if it exceeds the max allowed per character count
        max_char_belly = float(Env.BELLY_CHARACTER_MAX_MULTIPLE.get()) * float(Env.BELLY_BASE_MESSAGE.get())
        char_belly = char_belly if char_belly <= max_char_belly else max_char_belly
        final_belly += char_belly
    except AttributeError:
        pass
    except TypeError:
        pass

    # Reply to channel post multiplier
    try:
        if update.message.reply_to_message.sender_chat.id == int(Env.OPD_CHANNEL_ID.get()):
            final_belly *= float(Env.BELLY_REPLY_TO_CHANNEL_POST_MULTIPLIER.get())
    except AttributeError:
        pass

    # Sticker multiplier
    try:
        if update.message.sticker is not None:
            final_belly *= float(Env.BELLY_STICKER_MULTIPLIER.get())
    except AttributeError:
        pass
    # Animation multiplier
    try:
        if update.message.animation is not None:
            final_belly *= float(Env.BELLY_ANIMATION_MULTIPLIER.get())
    except AttributeError:
        pass

    return round(int(final_belly), -3)  # Round to the nearest thousandth
