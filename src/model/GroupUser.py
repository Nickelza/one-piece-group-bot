import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Group import Group
from src.model.User import User


class GroupUser(BaseModel):
    """
    Group User class
    """
    id = PrimaryKeyField()
    group = ForeignKeyField(Group, backref='groups', on_delete='RESTRICT', on_update='CASCADE')
    user = ForeignKeyField(User, backref='users', on_delete='RESTRICT', on_update='CASCADE')
    last_message_date = DateTimeField(default=datetime.datetime.now)
    is_active = BooleanField(default=True)

    class Meta:
        db_table = 'group_user'


GroupUser.create_table()
