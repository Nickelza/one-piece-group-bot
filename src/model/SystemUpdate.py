from peewee import *

from src.model.BaseModel import BaseModel


class SystemUpdate(BaseModel):
    """
    SystemUpdate class
    """

    title = CharField()
    description = CharField(max_length=999)
    chat_id = CharField()
    message_id = BigIntegerField()

    class Meta:
        db_table = "system_update"

    @staticmethod
    def get_latest_update():
        return SystemUpdate.select().order_by(SystemUpdate.date.desc()).get_or_none()


SystemUpdate.create_table()
