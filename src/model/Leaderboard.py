from peewee import *

from src.model.BaseModel import BaseModel


class Leaderboard(BaseModel):
    """
    Leaderboard class
    """
    id = PrimaryKeyField()
    year = SmallIntegerField()
    week = SmallIntegerField()
    message_id = IntegerField()

    class Meta:
        db_table = 'leaderboard'


Leaderboard.create_table()
