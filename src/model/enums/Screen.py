from enum import Enum


class Screen(Enum):
    UNKNOWN = '0'

    GRP_USER_STATUS = 'G1'
    GRP_DOC_Q_GAME = 'G2'
    GRP_CHANGE_REGION = 'G3'
    GRP_FIGHT = 'G4'
    GRP_GAME = 'G5'
    GRP_GAME_SELECTION = 'G6'
    GRP_GAME_OPPONENT_CONFIRMATION = 'G7'
    GRP_ROCK_PAPER_SCISSORS_GAME = 'G8'

    # Deprecated
    GRP_SHOW_BOUNTY = 'G-1'

    PVT_START = 'P1'
    PVT_SETTINGS = 'P2'
    PVT_SETTINGS_LOCATION_UPDATE = 'P3'

    ADM_SAVE_MEDIA = 'A1'
