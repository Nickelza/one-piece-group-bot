import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Group import Group


class Topic(BaseModel):
    """
    Topic class
    """
    id = PrimaryKeyField()
    group = ForeignKeyField(Group, backref='topics', on_delete='CASCADE', on_update='CASCADE')
    tg_topic_id = IntegerField()
    last_message_date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'topic'


Topic.create_table()
