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

    # Callback query - No belly
    try:
        if update.callback_query.data is not None:
            return 0
    except AttributeError:
        pass

    # Forwarded message - Base belly
    try:
        if update.message.forward_from is not None:
            return int(Env.BASE_MESSAGE_BELLY.get())
    except AttributeError:
        pass

    final_belly: float = int(Env.BASE_MESSAGE_BELLY.get())

    # Char multiplier - Text messages which are not forwarded
    try:
        final_belly *= (1 + (len(update.message.text) * float(Env.CHARACTER_BELLY_MULTIPLIER.get())))
    except AttributeError:
        pass

    # Reply to channel post multiplier
    try:
        if update.message.reply_to_message.sender_chat.id == int(Env.OPD_CHANNEL_ID.get()):
            final_belly *= float(Env.REPLY_TO_CHANNEL_POST_MULTIPLIER.get())
    except AttributeError:
        pass

    return int(final_belly)
