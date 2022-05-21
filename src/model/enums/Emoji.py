from enum import Enum


class Emoji(Enum):
    """
    Enum class for Emoji
    """

    # Doc Q Game
    DOC_Q_GAME_OPTION = '🍎'
    DOC_Q_GAME_CORRECT_OPTION = '🍏'
    DOC_Q_GAME_WIN = '🎉'
    DOC_Q_GAME_LOSE = '💥'

    # Leaderboard
    LEADERBOARD_PIRATE_KING = '🔱'
    LEADERBOARD_EMPEROR = '👑'
    LEADERBOARD_FIRST_MATE = '🥇'
    LEADERBOARD_SUPERNOVA = '🌟'
    LEADERBOARD_ROOKIE = '👤'

    # Fight
    FIGHT = '⚔'
    RETREAT = '🏳️'

    # Other
    ACCEPT = '✅'
    ENABLED = '✅'
    CANCEL = '❌'
    DISABLED = '❌'
    REJECT = '❌'
    SETTINGS = '⚙'
    BACK = '🔙'

    # Rock Paper Scissors
    ROCK = '✊'
    PAPER = '🖐'
    SCISSORS = '✌'
