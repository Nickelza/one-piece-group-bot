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
    tg_username = CharField(max_length=99)
    bounty = BigIntegerField(default=0)
    pending_bounty = BigIntegerField(default=0)
    max_rank_index = SmallIntegerField(null=True)
    can_play_doc_q = BooleanField(default=True)
    can_initiate_game = BooleanField(default=True)
    bounty_poster_limit = SmallIntegerField(default=0)
    location_level = SmallIntegerField(default=0)
    should_propose_new_world = BooleanField(default=True)
    can_change_region = BooleanField(default=True)
    fight_immunity_end_date = DateTimeField(null=True)
    fight_cooldown_end_date = DateTimeField(null=True)
    should_send_location_update = BooleanField(default=True)
    impel_down_release_date = DateTimeField(null=True)
    impel_down_is_permanent = BooleanField(default=False)
    last_message_date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'user'

    def get_bounty_formatted(self) -> str:
        """
        Returns a formatted string of the bounty
        :return: The formatted string e.g. 1,000,000
        """

        return '{0:,}'.format(self.bounty)

    def is_arrested(self):
        """
        Returns True if the user is arrested
        :return: True if the user is arrested
        """

        return ((self.impel_down_release_date is not None and self.impel_down_release_date > datetime.datetime.now())
                or self.impel_down_is_permanent)


User.create_table()
