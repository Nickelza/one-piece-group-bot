from enum import StrEnum


class ContextDataKey(StrEnum):
    SAVED_MEDIA = 'saved_media'
    BOUNTY_LOAN_REPAY_AMOUNT = 'loan_repay_amount'
    CREATED_PREDICTION = 'created_prediction'
    INLINE_QUERY = 'inline_query'


class ContextDataType(StrEnum):
    BOT = 'bot'
    USER = 'user'
