from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Group import Group


class Leaderboard(BaseModel):
    """
    Leaderboard class
    """
    id = PrimaryKeyField()
    year = SmallIntegerField()
    week = SmallIntegerField()
    group: Group = ForeignKeyField(Group, null=True, backref='leaderboards')
    global_message_id = IntegerField(null=True)

    class Meta:
        db_table = 'leaderboard'


Leaderboard.create_table()
