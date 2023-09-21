from enum import StrEnum


class Emoji(StrEnum):
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
    CORRECT = '✅'
    CANCEL = '❌'
    DELETE = '🗑'
    DISABLED = '❌'
    DISABLED_EMPTY = '☑'
    CLOSE = '❌'
    REJECT = '❌'
    SETTINGS = '⚙'
    BACK = '🔙'
    STATUS = '📈'
    PRISONER = '🚫'
    YES = '✅'
    NO = '❌'
    LEFT_ARROW = '⬅'
    RIGHT_ARROW = '➡'
    PIN = '📌'
    RADIO_BUTTON = '🔘'
    MONEY = '💰'
    SAD = '😢'
    STATS = '📊'

    # Game
    WINNER = '🏆'
    LOSER = '💥'
    CONFETTI = '🎉'
    HEART = '❤'

    # Prediction
    PREDICTION_BET_WIN = '🏆'
    PREDICTION_BET_LOSE = '❗'
    PREDICTION_FEATURE_ENABLED = '🟢'
    PREDICTION_FEATURE_DISABLED = '🔴'
    PREDICTION_NEW = '🆕'
    PREDICTION_OPEN = '🔓'
    PREDICTION_CLOSED = '🔐'
    PREDICTION = '📊'

    # Rock Paper Scissors
    ROCK = '✊'
    PAPER = '🖐'
    SCISSORS = '✌'

    # Russian Roulette
    NOT_FIRED_CHAMBER = '🔴'
    FIRED_EMPTY_CHAMBER = '⭕'
    FIRED_BULLET_CHAMBER = '💥'
    CENTER_CHAMBER = '⚪'

    # Crew
    CREW = '🏴‍☠'

    # Logs
    LOGS = '📋'
    LOG_POSITIVE = '🟢'
    LOG_NEGATIVE = '🔴'
    LOG_DRAW = '🔵'
    LOG_NEUTRAL = '⚪'
    LOG_FORCED_END = '🟡'

    # Impel Down
    DISCIPLINARY_ACTION = '⛔'

    # Devil Fruit
    DEVIL_FRUIT = '🍎'
