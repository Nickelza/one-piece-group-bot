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
    last_error_date = DateTimeField(null=True)
    last_error_message = CharField(null=True)
    is_muted = BooleanField(default=False)

    class Meta:
        db_table = 'topic'


Topic.create_table()
