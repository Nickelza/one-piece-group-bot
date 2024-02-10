from datetime import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Crew import Crew
from src.model.DavyBackFight import DavyBackFight
from src.model.User import User


class DavyBackFightParticipant(BaseModel):
    """
    DavyBackFightParticipant class
    """

    id: int | PrimaryKeyField = PrimaryKeyField()
    davy_back_fight: DavyBackFight | ForeignKeyField = ForeignKeyField(
        DavyBackFight, backref="davy_back_fight_participants", on_delete="CASCADE"
    )
    user: User | ForeignKeyField = ForeignKeyField(User, backref="davy_back_fight_participants")
    crew: Crew | ForeignKeyField = ForeignKeyField(Crew, backref="davy_back_fight_participants")
    contribution: int | BigIntegerField = BigIntegerField(default=0)
    date = DateTimeField(default=datetime.now)
    win_amount: int | BigIntegerField = BigIntegerField(null=True)

    class Meta:
        db_table = "davy_back_fight_participant"

    @staticmethod
    def get_top_player(dbf: DavyBackFight, crew: Crew) -> "DavyBackFightParticipant":
        """
        Get the top player of a crew in a Davy Back Fight
        :param dbf: The Davy Back Fight object
        :param crew: The crew object
        :return: The DavyBackFightParticipant object
        """
        return (
            DavyBackFightParticipant.select()
            .where(
                (DavyBackFightParticipant.davy_back_fight == dbf)
                & (DavyBackFightParticipant.crew == crew)
            )
            .order_by(DavyBackFightParticipant.contribution.desc())
            .first()
        )

    def get_contribution_formatted(self):
        """
        Get the contribution formatted
        :return: The contribution formatted
        """

        from src.service.bounty_service import get_belly_formatted

        return get_belly_formatted(self.contribution)

    @staticmethod
    def get_participants_by_contribution(dbf: DavyBackFight) -> list["DavyBackFightParticipant"]:
        """
        Get the participants by contribution
        :param dbf: The Davy Back Fight object
        :return: The list of DavyBackFightParticipant objects
        """

        return (
            DavyBackFightParticipant.select()
            .where(DavyBackFightParticipant.davy_back_fight == dbf)
            .order_by(DavyBackFightParticipant.contribution.desc())
        )

    @staticmethod
    def get_total_contributions(dbf: DavyBackFight, crew: Crew) -> int:
        """
        Get the total contributions of a crew in a Davy Back Fight
        :param dbf: The Davy Back Fight object
        :param crew: The crew object
        :return: The total contributions
        """
        return (
            DavyBackFightParticipant.select(fn.SUM(DavyBackFightParticipant.contribution))
            .where(
                (DavyBackFightParticipant.davy_back_fight == dbf)
                & (DavyBackFightParticipant.crew == crew)
            )
            .scalar()
        )

    def get_contribution_percentage(self) -> float:
        """
        Get the user contribution percentage
        :return: The user contribution percentage
        """
        total = DavyBackFightParticipant.get_total_contributions(self.davy_back_fight, self.crew)
        return (self.contribution / total) * 100 if total > 0 else 0

    def in_winner_crew(self):
        """
        Won the Davy Back Fight
        :return: None
        """

        return self.davy_back_fight.get_winner_crew() == self.crew

    def get_win_amount(self) -> int:
        """
        Get the user win amount
        :return: The user win
        """
        from src.service.math_service import get_value_from_percentage

        user_percentage = self.get_contribution_percentage()
        return int(
            get_value_from_percentage(
                self.davy_back_fight.get_opponent_chest_amount(self.crew), user_percentage
            )
        )

    def get_win_amount_formatted(self) -> str:
        """
        Get the user win amount formatted
        :return: The user win formatted
        """
        from src.service.bounty_service import get_belly_formatted

        return get_belly_formatted(self.get_win_amount())


DavyBackFightParticipant.create_table()
