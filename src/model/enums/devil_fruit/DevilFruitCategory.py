from enum import IntEnum


class DevilFruitCategory(IntEnum):
    """
    Enum for the category of a devil fruit
    """
    ZOAN = 3
    ANCIENT_ZOAN = 4
    MYTHICAL_ZOAN = 5

    def get_description(self) -> str:
        """
        Get the description of the devil fruit category
        :return: The description of the devil fruit category
        """

        return DEVIL_FRUIT_CATEGORY_DESCRIPTION_MAP[self]


DEVIL_FRUIT_CATEGORY_DESCRIPTION_MAP = {
    DevilFruitCategory.ZOAN: "Zoan",
    DevilFruitCategory.ANCIENT_ZOAN: "Ancient Zoan",
    DevilFruitCategory.MYTHICAL_ZOAN: "Mythical Zoan"
}
