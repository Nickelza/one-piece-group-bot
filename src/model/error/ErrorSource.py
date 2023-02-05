from strenum import StrEnum


class ErrorSource(StrEnum):
    """
    Enum for error source
    """
    GROUP_CHAT = 'G'
    PRIVATE_CHAT = 'P'
    TG_REST = 'T'
    COMMON = 'C'
