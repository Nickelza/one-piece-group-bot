import json
from enum import IntEnum

from resources import phrases


class DailyRewardBonusType(IntEnum):
    STREAK = 1
    LOCATION = 2
    CREW = 3
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


DAILY_BONUS_REWARD_TYPE_DESCRIPTION = {
    DailyRewardBonusType.STREAK: phrases.DAILY_REWARD_BONUS_DESCRIPTION_STREAK,
    DailyRewardBonusType.LOCATION: phrases.DAILY_REWARD_BONUS_DESCRIPTION_LOCATION,
    DailyRewardBonusType.CREW: phrases.DAILY_REWARD_BONUS_DESCRIPTION_CREW,
    DailyRewardBonusType.CREW_MVP: phrases.DAILY_REWARD_BONUS_DESCRIPTION_CREW_MVP,
}
