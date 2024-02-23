from enum import StrEnum

import resources.Environment as Env
from src.utils.math_utils import get_random_key_based_on_probability


class DailyRewardPrizeType(StrEnum):
    BELLY = "belly"
    SMILE = "smile"

    @staticmethod
    def get_random() -> "DailyRewardPrizeType":
        """
        Get a random prize type by probability percentage
        :return: The random prize type
        """

        return get_random_key_based_on_probability(DAILY_REWARD_PRIZE_TYPE_PROBABILITY)


DAILY_REWARD_PRIZE_TYPE_PROBABILITY = {
    DailyRewardPrizeType.BELLY: Env.DAILY_REWARD_PRIZE_BELLY_PERCENTAGE.get_int(),
    DailyRewardPrizeType.SMILE: Env.DAILY_REWARD_PRIZE_SMILE_PERCENTAGE.get_int(),
}
