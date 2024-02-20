from enum import IntEnum

from resources import phrases


class DevilFruitCategory(IntEnum):
    """
    Enum for the category of a devil fruit
    """

    ZOAN = 3
    ANCIENT_ZOAN = 4
    MYTHICAL_ZOAN = 5
    SMILE = 6

    def get_description(self) -> str:
        """
        Get the description of the devil fruit category
        :return: The description of the devil fruit category
        """

        return DEVIL_FRUIT_CATEGORY_DESCRIPTION_MAP[self]


DEVIL_FRUIT_CATEGORY_DESCRIPTION_MAP = {
    DevilFruitCategory.ZOAN: phrases.DEVIL_FRUIT_CATEGORY_DESCRIPTION_ZOAN,
    DevilFruitCategory.ANCIENT_ZOAN: phrases.DEVIL_FRUIT_CATEGORY_DESCRIPTION_ANCIENT_ZOAN,
    DevilFruitCategory.MYTHICAL_ZOAN: phrases.DEVIL_FRUIT_CATEGORY_DESCRIPTION_MYTHICAL_ZOAN,
    DevilFruitCategory.SMILE: phrases.DEVIL_FRUIT_CATEGORY_DESCRIPTION_SMILE,
}
