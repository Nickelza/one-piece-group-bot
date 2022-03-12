from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Leaderboard import Leaderboard
from src.model.User import User


class LeaderboardUser(BaseModel):
    """
    Leaderboard class
    """
    leaderboard = ForeignKeyField(Leaderboard, backref='leaderboard_users', on_delete='CASCADE', on_update='CASCADE')
    user = ForeignKeyField(User, backref='leaderboard_users', on_delete='CASCADE', on_update='CASCADE')
    position = IntegerField()
    bounty = BigIntegerField()
    rank_index = SmallIntegerField()

    class Meta:
        db_table = 'leaderboard_user'


LeaderboardUser.create_table()
