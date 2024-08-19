from peewee import *

from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat
from src.model.User import User


class UnmutedUser(BaseModel):
    """
    Unmuted user class
    """

    user = ForeignKeyField(User, backref="unmuted_users", on_delete="CASCADE", on_update="CASCADE")
    group_chat = ForeignKeyField(
        GroupChat,
        null=True,
        backref="unmuted_users_groups_chats",
        on_delete="CASCADE",
        on_update="CASCADE",
    )

    class Meta:
        db_table = "unmuted_user"


UnmutedUser.create_table()
