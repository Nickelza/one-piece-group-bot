import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.SystemUpdate import SystemUpdate
from src.model.User import User


class SystemUpdateUser(BaseModel):
    """
    SystemUpdateUser class
    """
    id = PrimaryKeyField()
    system_update = ForeignKeyField(SystemUpdate, backref='system_update')
    user = ForeignKeyField(User, backref='system_update')
    date = DateTimeField(default=datetime.datetime.now)
    error = CharField(null=True)

    class Meta:
        db_table = 'system_update_user'


SystemUpdateUser.create_table()
