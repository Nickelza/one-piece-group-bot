from enum import StrEnum


class ContextDataKey(StrEnum):
    SAVED_MEDIA = "saved_media"
    BOUNTY_LOAN_REPAY_AMOUNT = "loan_repay_amount"
    CREATED_PREDICTION = "created_prediction"
    INLINE_QUERY = "inline_query"
    PAST_MESSAGES_DATE = "past_messages_date"
    FILTER = "filter"
    INBOUND_KEYBOARD = "inbound_keyboard"
    KEYBOARD_DATA = "keyboard_data"
    AMOUNT = "amount"
    LAST_REQUEST = "last_request"
    GAME_OPPONENT_TIMEOUT = "game_opponent_timeout"


class ContextDataType(StrEnum):
    BOT = "bot"
    USER = "user"
