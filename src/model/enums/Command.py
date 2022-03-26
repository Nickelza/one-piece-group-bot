from enum import Enum


class Command(Enum):
    """
    Enum of commands that can be used.
    """

    ND = None

    # Private
    PVT_START = "start"

    # Group
    GRP_DOC_Q_GAME = 'docq'
    GRP_USER_STATUS = 'status'
    GRP_CHANGE_REGION_NEW_WORLD = 'newworld'
    GRP_CHANGE_REGION_PARADISE = 'paradise'
    # Deprecated
    GRP_SHOW_BOUNTY = 'bounty'

    # Admin chat
    ADM_SAVE_MEDIA = 'savemedia'

    def get_formatted(self):
        """
        Returns the command formatted for the text display.
        """
        return '`/{}`'.format(self.value)
