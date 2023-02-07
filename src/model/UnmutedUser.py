import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Group import Group
from src.model.Topic import Topic
from src.model.User import User


class UnmutedUser(BaseModel):
    """
    Unmuted user class
    """
    id = PrimaryKeyField()
    user = ForeignKeyField(User, backref='unmuted_users', on_delete='CASCADE', on_update='CASCADE')
    group = ForeignKeyField(Group, backref='unmuted_users_groups', on_delete='CASCADE', on_update='CASCADE')
    topic = ForeignKeyField(Topic, null=True, backref='unmuted_users_topics', on_delete='CASCADE', on_update='CASCADE')
    date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'unmuted_user'


UnmutedUser.create_table()
