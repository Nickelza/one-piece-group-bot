import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Group import Group
from src.model.User import User


class GroupUser(BaseModel):
    """
    Group User class
    """

    group = ForeignKeyField(Group, backref="groups", on_delete="RESTRICT", on_update="CASCADE")
    user = ForeignKeyField(User, backref="users", on_delete="RESTRICT", on_update="CASCADE")
    last_message_date = DateTimeField(default=datetime.datetime.now)
    is_active = BooleanField(default=True)
    is_admin = BooleanField(default=False)

    class Meta:
        db_table = "group_user"

    @staticmethod
    def get_user_is_active_is_same_group_statement(user_1, user_2):
        return (
            GroupUser.select(fn.COUNT(GroupUser.group).alias("count_same_group")).where(
                GroupUser.user == user_1,
                GroupUser.is_active == True,
                GroupUser.group.in_(
                    GroupUser.select(GroupUser.group).where(
                        GroupUser.user == user_2, GroupUser.is_active == True
                    )
                ),
            )
        ) > 0

    @staticmethod
    def set_no_longer_admin(user, group):
        GroupUser.update(is_admin=False).where(
            (GroupUser.user == user) & (GroupUser.group == group)
        ).execute()


GroupUser.create_table()
