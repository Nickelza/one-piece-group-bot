from enum import StrEnum


class Screen(StrEnum):
    UNKNOWN = '0'

    GRP_USER_STATUS = 'G1'
    GRP_DOC_Q_GAME = 'G2'
    GRP_CHANGE_REGION = 'G3'
    GRP_FIGHT = 'G4'
    GRP_GAME = 'G5'
    GRP_GAME_SELECTION = 'G6'
    GRP_GAME_OPPONENT_CONFIRMATION = 'G7'
    GRP_ROCK_PAPER_SCISSORS_GAME = 'G8'
    GRP_RUSSIAN_ROULETTE_GAME = 'G9'
    GRP_PREDICTION_BET = 'G10'
    GRP_PREDICTION_BET_REMOVE = 'G11'
    GRP_PREDICTION_BET_STATUS = 'G12'
    GRP_CREW_JOIN = 'G13'
    GRP_CREW_INVITE = 'G14'
    GRP_SILENCE = 'G15'
    GRP_SILENCE_END = 'G16'
    GRP_SPEAK = 'G17'
    GRP_BOUNTY_GIFT = 'G18'
    GRP_DEVIL_FRUIT_COLLECT = 'G19'
    GRP_SETTINGS = 'G20'

    PVT_START = 'P1'
    PVT_SETTINGS = 'P2'
    PVT_SETTINGS_LOCATION_UPDATE = 'P3'  # Deprecated
    PVT_USER_STATUS = 'P4'
    PVT_CREW = 'P5'
    PVT_CREW_CREATE_OR_EDIT = 'P6'
    PVT_CREW_LEAVE = 'P7'
    PVT_CREW_DISBAND = 'P8'
    PVT_CREW_MEMBER = 'P9'
    PVT_CREW_MEMBER_REMOVE = 'P10'
    PVT_SETTINGS_NOTIFICATIONS = 'P11'
    PVT_SETTINGS_NOTIFICATIONS_TYPE = 'P12'
    PVT_SETTINGS_NOTIFICATIONS_TYPE_EDIT = 'P13'
    PVT_LOGS = 'P14'
    PVT_LOGS_TYPE = 'P15'
    PVT_LOGS_TYPE_DETAIL = 'P16'
    PVT_PREDICTION = 'P17'
    PVT_PREDICTION_DETAIL = 'P18'
    PVT_PREDICTION_DETAIL_PLACE_BET = 'P19'
    PVT_PREDICTION_DETAIL_PLACE_BET_SEND_AMOUNT = 'P20'
    PVT_PREDICTION_DETAIL_REMOVE_BET = 'P21'
    PVT_PREDICTION_DETAIL_REMOVE_BET_CONFIRM = 'P22'
    PVT_DEVIL_FRUIT = 'P23'
    PVT_DEVIL_FRUIT_DETAIL = 'P24'
    PVT_DEVIL_FRUIT_DETAIL_EAT = 'P25'
    PVT_DEVIL_FRUIT_DETAIL_TRADE = 'P26'
    PVT_DEVIL_FRUIT_DETAIL_DISCARD = 'P27'
