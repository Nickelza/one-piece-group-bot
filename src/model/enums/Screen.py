from enum import Enum


class Screen(Enum):
    UNKOWN = '0'

    GRP_USER_STATUS = 'G1'
    GRP_DOC_Q_GAME = 'G2'
    GRP_CHANGE_REGION = 'G3'
    GRP_FIGHT = 'G4'
    # Deprecated
    GRP_SHOW_BOUNTY = 'G-1'

    PVT_START = 'P1'

    ADM_SAVE_MEDIA = 'A1'
