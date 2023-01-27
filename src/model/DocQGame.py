import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Group import Group
from src.model.Topic import Topic
from src.model.User import User
from src.model.enums.GameStatus import GameStatus


class DocQGame(BaseModel):
    """
    Doc Q Game class
    """
    id = PrimaryKeyField()
    user = ForeignKeyField(User, backref='doc_q_game_users', on_delete='CASCADE', on_update='CASCADE')
    datetime = DateTimeField(default=datetime.datetime.now)
    status = SmallIntegerField(default=GameStatus.IN_PROGRESS)
    correct_choices_index = CharField(max_length=99, null=True)
    group = ForeignKeyField(Group, backref='doc_q_game_groups', on_delete='RESTRICT', on_update='CASCADE')
    topic = ForeignKeyField(Topic, null=True, backref='doc_q_game_topics', on_delete='RESTRICT', on_update='CASCADE')
    message_id = IntegerField(null=True)
    belly = BigIntegerField(null=True)

    class Meta:
        db_table = 'doc_q_game'


DocQGame.create_table()
