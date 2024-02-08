import datetime

from peewee import *

import resources.Environment as Env
from src.model.BaseModel import BaseModel
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.GameStatus import GameStatus


class DavyBackFight(BaseModel):
    """
    DavyBackFight class
    """

    id: int | PrimaryKeyField = PrimaryKeyField()
    challenger_crew: Crew | ForeignKeyField = ForeignKeyField(
        Crew, backref="davy_back_fights_challengers"
    )
    opponent_crew: Crew | ForeignKeyField = ForeignKeyField(
        Crew, backref="davy_back_fights_opponents"
    )
    challenger_chest: int | BigIntegerField = BigIntegerField(default=0)
    opponent_chest: int | BigIntegerField = BigIntegerField(default=0)
    participants_count: int | IntegerField = IntegerField(null=True)
    date = DateTimeField(default=datetime.datetime.now)
    status: int | SmallIntegerField = SmallIntegerField(
        default=GameStatus.AWAITING_OPPONENT_CONFIRMATION
    )
    start_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    conscript: User | ForeignKeyField = ForeignKeyField(
        User, backref="davy_back_fights_conscripts", null=True
    )
    conscript_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    penalty_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)

    class Meta:
        db_table = "davy_back_fight"

    @staticmethod
    def delete_expired_requests():
        """
        Delete expire requests, so requests that are in AWAITING_OPPONENT_CONFIRMATION status and
        were created more than x minutes ago
        """
        DavyBackFight.delete().where(
            DavyBackFight.status == GameStatus.AWAITING_OPPONENT_CONFIRMATION,
            DavyBackFight.date
            < (
                datetime.datetime.now()
                - datetime.timedelta(
                    minutes=Env.CREW_DAVY_BACK_FIGHT_REQUEST_EXPIRATION_TIME.get_int()
                )
            ),
        ).execute()

    def get_participants(self, crew: Crew = None) -> list[any]:
        """
        Get all the participants of a Davy Back Fight
        :param crew: The crew object
        :return: The list of participants
        """

        if crew is None:
            return self.davy_back_fight_participants

        return [p for p in self.davy_back_fight_participants if p.crew == crew]

    def get_participants_users(self, crew: Crew = None) -> list[User]:
        """
        Get all the participants of a Davy Back Fight
        :param crew: The crew object
        :return: The list of participants
        """

        if crew is None:
            return [p.user for p in self.davy_back_fight_participants]

        return [p.user for p in self.davy_back_fight_participants if p.crew == crew]

    def get_non_participants_users(self, crew: Crew) -> list[any]:
        """
        Get all the non-participants of a Davy Back Fight
        :param crew: The crew object
        :return: The list of non-participants
        """
        return [m for m in crew.get_members() if m not in self.get_participants_users(crew=crew)]

    def get_status(self) -> GameStatus:
        """
        Get the status of the Davy Back Fight
        :return: The status
        """

        return GameStatus(self.status)

    def get_crew_gain(self, crew: Crew) -> int:
        """
        Get the crew gain
        :param crew: The crew object
        :return: The crew gain
        """

        return sum([p.contribution for p in self.davy_back_fight_participants if p.crew == crew])

    def get_opponent_crew(self, crew: Crew):
        """
        Get the opponent crew
        :param crew: The crew object
        :return: The opponent crew
        """

        if crew == self.challenger_crew:
            return self.opponent_crew
        return self.challenger_crew

    def get_in_progress_display_status(self, crew: Crew) -> GameStatus:
        """
        Get the in progress display status [WINNING, LOSING, DRAW]
        :param crew: The crew object
        :return: The in progress display status
        """

        crew_total = self.get_crew_gain(crew)
        opponent_total = self.get_crew_gain(self.get_opponent_crew(crew))

        if crew_total > opponent_total:
            return GameStatus.WINNING

        if crew_total < opponent_total:
            return GameStatus.LOSING

        return GameStatus.DRAW


DavyBackFight.create_table()
