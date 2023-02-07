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
    last_error_date = DateTimeField(null=True)
    last_error_message = CharField(null=True)
    is_active = BooleanField(default=True)
    is_muted = BooleanField(default=False)

    class Meta:
        db_table = 'group'


Group.create_table()
