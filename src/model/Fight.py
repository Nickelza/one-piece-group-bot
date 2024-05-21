import datetime

from peewee import *

import resources.Environment as Env
from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.service.date_service import (
    get_elapsed_hours,
    get_remaining_duration,
    get_datetime_in_future_hours,
)


class Fight(BaseModel):
    """
    Fight class
    """

    id: int | PrimaryKeyField = PrimaryKeyField()
    challenger: User | ForeignKeyField = ForeignKeyField(
        User, backref="fight_challengers", on_delete="CASCADE", on_update="CASCADE"
    )
    opponent: User | ForeignKeyField = ForeignKeyField(
        User, backref="fight_opponents", on_delete="CASCADE", on_update="CASCADE"
    )
    win_probability: float | FloatField = FloatField()
    date: datetime.datetime | DateTimeField = DateTimeField(default=datetime.datetime.now)
    status: bool | SmallIntegerField = SmallIntegerField(default=GameStatus.IN_PROGRESS)
    group_chat: GroupChat | ForeignKeyField = ForeignKeyField(
        GroupChat,
        null=True,
        backref="fight_groups_chats",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    message_id: int | IntegerField = IntegerField(null=True)
    belly: int | BigIntegerField = BigIntegerField(null=True)

    in_revenge_to_fight = ForeignKeyField(
        "self",
        null=True,
        backref="revenge_attack_fights",
        on_delete="RESTRICT",
        on_update="RESTRICT",
    )

    # Backref
    revenge_attack_fights = None

    class Meta:
        db_table = "fight"

    def get_win_probability(self, user: User) -> float:
        """
        Get the win probability given a user

        :param user: The user
        :return: The win probability
        """

        if user.id == self.challenger.id:
            return float(str(self.win_probability))
        else:
            return 100 - self.win_probability

    @staticmethod
    def get_total_win_or_loss(user: User, status: GameStatus) -> int:
        """
        Get the total amount of wins or losses a user has
        param user: The user
        param status: The status (won or lost)
        return: The total amount of wins or losses
        """

        return (
            Fight().select().where((Fight.challenger == user) & (Fight.status == status)).count()
            + Fight()
            .select()
            .where((Fight.opponent == user) & (Fight.status == status.get_opposite_status()))
            .count()
        )

    @staticmethod
    def get_total_belly_won_or_lost(user: User, status: GameStatus) -> int:
        """
        Get the total amount of belly a user has won or lost
        param user: The user
        param status: The status (won or lost)
        return: The total amount of belly
        """

        return (
            Fight.select(fn.SUM(Fight.belly)).where(
                (Fight.challenger == user) & (Fight.status == status)
            )
        ).scalar() + (
            Fight.select(fn.SUM(Fight.belly)).where(
                (Fight.opponent == user) & (Fight.status == status.get_opposite_status())
            )
        ).scalar()

    @staticmethod
    def get_max_won_or_lost(user: User, status: GameStatus) -> "Fight":
        """
        Get the fight with the max belly won or lost
        param user: The user
        param status: The status (won or lost)
        return: The fight
        """

        # Max fight as challenger
        max_fight_as_challenger: Fight = (
            Fight()
            .select()
            .where((Fight.challenger == user) & (Fight.status == status))
            .order_by(Fight.belly.desc())
            .first()
        )

        # Max fight as opponent
        max_fight_as_opponent: Fight = (
            Fight()
            .select()
            .where((Fight.opponent == user) & (Fight.status == status.get_opposite_status()))
            .order_by(Fight.belly.desc())
            .first()
        )

        # The max fight
        return max(max_fight_as_challenger, max_fight_as_opponent, key=lambda f: f.belly)

    @staticmethod
    def get_most_fought_user(user: User) -> (User, int):
        """
        Get the most fought user and the amount of fights
        param user: The user
        return: The most fought user and the amount of fights
        """

        most_fought_user_as_challenger = (
            Fight()
            .select(Fight.opponent, fn.COUNT(Fight.opponent).alias("count"))
            .where(Fight.challenger == user)
            .group_by(Fight.opponent)
            .order_by(SQL("count").desc())
            .first()
        )
        amount_as_challenger = most_fought_user_as_challenger.count

        most_fought_user_as_opponent = (
            Fight()
            .select(Fight.challenger, fn.COUNT(Fight.challenger).alias("count"))
            .where(Fight.opponent == user)
            .group_by(Fight.challenger)
            .order_by(SQL("count").desc())
            .first()
        )
        amount_as_opponent = most_fought_user_as_opponent.count

        if amount_as_opponent > amount_as_challenger:
            return most_fought_user_as_opponent.challenger, amount_as_opponent

        return most_fought_user_as_challenger.opponent, amount_as_challenger

    def get_opponent(self, user: User) -> User:
        """
        Get the other opponent
        param user: The user
        return: The opponent
        """

        # noinspection PyTypeChecker
        # Warns that the return type is ForeignKeyField
        return self.challenger if self.challenger != user else self.opponent

    def get_status(self) -> GameStatus:
        """
        Get the status of the game
        :return: The status of the game
        """

        return GameStatus(self.status)

    def get_revenge_fight(self) -> "Fight":
        """
        Get the revenge fight
        :return: The revenge fight
        """

        return Fight.get_or_none(Fight.in_revenge_to_fight == self)

    def can_revenge(self, user: User = None) -> bool:
        """
        Check if a fight can be revenged.
        User can revenge a fight if they were attacked less than x time ago and have not
        already revenged that fight
        :param user: The user
        :return: True if the user can revenge the fight, False otherwise
        """

        # User is challenger
        if self.challenger == user:
            return False

        # Attack was more than x hours ago
        if get_elapsed_hours(self.date) > Env.FIGHT_PLUNDER_REVENGE_DURATION_HOURS.get_int():
            return False

        # Fight was in response to attack
        if self.in_revenge_to_fight is not None:
            return False

        # This fight has already been revenged
        if self.get_revenge_fight() is not None:
            return False

        return True

    def get_revenge_remaining_duration(self) -> str:
        """
        Get the remaining duration for the revenge
        :return: The remaining duration
        """

        return get_remaining_duration(
            get_datetime_in_future_hours(
                Env.FIGHT_PLUNDER_REVENGE_DURATION_HOURS.get_int(), self.date
            )
        )


Fight.create_table()
