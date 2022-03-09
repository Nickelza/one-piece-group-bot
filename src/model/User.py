import datetime

from peewee import *

from src.model.BaseModel import BaseModel


class User(BaseModel):
    """
    User class
    """
    id = PrimaryKeyField()
    tg_user_id = CharField(max_length=99, unique=True)
    tg_first_name = CharField(max_length=99)
    tg_last_name = CharField(max_length=99)
    bounty = BigIntegerField(default=0)
    max_bounty = BigIntegerField(default=0)
    max_title = SmallIntegerField(null=True)
    can_play_doc_q = BooleanField(default=True)
    bounty_poster_limit = SmallIntegerField(default=0)
    last_message_date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'user'


User.create_table()
