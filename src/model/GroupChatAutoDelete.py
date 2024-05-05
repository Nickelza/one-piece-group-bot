import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat


class GroupChatAutoDelete(BaseModel):
    """
    Group Chat Auto Delete class
    """

    id: int | PrimaryKeyField = PrimaryKeyField()
    group_chat: GroupChat | ForeignKeyField = ForeignKeyField(
        GroupChat, backref="auto_delete", on_delete="CASCADE"
    )
    message_id: int | IntegerField = IntegerField()
    date: datetime.datetime | DateTimeField = DateTimeField(default=datetime.datetime.now)
    delete_date: datetime.datetime | DateTimeField = DateTimeField()

    class Meta:
        db_table = "group_chat_auto_delete"


GroupChatAutoDelete.create_table()
