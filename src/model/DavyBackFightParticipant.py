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

    class Meta:
        db_table = "davy_back_fight_participant"


DavyBackFightParticipant.create_table()
