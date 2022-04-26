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
    max_rank_index = SmallIntegerField(null=True)
    can_play_doc_q = BooleanField(default=True)
    bounty_poster_limit = SmallIntegerField(default=0)
    location_level = SmallIntegerField(default=0)
    should_propose_new_world = BooleanField(default=True)
    can_change_region = BooleanField(default=True)
    fight_immunity_end_date = DateTimeField(null=True)
    should_send_location_update = BooleanField(default=True)
    last_message_date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'user'


User.create_table()
