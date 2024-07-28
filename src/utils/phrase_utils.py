from resources import phrases
from src.model.enums.Emoji import Emoji
from src.utils.string_utils import get_belly_formatted


def get_outcome_text(won: bool, amount: int) -> str:
    """
    Return the text to display when a player wins.
    :param won: True if the player won, False otherwise.
    :param amount: The amount of coins won.
    :return: The text to display.
    """

    return phrases.LOG_ITEM_DETAIL_OUTCOME_BELLY_TEXT.format(
        (Emoji.LOG_POSITIVE if won else Emoji.LOG_NEGATIVE),
        (phrases.TEXT_WON if won else phrases.TEXT_LOST),
        get_belly_formatted(amount) if won else get_belly_formatted(amount // 2),
    )
