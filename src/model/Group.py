import datetime

from peewee import *

from src.model.BaseModel import BaseModel


class Group(BaseModel):
    """
    Group class
    """
    id = PrimaryKeyField()
    tg_group_id = CharField(unique=True)
    tg_group_name = CharField()
    tg_group_username = CharField(null=True)
    is_forum = BooleanField(default=False)
    added_date = DateTimeField(default=datetime.datetime.now)
    last_message_date = DateTimeField(default=datetime.datetime.now)
    is_active = BooleanField(default=True)

    class Meta:
        db_table = 'group'


Group.create_table()
