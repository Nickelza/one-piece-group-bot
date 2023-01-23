from strenum import StrEnum


class TgRestObjectType(StrEnum):
    """
    Enum for the object type of Telegram REST API request.
    """
    PREDICTION = 'prediction'
    PRIVATE_MESSAGE = 'private_message'
    IMPEL_DOWN_NOTIFICATION = 'impel_down_notification'
    DEVIL_FRUIT_AWARD = 'devil_fruit_award'
