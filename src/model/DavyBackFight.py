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
    conscript_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)

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


DavyBackFight.create_table()
