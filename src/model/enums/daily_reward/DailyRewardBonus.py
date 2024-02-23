import json
from enum import IntEnum

from resources import phrases


class DailyRewardBonusType(IntEnum):
    STREAK = 1
    LOCATION = 2
    CREW_LEVEL = 3
    CREW_MVP = 4

    def get_description(self) -> str:
        """
        Get the description for the bonus type
        :return: The description
        """
        return DAILY_BONUS_REWARD_TYPE_DESCRIPTION[self]


class DailyRewardBonus:
    def __init__(self, bonus_type: DailyRewardBonusType, value: int, amount: int):
        self.bonus_type = bonus_type
        self.value = value
        self.amount = amount

    def get_type(self) -> DailyRewardBonusType:
        """
        Get the bonus type
        :return: The bonus type
        """
        return DailyRewardBonusType(self.bonus_type)

    @staticmethod
    def from_string(bonus_list: str) -> list["DailyRewardBonus"]:
        """
        Get the daily reward bonus list from a string
        :param bonus_list: The string
        :return: The bonus list
        """
        if not bonus_list:
            return []

        bonus_list_json = json.loads(bonus_list)
        return [DailyRewardBonus(**bonus) for bonus in bonus_list_json]

    def get_description(self) -> str:
        """
        Get the description for the bonus
        :return: The description
        """
        return DAILY_BONUS_REWARD_TYPE_DESCRIPTION[self.get_type()]

    def get_explanation(self) -> str:
        """
        Get the explanation for the bonus
        :return: The explanation
        """
        return DAILY_BONUS_REWARD_TYPE_EXPLANATION[self.get_type()]


DAILY_BONUS_REWARD_TYPE_DESCRIPTION = {
    DailyRewardBonusType.STREAK: phrases.DAILY_REWARD_BONUS_DESCRIPTION_STREAK,
    DailyRewardBonusType.LOCATION: phrases.DAILY_REWARD_BONUS_DESCRIPTION_LOCATION,
    DailyRewardBonusType.CREW_LEVEL: phrases.DAILY_REWARD_BONUS_DESCRIPTION_CREW_LEVEL,
    DailyRewardBonusType.CREW_MVP: phrases.DAILY_REWARD_BONUS_DESCRIPTION_CREW_MVP,
}

DAILY_BONUS_REWARD_TYPE_EXPLANATION = {
    DailyRewardBonusType.STREAK: phrases.DAILY_REWARD_BONUS_DESCRIPTION_STREAK_EXPLANATION,
    DailyRewardBonusType.LOCATION: phrases.DAILY_REWARD_BONUS_DESCRIPTION_LOCATION_EXPLANATION,
    DailyRewardBonusType.CREW_LEVEL: phrases.DAILY_REWARD_BONUS_DESCRIPTION_CREW_LEVEL_EXPLANATION,
    DailyRewardBonusType.CREW_MVP: phrases.DAILY_REWARD_BONUS_DESCRIPTION_CREW_MVP_EXPLANATION,
}
