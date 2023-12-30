import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.User import User


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
        db_table = "group"

    def get_active_users(self) -> list[User]:
        """
        Get the active users in the group
        :return: The active users in the group
        """
        from src.model.GroupUser import GroupUser

        return (
            User()
            .select()
            .join(GroupUser)
            .join(Group)
            .where((Group.id == self.id) & (GroupUser.is_active == True))
        )

    def get_active_users_ids(self) -> list[int]:
        """
        Get the active users ids in the group
        :return: The active users ids in the group
        """

        return [user.id for user in self.get_active_users()]


Group.create_table()
