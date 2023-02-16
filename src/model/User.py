import datetime
from typing import Any

from peewee import *
from telegram import ChatMember, Update
from telegram.constants import ChatMemberStatus

import constants as c
from src.model.BaseModel import BaseModel
from src.model.Crew import Crew
from src.model.enums.CrewRole import CrewRole
from src.model.enums.Location import get_last_new_world, get_first_new_world, get_by_level, Location, \
    is_paradise_by_level
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
    doc_q_cooldown_end_date = DateTimeField(null=True)
    game_cooldown_end_date = DateTimeField(null=True)
    bounty_poster_limit = SmallIntegerField(default=0)
    location_level = SmallIntegerField(default=0)
    should_propose_new_world = BooleanField(default=True)
    can_change_region = BooleanField(default=True)
    fight_immunity_end_date = DateTimeField(null=True)
    fight_cooldown_end_date = DateTimeField(null=True)
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
    private_screen_in_edit_id = IntegerField(null=True)
    bounty_gift_tax = IntegerField(default=0)
    is_admin = BooleanField(default=False)
    can_collect_devil_fruit = BooleanField(default=True)

    # Transient fields

    # If the model should be updated at script end. Sometimes the model is updated in functions where it can not be
    # passed as a parameter, so updating it at the end of the script would overwrite the changes
    should_update_model: bool = True

    # Pending bounty at the start of the script. Used to check if the pending bounty went negative

    previous_pending_bounty: int = 0

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

    @staticmethod
    def get_is_not_arrested_statement_condition() -> Any:
        """
        Returns a case statement condition which returns true if the user is not arrested
        :return: The case statement
        """
        return ((User.impel_down_is_permanent == False) &
                ((User.impel_down_release_date.is_null()) | (User.impel_down_release_date < datetime.datetime.now())))

    def update_private_screen_list(self, screen: Screen, previous_screen_list: list[Screen] = None):
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

    def in_edit_mode(self):
        """
        Returns True if the user is in edit mode
        :return: True if the user is in edit mode
        """

        return self.private_screen_step is not None

    def get_private_screen_list(self) -> list[Screen]:
        """
        Returns the private screen list
        :return: The private screen list
        """

        if self.private_screen_list is None:
            return []

        return [Screen(str(screen)) for screen in self.private_screen_list.split(c.STANDARD_SPLIT_CHAR)]

    def get_current_private_screen(self) -> Screen:
        """
        Returns the current saved private screen
        :return: The private screen
        """

        return (self.get_private_screen_list() or [None])[-1]

    def reset_private_screen(self):
        """
        Resets the private screen
        """

        self.private_screen_step = None
        self.private_screen_in_edit_id = None

    def is_crew_captain(self):
        """
        Returns True if the user is the captain of a Crew
        :return: True if the user is the captain of a Crew
        """

        if self.is_crew_member() and self.crew_role is not None:
            return CrewRole(self.crew_role) is CrewRole.CAPTAIN

        return False

    @staticmethod
    def get_by_tg_id(tg_user_id: str) -> 'User':
        """
        Returns the User by the Telegram user id
        :param tg_user_id: The Telegram user id
        :return: The User
        """

        return User.get_or_none(User.tg_user_id == tg_user_id)

    def is_crew_member(self):
        """
        Returns True if the user is in a crew
        :return: True if the user is in a crew
        """

        return self.crew is not None

    def in_same_crew(self, user: 'User') -> bool:
        """
        Returns True if the user is in the same crew as the given user
        :param user: The user
        :return: True if the user is in the same crew as the given user
        """

        return self.crew is not None and self.crew == user.crew

    def get_markdown_mention(self) -> str:
        """
        Returns the markdown mention of the user
        :return: The markdown mention of the user
        """

        from src.service.message_service import mention_markdown_v2

        return mention_markdown_v2(str(self.tg_user_id), str(self.tg_first_name))

    def refresh(self) -> 'User':
        """
        Refreshes the user
        :return: The refreshed user
        """

        return type(self).get(self._pk_expr())

    def get_max_bounty(self) -> int:
        """
        Returns the max bounty between the user and the crew average
        :return: The max bounty between the user and the crew average
        """

        if self.is_crew_member():
            return max(int(str(self.bounty)), self.crew.get_average_bounty())

        return int(str(self.bounty))

    def in_new_world(self):
        """
        Returns True if the user is in the New World
        :return: True if the user is in the New World
        """

        from src.model.enums.Location import is_new_world_by_level
        return is_new_world_by_level(int(str(self.location_level)))

    def has_higher_bounty_than_crew_average(self) -> bool:
        """
        Returns True if the user has a higher bounty than the crew average
        :return: True if the user has a higher bounty than the crew average
        """

        if self.is_crew_member():
            return int(str(self.bounty)) > self.crew.get_average_bounty()

        return False

    def has_new_world_bonus(self) -> bool:
        """
        Returns True if the user has the New World bonus
        :return: True if the user has the New World bonus
        """

        return self.in_new_world() and not self.has_bounty_gain_limitations()

    def has_crew_bonus(self) -> bool:
        """
        Returns True if the user has the Crew bonus
        :return: True if the user has the Crew bonus
        """

        return self.is_crew_member() and not self.has_bounty_gain_limitations()

    def has_crew_mvp_bonus(self) -> bool:
        """
        Returns True if the user has the Crew MVP bonus
        :return: True if the user has the Crew MVP bonus
        """

        return self.has_higher_bounty_than_crew_average() and not self.has_bounty_gain_limitations()

    def is_in_paradise(self) -> bool:
        """
        Returns True if the user is in Paradise
        :return: True if the user is in Paradise
        """

        return is_paradise_by_level(int(str(self.location_level)))

    def get_location(self) -> Location:
        """
        Returns the location of the user
        :return: The location of the user
        """

        return get_by_level(int(str(self.location_level)))

    def has_bounty_gain_limitations(self) -> bool:
        """
        Returns True if the user has bounty gain limitations
        This occurs when the user is in Paradise but has enough bounty to be in the New World, or their bounty is
        higher than that required to reach the final location
        :return: True if the user has bounty gain limitations
        """

        return ((self.is_in_paradise() and (self.bounty + self.pending_bounty) >= get_first_new_world().required_bounty)
                or ((self.bounty + self.pending_bounty) >= get_last_new_world().required_bounty))

    @staticmethod
    def get_has_bounty_gain_limitations_statement_condition() -> Any:
        """
        Returns the has bounty gain limitations statement condition
        :return: The has bounty gain limitations statement condition
        """

        return (((User.location_level < get_first_new_world().level) &
                 ((User.bounty + User.pending_bounty) >= get_first_new_world().required_bounty)) |
                ((User.bounty + User.pending_bounty) >= get_last_new_world().required_bounty))

    async def is_chat_admin(self, update: Update):
        """
        Returns True if the user is an admin of the chat
        :param update: The update
        :return: True if the user is an admin of the chat
        """

        from telegram.error import Forbidden
        try:
            chat_member: ChatMember = await update.effective_chat.get_member(str(self.tg_user_id))
            return chat_member.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)
        except Forbidden:  # Bot kicked from the group chat
            pass


User.create_table()
