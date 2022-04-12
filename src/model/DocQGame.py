import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.User import User
from src.model.enums.GameStatus import GameStatus


class DocQGame(BaseModel):
    """
    Doc Q Game class
    """
    id = PrimaryKeyField()
    user = ForeignKeyField(User, backref='doc_q_game_users', on_delete='CASCADE', on_update='CASCADE')
    datetime = DateTimeField(default=datetime.datetime.now)
    status = SmallIntegerField(default=GameStatus.IN_PROGRESS.value)
    correct_choices_index = CharField(max_length=99, null=True)
    message_id = IntegerField(null=True)
    berry = BigIntegerField(null=True)

    class Meta:
        db_table = 'doc_q_game'


DocQGame.create_table()
