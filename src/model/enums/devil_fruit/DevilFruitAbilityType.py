from enum import IntEnum, StrEnum


class Sign(StrEnum):
    """
    Enum for the sign of an ability.
    """

    POSITIVE = '+'
    NEGATIVE = '-'


class DevilFruitAbilityType(IntEnum):
    """
    Enum for the type of Devil Fruit ability type.
    """

    DOC_Q_COOLDOWN_DURATION = 1
    GAME_COOLDOWN_DURATION = 2
    FIGHT_COOLDOWN_DURATION = 3
    FIGHT_IMMUNITY_DURATION = 4
    FIGHT_DEFENSE_BOOST = 5
    PREDICTION_WAGER_REFUND = 6
    GIFT_TAX = 7

    def get_description(self) -> str:
        """
        Get the description of the devil fruit ability type
        :return: The description of the devil fruit ability type
        """

        return DEVIL_FRUIT_ABILITY_TYPE_DESCRIPTION_MAP[self]

    def get_sign(self) -> Sign:
        """
        Get the sign of the devil fruit ability type
        :return: The sign of the devil fruit ability type
        """

        return DEVIL_FRUIT_ABILITY_TYPE_SIGN_MAP[self]


DEVIL_FRUIT_ABILITY_TYPE_DESCRIPTION_MAP = {
    DevilFruitAbilityType.DOC_Q_COOLDOWN_DURATION: "Doc Q Cooldown",
    DevilFruitAbilityType.GAME_COOLDOWN_DURATION: "Challenge Cooldown",
    DevilFruitAbilityType.FIGHT_COOLDOWN_DURATION: "Fight Cooldown",
    DevilFruitAbilityType.FIGHT_IMMUNITY_DURATION: "Fight Immunity",
    DevilFruitAbilityType.FIGHT_DEFENSE_BOOST: "Fight Defense Boost",
    DevilFruitAbilityType.PREDICTION_WAGER_REFUND: "Prediction wager fund max refund",
    DevilFruitAbilityType.GIFT_TAX: "Gift Tax"
}

DEVIL_FRUIT_ABILITY_TYPE_SIGN_MAP = {
    DevilFruitAbilityType.DOC_Q_COOLDOWN_DURATION: Sign.NEGATIVE,
    DevilFruitAbilityType.GAME_COOLDOWN_DURATION: Sign.NEGATIVE,
    DevilFruitAbilityType.FIGHT_COOLDOWN_DURATION: Sign.NEGATIVE,
    DevilFruitAbilityType.FIGHT_IMMUNITY_DURATION: Sign.POSITIVE,
    DevilFruitAbilityType.FIGHT_DEFENSE_BOOST: Sign.POSITIVE,
    DevilFruitAbilityType.PREDICTION_WAGER_REFUND: Sign.POSITIVE,
    DevilFruitAbilityType.GIFT_TAX: Sign.NEGATIVE
}
