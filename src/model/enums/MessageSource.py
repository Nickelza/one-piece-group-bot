from enum import StrEnum


class MessageSource(StrEnum):
    """
    Enum class for message source.
    """
    ND = 'ND'
    PRIVATE = 'P'
    GROUP = 'G'
    TG_REST = 'T'
    INLINE_QUERY = 'I'
