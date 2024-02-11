from enum import IntEnum, StrEnum

from resources import phrases


class Sign(StrEnum):
    """
    Enum for the sign of an ability.
    """

    POSITIVE = "+"
    NEGATIVE = "-"


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
    GIFT_LOAN_TAX = 7
    INCOME_TAX = 8
    PLUNDER_COOLDOWN_DURATION = 9
    PLUNDER_IMMUNITY_DURATION = 10
    PLUNDER_SENTENCE_DURATION = 11

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
    DevilFruitAbilityType.DOC_Q_COOLDOWN_DURATION: phrases.ABILITY_TYPE_DOC_Q_COOLDOWN_DURATION,
    DevilFruitAbilityType.GAME_COOLDOWN_DURATION: phrases.ABILITY_TYPE_GAME_COOLDOWN_DURATION,
    DevilFruitAbilityType.FIGHT_COOLDOWN_DURATION: phrases.ABILITY_TYPE_FIGHT_COOLDOWN_DURATION,
    DevilFruitAbilityType.FIGHT_IMMUNITY_DURATION: phrases.ABILITY_TYPE_FIGHT_IMMUNITY_DURATION,
    DevilFruitAbilityType.FIGHT_DEFENSE_BOOST: phrases.ABILITY_TYPE_FIGHT_DEFENSE_BOOST,
    DevilFruitAbilityType.PREDICTION_WAGER_REFUND: phrases.ABILITY_TYPE_PREDICTION_WAGER_REFUND,
    DevilFruitAbilityType.GIFT_LOAN_TAX: phrases.ABILITY_TYPE_GIFT_LOAN_TAX,
    DevilFruitAbilityType.INCOME_TAX: phrases.ABILITY_TYPE_INCOME_TAX,
    DevilFruitAbilityType.PLUNDER_COOLDOWN_DURATION: (
        phrases.ABILITY_TYPE_PLUNDER_COOLDOWN_DURATION
    ),
    DevilFruitAbilityType.PLUNDER_IMMUNITY_DURATION: (
        phrases.ABILITY_TYPE_PLUNDER_IMMUNITY_DURATION
    ),
    DevilFruitAbilityType.PLUNDER_SENTENCE_DURATION: (
        phrases.ABILITY_TYPE_PLUNDER_SENTENCE_DURATION
    ),
}

DEVIL_FRUIT_ABILITY_TYPE_SIGN_MAP = {
    DevilFruitAbilityType.DOC_Q_COOLDOWN_DURATION: Sign.NEGATIVE,
    DevilFruitAbilityType.GAME_COOLDOWN_DURATION: Sign.NEGATIVE,
    DevilFruitAbilityType.FIGHT_COOLDOWN_DURATION: Sign.NEGATIVE,
    DevilFruitAbilityType.FIGHT_IMMUNITY_DURATION: Sign.POSITIVE,
    DevilFruitAbilityType.FIGHT_DEFENSE_BOOST: Sign.POSITIVE,
    DevilFruitAbilityType.PREDICTION_WAGER_REFUND: Sign.POSITIVE,
    DevilFruitAbilityType.GIFT_LOAN_TAX: Sign.NEGATIVE,
    DevilFruitAbilityType.INCOME_TAX: Sign.NEGATIVE,
    DevilFruitAbilityType.PLUNDER_COOLDOWN_DURATION: Sign.NEGATIVE,
    DevilFruitAbilityType.PLUNDER_IMMUNITY_DURATION: Sign.POSITIVE,
    DevilFruitAbilityType.PLUNDER_SENTENCE_DURATION: Sign.NEGATIVE,
}
