from peewee import *

from src.model.BaseModel import BaseModel
from src.model.User import User


class DisabledNotification(BaseModel):
    """
    DisabledNotification class
    """

    id = PrimaryKeyField()
    user = ForeignKeyField(
        User, backref="disabled_notification_users", on_delete="CASCADE", on_update="CASCADE"
    )
    type = SmallIntegerField(null=True)

    class Meta:
        db_table = "disabled_notification"


DisabledNotification.create_table()
