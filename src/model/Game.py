import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.User import User
from src.model.enums.GameStatus import GameStatus


class Game(BaseModel):
    """
    Game class
    """
    id = PrimaryKeyField()
    challenger = ForeignKeyField(User, backref='game_challengers', on_delete='CASCADE',
                                 on_update='CASCADE')
    opponent = ForeignKeyField(User, backref='game_opponents', on_delete='CASCADE', on_update='CASCADE')
    type = SmallIntegerField(null=True)
    board = CharField(max_length=999, null=True)
    date = DateTimeField(default=datetime.datetime.now)
    status = SmallIntegerField(default=GameStatus.AWAITING_SELECTION)
    message_id = IntegerField(null=True)
    wager = IntegerField(null=True)

    class Meta:
        db_table = 'game'


Game.create_table()
