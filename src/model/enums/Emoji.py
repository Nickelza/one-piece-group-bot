from enum import StrEnum


class Emoji(StrEnum):
    """
    Enum class for Emoji
    """

    # Doc Q Game
    DOC_Q_GAME_OPTION = "🍎"
    DOC_Q_GAME_CORRECT_OPTION = "🍏"
    DOC_Q_GAME_WIN = "🎉"
    DOC_Q_GAME_LOSE = "💥"

    # Leaderboard
    LEADERBOARD_PIRATE_KING = "🔱"
    LEADERBOARD_EMPEROR = "👑"
    LEADERBOARD_FIRST_MATE = "🥇"
    LEADERBOARD_SUPERNOVA = "🌟"
    LEADERBOARD_ROOKIE = "👤"
    LEADERBOARD_ADMIN = "🎖️"
    LEADERBOARD_LEGENDARY_PIRATE = "💎"
    LEADERBOARD_WARLORD = "⚔"

    # Fight
    FIGHT = "⚔"
    RETREAT = "🏳️"
    PLUNDER = "🥷️"

    # Other
    ACCEPT = "✅"
    ENABLED = "✅"
    CORRECT = "✅"
    CANCEL = "❌"
    DELETE = "🗑"
    DISABLED = "❌"
    DISABLED_EMPTY = "☑"
    CLOSE = "❌"
    REJECT = "❌"
    SETTINGS = "⚙"
    BACK = "🔙"
    STATUS = "📈"
    PRISONER = "🚫"
    YES = "✅"
    NO = "❌"
    LEFT_ARROW = "⬅"
    RIGHT_ARROW = "➡"
    PIN = "📌"
    RADIO_BUTTON = "🔘"
    MONEY = "💰"
    SAD = "😢"
    STATS = "📊"
    WARNING = "⚠"
    NEW = "🆕"
    GLOBE = "🌎"
    SAVE = "💾"
    CREATE = "➕"
    CHANGE = "🔄"
    SHARE = "📤"
    GROUP = "👥"
    USER = "👤"
    NULL = ""
    DICE = "🎲"
    WARNING_STRONG = "‼"
    RED = "🔴"
    YELLOW = "🟡"
    GREEN = "🟢"
    SEARCH = "🔍"
    RESET = "🔄"
    SHOP = "🛒"
    GIFT = "🎁"
    INFO = "ℹ"
    HELP = "❓"

    # Game
    WINNER = "🏆"
    LOSER = "💥"
    CONFETTI = "🎉"
    BLUE_HEART = "💙"

    # Prediction
    PREDICTION_BET_WIN = "🏆"
    PREDICTION_BET_LOSE = "❗"
    PREDICTION_FEATURE_ENABLED = "🟢"
    PREDICTION_FEATURE_DISABLED = "🔴"
    PREDICTION_NEW = "🆕"
    PREDICTION_OPEN = "🔓"
    PREDICTION_CLOSED = "🔐"
    PREDICTION = "📊"
    PREDICTION_CUT_OFF = "✂"

    # Rock Paper Scissors
    ROCK = "✊"
    PAPER = "🖐"
    SCISSORS = "✌"

    # Russian Roulette
    NOT_FIRED_CHAMBER = "🔴"
    FIRED_EMPTY_CHAMBER = "⭕"
    FIRED_BULLET_CHAMBER = "💥"
    CENTER_CHAMBER = "⚪"

    # Crew
    CREW = "🏴‍☠"

    # Logs
    LOGS = "📋"
    LOG_POSITIVE = "🟢"
    LOG_NEGATIVE = "🔴"
    LOG_DRAW = "🔵"
    LOG_NEUTRAL = "⚪"
    LOG_FORCED_END = "🟡"
    LOG_BLUE = "🔵"
    LOG_PURPLE = "🟣"
    LOG_YELLOW = "🟡"

    # Impel Down
    DISCIPLINARY_ACTION = "⛔"

    # Devil Fruit
    DEVIL_FRUIT = "🍎"
