from resources import phrases
from src.model.DailyReward import DailyReward
from src.model.enums.Location import get_last_new_world, get_first_new_world
from src.model.enums.daily_reward.DailyRewardBonus import DailyRewardBonus
from src.model.enums.daily_reward.DailyRewardLimitation import DailyRewardLimitation
from src.service.string_service import get_belly_formatted


def get_text(reward: DailyReward) -> str:
    """
    Get the text for the reward
    :param reward: The reward
    :return: The text
    """

    bonus_text = ""
    bonus_list: list[DailyRewardBonus] = DailyRewardBonus.from_string(reward.bonus_list)
    if len(bonus_list) == 0:
        match DailyRewardLimitation(reward.limitation):
            case DailyRewardLimitation.LOCATION_PARADISE:
                bonus_text = phrases.DAILY_REWARD_BONUS_LIMITATION_LOCATION_PARADISE.format(
                    get_belly_formatted(get_first_new_world().required_bounty)
                )
            case DailyRewardLimitation.LOCATION_NEW_WORLD:
                bonus_text = phrases.DAILY_REWARD_BONUS_LIMITATION_LOCATION_NEW_WORLD.format(
                    get_belly_formatted(get_last_new_world().required_bounty)
                )
            case DailyRewardLimitation.ARRESTED:
                bonus_text = phrases.DAILY_REWARD_BONUS_LIMITATION_ARRESTED
            case _:
                raise ValueError("Invalid limitation")
    else:
        for bonus in bonus_list:
            bonus_text += phrases.DAILY_REWARD_BONUS.format(
                bonus.get_description(), bonus.value, get_belly_formatted(bonus.amount)
            )

    return phrases.DAILY_REWARD.format(
        get_belly_formatted(reward.base_amount),
        bonus_text,
        get_belly_formatted(reward.total_amount),
    )
