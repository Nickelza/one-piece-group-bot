import datetime

from peewee import *

from src.model.BaseModel import BaseModel


class SystemUpdate(BaseModel):
    """
    SystemUpdate class
    """
    id = PrimaryKeyField()
    title = CharField()
    description = CharField()
    date = DateTimeField(default=datetime.datetime.now)
    chat_id = CharField()
    message_id = BigIntegerField()

    class Meta:
        db_table = 'system_update'

    @staticmethod
    def get_latest_update():
        return SystemUpdate.select().order_by(SystemUpdate.date.desc()).get_or_none()


SystemUpdate.create_table()
