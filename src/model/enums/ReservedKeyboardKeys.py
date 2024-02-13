from enum import StrEnum


class ReservedKeyboardKeys(StrEnum):
    SCREEN = "sc"
    PREVIOUS_SCREEN = "psc"
    DELETE = "del"
    IN_EDIT_ID = "z"
    SCREEN_STEP = "y"
    TOGGLE = "x"
    PAGE = "w"
    CONFIRM = "v"
    AUTHORIZED_USER = "u"
    RESET = "t"
    FILTER = "s"
    NUMBER = "r"
    DIRECT_ITEM = "q"
    CONTEXT = "ctx"

    # Not unique
    DEFAULT_PRIMARY_KEY = "a"
    DEFAULT_SECONDARY_KEY = "b"
