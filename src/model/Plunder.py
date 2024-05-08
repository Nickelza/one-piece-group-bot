import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.BountyLoan import BountyLoan
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.BountyLoanSource import BountyLoanSource
from src.model.enums.GameStatus import GameStatus


class Plunder(BaseModel):
    """
    Plunder class
    """

    id: int | PrimaryKeyField = PrimaryKeyField()
    challenger: User | ForeignKeyField = ForeignKeyField(
        User, backref="plunder_challengers", on_delete="CASCADE", on_update="CASCADE"
    )
    opponent: User | ForeignKeyField = ForeignKeyField(
        User, backref="plunder_opponents", on_delete="CASCADE", on_update="CASCADE"
    )
    win_probability: float | FloatField = FloatField()
    date: datetime.datetime | DateTimeField = DateTimeField(default=datetime.datetime.now)
    status: bool | SmallIntegerField = SmallIntegerField(default=GameStatus.IN_PROGRESS)
    group_chat: GroupChat | ForeignKeyField = ForeignKeyField(
        GroupChat,
        null=True,
        backref="plunder_groups_chats",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    message_id: int | IntegerField = IntegerField(null=True)
    belly: int | BigIntegerField = BigIntegerField(null=True)
    sentence_duration = IntegerField(null=True)

    class Meta:
        db_table = "plunder"

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
            Plunder()
            .select()
            .where((Plunder.challenger == user) & (Plunder.status == status))
            .count()
            + Plunder()
            .select()
            .where((Plunder.opponent == user) & (Plunder.status == status.get_opposite_status()))
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
            Plunder.select(fn.SUM(Plunder.belly)).where(
                (Plunder.challenger == user) & (Plunder.status == status)
            )
        ).scalar() + (
            Plunder.select(fn.SUM(Plunder.belly)).where(
                (Plunder.opponent == user) & (Plunder.status == status.get_opposite_status())
            )
        ).scalar()

    @staticmethod
    def get_max_won_or_lost(user: User, status: GameStatus) -> "Plunder":
        """
        Get the plunder with the max belly won or lost
        param user: The user
        param status: The status (won or lost)
        return: The plunder
        """

        # Max plunder as challenger
        max_plunder_as_challenger: Plunder = (
            Plunder()
            .select()
            .where((Plunder.challenger == user) & (Plunder.status == status))
            .order_by(Plunder.belly.desc())
            .first()
        )

        # Max plunder as opponent
        max_plunder_as_opponent: Plunder = (
            Plunder()
            .select()
            .where((Plunder.opponent == user) & (Plunder.status == status.get_opposite_status()))
            .order_by(Plunder.belly.desc())
            .first()
        )

        # The max plunder
        return max(max_plunder_as_challenger, max_plunder_as_opponent, key=lambda f: f.belly)

    @staticmethod
    def get_most_plundered_user(user: User) -> (User, int):
        """
        Get the most plundered user and the amount of plunders
        param user: The user
        return: The most plundered user and the amount of plunders
        """

        most_plundered_user_as_challenger = (
            Plunder()
            .select(Plunder.opponent, fn.COUNT(Plunder.opponent).alias("count"))
            .where(Plunder.challenger == user)
            .group_by(Plunder.opponent)
            .order_by(SQL("count").desc())
            .first()
        )
        amount_as_challenger = most_plundered_user_as_challenger.count

        most_plundered_user_as_opponent = (
            Plunder()
            .select(Plunder.challenger, fn.COUNT(Plunder.challenger).alias("count"))
            .where(Plunder.opponent == user)
            .group_by(Plunder.challenger)
            .order_by(SQL("count").desc())
            .first()
        )
        amount_as_opponent = most_plundered_user_as_opponent.count

        if amount_as_opponent > amount_as_challenger:
            return most_plundered_user_as_opponent.challenger, amount_as_opponent

        return most_plundered_user_as_challenger.opponent, amount_as_challenger

    @staticmethod
    def get_max_sentence(user: User) -> "Plunder":
        """
        Get the plunder with the max sentence
        param user: The user
        return: The plunder
        """

        # Max plunder as challenger
        return (
            Plunder()
            .select()
            .where(((Plunder.challenger == user) & (Plunder.status == GameStatus.LOST)))
            .order_by(Plunder.sentence_duration.desc())
            .first()
        )

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

    def get_loan(self) -> BountyLoan:
        """
        Get the loan
        :return: The loan
        """

        return BountyLoan.get(
            BountyLoan.source == BountyLoanSource.PLUNDER, BountyLoan.external_id == self.id
        )


Plunder.create_table()
