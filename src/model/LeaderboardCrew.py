from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Crew import Crew
from src.model.Leaderboard import Leaderboard
from src.model.User import User


class LeaderboardCrew(BaseModel):
    """
    Leaderboard class
    """

    leaderboard: Leaderboard | ForeignKeyField = ForeignKeyField(
        Leaderboard, backref="leaderboard_crews", on_delete="CASCADE", on_update="CASCADE"
    )
    crew: Crew | ForeignKeyField = ForeignKeyField(
        Crew, backref="leaderboard_crews", on_delete="CASCADE", on_update="CASCADE"
    )
    captain: User | ForeignKeyField = ForeignKeyField(
        User, backref="leaderboard_crews", on_delete="CASCADE", on_update="CASCADE"
    )
    position: int | IntegerField = IntegerField()
    level: int | IntegerField = IntegerField()
    total_chest_amount: int | BigIntegerField = BigIntegerField()

    class Meta:
        db_table = "leaderboard_crew"


LeaderboardCrew.create_table()
