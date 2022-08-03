from strenum import StrEnum


class TgRestObjectType(StrEnum):
    """
    Enum for the object type of Telegram REST API request.
    """
    PREDICTION = 'prediction'
