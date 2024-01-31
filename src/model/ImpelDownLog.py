from datetime import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.User import User


class ImpelDownLog(BaseModel):
    """
    Impel Down Log class
    """

    id = PrimaryKeyField()
    user = ForeignKeyField(
        User, backref="impel_down_users", on_delete="CASCADE", on_update="CASCADE"
    )
    sentence_type = CharField(max_length=99, null=True)
    sentence_origin = CharField(max_length=99, null=True)
    date_time = DateTimeField(default=datetime.now)
    release_date_time = DateTimeField(null=True)
    is_permanent = BooleanField(default=False)
    bounty_action = CharField(max_length=99, null=True)
    reason = CharField(max_length=999, null=True)
    previous_bounty = BigIntegerField(null=True)
    new_bounty = BigIntegerField(null=True)
    message_sent = BooleanField(default=False)
    is_reversed = BooleanField(default=False)
    external_id = IntegerField(null=True)

    class Meta:
        db_table = "impel_down_log"


ImpelDownLog.create_table()
