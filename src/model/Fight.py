import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.User import User
from src.model.enums.GameStatus import GameStatus


class Fight(BaseModel):
    """
    Fight class
    """
    id = PrimaryKeyField()
    challenger = ForeignKeyField(User, backref='fight_challengers', on_delete='CASCADE', on_update='CASCADE')
    opponent = ForeignKeyField(User, backref='fight_opponents', on_delete='CASCADE', on_update='CASCADE')
    win_probability = FloatField(null=False)
    date = DateTimeField(default=datetime.datetime.now)
    status = SmallIntegerField(default=GameStatus.IN_PROGRESS.value)
    message_id = IntegerField(null=True)
    berry = IntegerField(null=True)

    class Meta:
        db_table = 'fight'


Fight.create_table()
