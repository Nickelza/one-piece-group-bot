from enum import Enum


class Command(Enum):
    """
    Enum of commands that can be used.
    """

    # Private
    PVT_START = "start"

    # Group
    GRP_DOC_Q_GAME = 'docq'
    GRP_BOUNTY = 'bounty'

    # Admin chat
    ADM_SAVE_MEDIA = 'savemedia'
