from enum import IntEnum


class RussianRouletteChamberStatus(IntEnum):
    """
    Enum for the status of a Russian Roulette chamber.
    """
    NOT_FIRED = 1
    FIRED = 2
