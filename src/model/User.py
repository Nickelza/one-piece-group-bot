import datetime

from peewee import *

import constants as c
from src.model.BaseModel import BaseModel
from src.model.Crew import Crew
from src.model.enums.Screen import Screen


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
    crew = ForeignKeyField(Crew, backref='crew_members', null=True)
    crew_join_date = DateTimeField(null=True)
    crew_role = SmallIntegerField(null=True)
    can_create_crew = BooleanField(default=True)
    can_join_crew = BooleanField(default=True)
    last_message_date = DateTimeField(default=datetime.datetime.now)
    private_screen_list = CharField(max_length=99)
    private_screen_step = SmallIntegerField()

    class Meta:
        db_table = 'user'

    def get_bounty_formatted(self) -> str:
        """
        Returns a formatted string of the bounty
        :return: The formatted string e.g. 1,000,000
        """

        from src.service.bounty_service import get_belly_formatted
        return get_belly_formatted(int(str(self.bounty)))  # Double cast to avoid IDE warnings (BigIntegerField type)

    def is_arrested(self):
        """
        Returns True if the user is arrested
        :return: True if the user is arrested
        """

        return ((self.impel_down_release_date is not None and self.impel_down_release_date > datetime.datetime.now())
                or self.impel_down_is_permanent)

    def update_private_screen_list(self, screen: Screen, previous_screen_list: list[Screen] = None) -> 'User':
        """
        Updates the private screen list
        :param screen: The screen
        :param previous_screen_list: The previous screen list
        """

        if previous_screen_list is not None:
            self.private_screen_step = None  # Will have to update when Skip button is present
            self.private_screen_list = c.STANDARD_SPLIT_CHAR.join(previous_screen_list)

        if self.private_screen_list is None or screen is Screen.PVT_START:
            self.private_screen_list = screen
        else:
            private_screen_list = self.get_private_screen_list()

            # Back button, remove last screen
            if len(private_screen_list) > 2 and private_screen_list[-2] is screen:
                private_screen_list.pop()
            elif private_screen_list[-1] is not screen:  # Add screen
                private_screen_list.append(screen)

            self.private_screen_list = c.STANDARD_SPLIT_CHAR.join(private_screen_list)

        if len(self.private_screen_list) == 0:
            self.private_screen_list = None

        self.save()
        return self

    def get_private_screen_list(self) -> list[Screen]:
        """
        Returns the private screen list
        :return: The private screen list
        """

        if self.private_screen_list is None:
            return []

        return [Screen(str(screen)) for screen in self.private_screen_list.split(c.STANDARD_SPLIT_CHAR)]


User.create_table()
