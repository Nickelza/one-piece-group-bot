from enum import StrEnum


class PredictionType(StrEnum):
    """

    Enum class for predictions type
    """

    VERSUS = "Versus"
    PREFERENCE = "Preference"
    EVENT = "Event"
    USER = "User"
