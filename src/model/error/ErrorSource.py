from enum import Enum


class ErrorSource(Enum):
    """
    Enum for error source
    """
    GROUP_CHAT = 'G'
    PRIVATE_CHAT = 'P'
    ADMIN_CHAT = 'A'
    TG_REST = 'T'
