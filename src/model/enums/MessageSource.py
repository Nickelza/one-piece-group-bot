from enum import Enum


class MessageSource(Enum):
    """
    Enum class for message source.
    """
    ND = 'ND'
    PRIVATE = 'P'
    GROUP = 'G'
    ADMIN = 'A'
