import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Group import Group


class GroupChat(BaseModel):
    """
    Group Chat class
    """
    id = PrimaryKeyField()
    group = ForeignKeyField(Group, backref='groups', on_delete='CASCADE', on_update='CASCADE')
    tg_topic_id = IntegerField(null=True)  # Nullable for general group_chat
    last_message_date = DateTimeField(default=datetime.datetime.now)
    last_error_date = DateTimeField(null=True)
    last_error_message = CharField(null=True)
    is_active = BooleanField(default=True)
    is_muted = BooleanField(default=False)

    class Meta:
        db_table = 'group_chat'


GroupChat.create_table()
