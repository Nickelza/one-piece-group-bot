import datetime

from peewee import *

import resources.Environment as Env
from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.daily_reward.DailyRewardBonus import DailyRewardBonus, DailyRewardBonusType
from src.model.enums.daily_reward.DailyRewardLimitation import DailyRewardLimitation
from src.model.enums.daily_reward.DailyRewardPrizeSource import DailyRewardPrizeSource
from src.model.enums.daily_reward.DailyRewardPrizeType import DailyRewardPrizeType
from src.service.date_service import get_day_in_past, is_same_day
from src.utils.math_utils import get_value_from_percentage


class DailyReward(BaseModel):
    """
    DailyReward class
    """

    id: int | PrimaryKeyField = PrimaryKeyField()
    user: User | ForeignKeyField = ForeignKeyField(User, backref="daily_bonuses")
    date: datetime.datetime | DateTimeField = DateTimeField(default=datetime.datetime.now)
    base_amount: int | BigIntegerField = BigIntegerField()
    bonus_list: str | TextField = TextField()
    total_amount: int | BigIntegerField = BigIntegerField()
    streak_count: int | IntegerField = IntegerField()
    limitation: str | DailyRewardLimitation = CharField(max_length=20)
    prize_type: DailyRewardPrizeType | CharField = CharField(max_length=20, null=True)
    prize_value: str | CharField = CharField(max_length=50, null=True)
    prize_source: DailyRewardPrizeSource | CharField = CharField(max_length=20, null=True)
    group_chat: GroupChat | ForeignKeyField = ForeignKeyField(GroupChat, backref="daily_rewards")
    message_id: int | IntegerField = IntegerField(null=True)
    message_id_prize: int | IntegerField = IntegerField(null=True)

    class Meta:
        db_table = "daily_reward"

    @staticmethod
    def reset():
        """
        Reset the daily rewards
        """

        User.reset_daily_reward()

    @staticmethod
    def get_daily_reward_reset_times():
        """
        Get how many times daily reward is reset during the day
        """
        cron_expression = Env.CRON_DAILY_REWARD.get()
        cron_parts = cron_expression.split()

        # Every hour, so 24 times
        if cron_parts[1] == "*":
            return 24

        # Every x hours
        if "*/" in cron_parts[1]:
            return 24 // int(cron_parts[1].split("/")[1])

        # Once
        return 1

    @staticmethod
    def get_next_reward_time() -> datetime.datetime:
        from src.service.date_service import get_next_run

        return get_next_run(Env.CRON_DAILY_REWARD.get())

    @staticmethod
    def get_remaining_time_to_next_reward() -> str:
        from src.service.date_service import get_remaining_duration

        return get_remaining_duration(DailyReward.get_next_reward_time())

    @staticmethod
    def get_last_streak_reward(user: User) -> "DailyReward":
        """
        Get the last streak reward for the user
        :param user: The user
        :return: The last streak reward
        """

        return (
            DailyReward.select()
            .where((DailyReward.user == user) & (DailyReward.date >= get_day_in_past(1)))
            .order_by(DailyReward.date.desc())
            .first()
        )

    @staticmethod
    def get_user_streak_count(user: User) -> int:
        """
        Get the user's streak count
        :param user: The user
        :return: The streak count
        """

        # Get the last reward that is from yesterday or later
        last_streak_reward = DailyReward.get_last_streak_reward(user)

        if last_streak_reward is None:
            return 1

        streak_count = last_streak_reward.streak_count

        # Is from yesterday, add one
        if is_same_day(last_streak_reward.date, get_day_in_past(1)):
            return streak_count + 1

        return last_streak_reward.streak_count

    @staticmethod
    def get_bonuses_for_user(user: User, base_amount: int) -> list[DailyRewardBonus]:
        """
        Get the bonus_list for the user
        :param user: The user
        :param base_amount: The base amount
        :return: The bonus_list
        """

        bonus_list: list[DailyRewardBonus] = []
        total_amount = base_amount

        for bonus_type in list(DailyRewardBonusType):
            match bonus_type:
                # Streak
                case DailyRewardBonusType.STREAK:
                    value = Env.DAILY_REWARD_BONUS_BASE_STREAK.get_int()
                    streak_count = min(
                        DailyReward.get_user_streak_count(user),
                        Env.DAILY_REWARD_BONUS_MAX_STREAK.get_int(),
                    )
                    value *= streak_count

                # Location
                case DailyRewardBonusType.LOCATION:
                    value = Env.DAILY_REWARD_BONUS_BASE_LOCATION.get_int() * user.location_level

                # Crew member
                case DailyRewardBonusType.CREW:
                    if not user.is_crew_member():
                        continue
                    value = Env.DAILY_REWARD_BONUS_CREW.get_int()

                # Crew MVP
                case DailyRewardBonusType.CREW_MVP:
                    if not user.has_crew_mvp_bonus():
                        continue
                    value = Env.DAILY_REWARD_BONUS_CREW_MVP.get_int()

                case _:
                    raise ValueError(f"Invalid bonus type: {bonus_type}")

            amount = int(get_value_from_percentage(total_amount, value))
            total_amount += amount
            bonus_list.append(DailyRewardBonus(bonus_type, value, amount))

        return bonus_list

    def get_days_to_next_prize(self) -> int:
        """
        Get the days to next prize
        :return: The days to next prize
        """

        prize_days = Env.DAILY_REWARD_STREAK_DAYS.get_int()
        last_streak_reward = self.get_last_streak_reward(self.user)

        # Not yet up to minimum streak days.
        # Ex. Day 3 with prize days 7, so 4 days remaining
        if last_streak_reward.streak_count < prize_days:
            return prize_days - last_streak_reward.streak_count

        # Ex. Day 9 with prize days 7, so 5 days remaining
        return prize_days - (last_streak_reward.streak_count % prize_days)

    def get_base_belly_prize_offer(self) -> int:
        """
        Get the base belly prize
        :return: The base belly prize offer
        """

        return self.total_amount

    @staticmethod
    def get_minimum_belly_prize() -> int:
        """
        Get the minimum belly prize
        :return: The minimum belly prize
        """

        return 1

    def get_maximum_belly_prize(self) -> int:
        """
        Get the maximum belly prize
        :return: The maximum belly prize
        """

        return self.total_amount * 2

    def should_award_prize(self) -> bool:
        """
        Should award prize
        :return: Should award prize
        """
        if self.get_days_to_next_prize() != Env.DAILY_REWARD_STREAK_DAYS.get_int():
            return False

        # Award if it's the first claim of the day
        rewards_today = (
            DailyReward.select()
            .where((DailyReward.user == self.user) & (DailyReward.date >= get_day_in_past()))
            .count()
        )

        return rewards_today == 1


DailyReward.create_table()
