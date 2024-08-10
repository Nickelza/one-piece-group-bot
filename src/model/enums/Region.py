from enum import IntEnum


class Region(IntEnum):
    """
    Enum class for region.
    """

    ND = 0
    PARADISE = 1
    NEW_WORLD = 2

    def get_other(self):
        """
        Returns the other region.
        """
        if self == Region.PARADISE:
            return Region.NEW_WORLD

        if self == Region.NEW_WORLD:
            return Region.PARADISE

        raise ValueError("Invalid region")
