from enum import Enum


class ReservedKeyboardKeys(str, Enum):
    SCREEN = 'sc'
    PREVIOUS_SCREEN = 'psc'
    DELETE = 'del'
    IN_EDIT_ID = 'z'
    SCREEN_STEP = 'y'
    TOGGLE = 'x'
    PAGE = 'w'
    CONFIRM = 'v'
    AUTHORIZED_USER = 'u'

    # Not unique
    DEFAULT_PRIMARY_KEY = 'a'
