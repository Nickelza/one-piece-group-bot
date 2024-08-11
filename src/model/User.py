import datetime
from typing import Any
from zoneinfo import ZoneInfo

from peewee import *
from telegram import Update
from telegram.ext import ContextTypes

import constants as c
import resources.Environment as Env
from resources import phrases
from src.model.BaseModel import BaseModel
from src.model.Crew import Crew
from src.model.enums.ContextDataKey import ContextDataKey, ContextDataType
from src.model.enums.Location import (
    get_last_new_world,
    get_first_new_world,
    get_by_level,
    Location,
    is_paradise_by_level,
)
from src.model.enums.Screen import Screen
from src.model.enums.crew.CrewRole import CrewRole
from src.model.enums.income_tax.IncomeTaxBracket import IncomeTaxBracket
from src.utils.context_utils import (
    get_user_context_data,
    set_user_context_data,
    remove_context_data,
)
from src.utils.math_utils import get_cumulative_percentage_sum


class User(BaseModel):
    """
    User class
    """

    id: int | PrimaryKeyField = PrimaryKeyField()
    tg_user_id: str | CharField = CharField(max_length=99, unique=True)
    tg_first_name: str | CharField = CharField(max_length=99)
    tg_last_name: str | CharField = CharField(max_length=99)
    tg_username: str | CharField = CharField(max_length=99)
    join_date: datetime.datetime | DateTimeField = DateTimeField(default=datetime.datetime.now)
    bounty: int | BigIntegerField = BigIntegerField(default=0)
    total_gained_bounty: int | BigIntegerField = BigIntegerField(
        default=0, constraints=[Check("total_gained_bounty >= 0")]
    )
    total_gained_bounty_unmodified: int | BigIntegerField = BigIntegerField(
        default=0, constraints=[Check("total_gained_bounty_unmodified >= 0")]
    )
    pending_bounty: int | BigIntegerField = BigIntegerField(default=0)
    doc_q_cooldown_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    game_cooldown_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    game_accept_global_cooldown_end_date: datetime.datetime | DateTimeField = DateTimeField(
        null=True
    )
    bounty_poster_limit: int | SmallIntegerField = SmallIntegerField(default=0)
    location_level: int | SmallIntegerField = SmallIntegerField(default=0)
    should_propose_new_world: bool | BooleanField = BooleanField(default=True)
    can_change_region: bool | BooleanField = BooleanField(default=True)
    fight_immunity_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    fight_cooldown_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    plunder_immunity_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    plunder_cooldown_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    impel_down_release_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    impel_down_is_permanent: bool | BooleanField = BooleanField(default=False)
    crew: Crew | ForeignKeyField = ForeignKeyField(Crew, backref="crew_members", null=True)
    crew_join_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    crew_role: int | SmallIntegerField = SmallIntegerField(null=True)
    crew_promotion_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    conscription_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    can_create_crew: bool | BooleanField = BooleanField(default=True)
    can_join_crew: bool | BooleanField = BooleanField(default=True)
    crew_davy_back_fight_priority: int | IntegerField = IntegerField(null=True)
    last_message_date: datetime.datetime | DateTimeField = DateTimeField(
        default=datetime.datetime.now
    )
    last_system_interaction_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    private_screen_list: str | CharField | None = CharField(max_length=99)
    private_screen_step: int | SmallIntegerField | None = SmallIntegerField()
    private_screen_in_edit_id: int | IntegerField | None = IntegerField(null=True)
    bounty_gift_tax: int | IntegerField = IntegerField(default=0)
    is_admin: bool | BooleanField = BooleanField(default=False)
    devil_fruit_collection_cooldown_end_date: datetime.datetime | DateTimeField = DateTimeField(
        null=True
    )
    timezone: str | CharField = CharField(max_length=99, null=True)
    is_active: bool | BooleanField = BooleanField(default=True)
    prediction_creation_cooldown_end_date: datetime.datetime | DateTimeField = DateTimeField(
        null=True
    )
    bounty_loan_issue_cool_down_end_date: datetime.datetime | DateTimeField = DateTimeField(
        null=True
    )
    # For Legendary Pirate
    is_exempt_from_global_leaderboard_requirements: bool | BooleanField = BooleanField(
        default=False
    )
    can_collect_daily_reward: bool | BooleanField = BooleanField(default=True)
    fight_scout_count: int | IntegerField = IntegerField(default=0)
    plunder_scout_count: int | IntegerField = IntegerField(default=0)

    # Transient fields
    # The private screen step with which the user arrived to the current screen
    private_screen_previous_step: int = None
    # If to stay on the same screen
    private_screen_stay: bool = False
    # Step to go back to
    private_screen_stay_step: int | None = None
    # If to force going back to previous screen
    private_screen_force_go_back: bool = False

    # If the model should be updated at script end. Sometimes the model is updated in functions
    # where it can not be passed as a parameter, so updating it at the end of the script would
    # overwrite the changes
    should_update_model: bool = True

    # Backref
    bounty_borrowers = None
    legendary_pirates = None
    warlords = None
    daily_bonuses = None

    class Meta:
        db_table = "user"

    def get_bounty_formatted(self) -> str:
        """
        Returns a formatted string of the bounty
        :return: The formatted string e.g. 1,000,000
        """

        from src.utils.string_utils import get_belly_formatted

        return get_belly_formatted(self.bounty)

    def is_arrested(self):
        """
        Returns True if the user is arrested
        :return: True if the user is arrested
        """

        return (
            self.impel_down_release_date is not None
            and self.impel_down_release_date > datetime.datetime.now()
        ) or self.impel_down_is_permanent

    def is_arrested_temporary(self):
        """
        Returns True if the user is temporarily arrested
        :return: True if the user is temporarily arrested
        """

        return self.is_arrested() and not self.impel_down_is_permanent

    def is_arrested_permanent(self):
        """
        Returns True if the user is permanently arrested
        :return: True if the user is permanently arrested
        """

        return self.is_arrested() and self.impel_down_is_permanent

    @staticmethod
    def get_is_not_arrested_statement_condition() -> Any:
        """
        Returns a case statement condition which returns true if the user is not arrested
        :return: The case statement
        """
        return (User.impel_down_is_permanent == False) & (
            (User.impel_down_release_date.is_null())
            | (User.impel_down_release_date < datetime.datetime.now())
        )

    def get_current_impel_down_log(self):
        """
        Returns the current impel down log
        :return: The current impel down log
        """

        from src.model.ImpelDownLog import ImpelDownLog

        return ImpelDownLog.get_current_for_user(self)

    def get_current_bail(self) -> int:
        """
        Get the bail for the user
        :return: The impel_down_log
        """
        current_impel_down_log = self.get_current_impel_down_log()
        if current_impel_down_log is None:
            return 0

        return current_impel_down_log.get_bail()

    def update_private_screen_list(
        self, screen: Screen, previous_screen_list: list[Screen] = None
    ):
        """
        Updates the private screen list
        :param screen: The screen
        :param previous_screen_list: The previous screen list
        """

        if previous_screen_list is not None and len(previous_screen_list) == 0:
            previous_screen_list = None

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

        return self.private_screen_step is not None or self.private_screen_in_edit_id is not None

    def get_private_screen_list(self) -> list[Screen]:
        """
        Returns the private screen list
        :return: The private screen list
        """

        if self.private_screen_list is None:
            return []

        return [
            Screen(str(screen)) for screen in self.private_screen_list.split(c.STANDARD_SPLIT_CHAR)
        ]

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
        self.private_screen_stay = False
        self.private_screen_stay_step = None

    def remove_last_private_screen(self):
        """
        Removes the last private screen
        """

        private_screen_list = self.get_private_screen_list()
        if len(private_screen_list) > 0:
            private_screen_list.pop()
            self.private_screen_list = c.STANDARD_SPLIT_CHAR.join(private_screen_list)

    def add_private_screen(self, screen: Screen):
        """
        Adds a private screen
        :param screen: The screen
        """

        private_screen_list = self.get_private_screen_list()
        private_screen_list.append(screen)
        self.private_screen_list = c.STANDARD_SPLIT_CHAR.join(private_screen_list)

    def replace_last_private_screen(self, screen: Screen):
        """
        Replaces the last private screen
        :param screen: The screen
        """

        self.remove_last_private_screen()
        self.add_private_screen(screen)

    def is_crew_captain(self):
        """
        Returns True if the user is the captain of a Crew
        :return: True if the user is the captain of a Crew
        """

        if self.is_crew_member() and self.crew_role is not None:
            return CrewRole(self.crew_role) is CrewRole.CAPTAIN

        return False

    def is_crew_first_mate(self):
        """
        Returns True if the user is the first mate of a Crew
        :return: True if the user is the first mate of a Crew
        """

        if self.is_crew_member() and self.crew_role is not None:
            return CrewRole(self.crew_role) is CrewRole.FIRST_MATE

        return False

    def is_crew_captain_or_first_mate(self):
        """
        Returns True if the user is the captain or first mate of a Crew
        :return: True if the user is the captain or first mate of a Crew
        """

        return self.is_crew_captain() or self.is_crew_first_mate()

    @staticmethod
    def get_by_tg_id(tg_user_id: str) -> "User":
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

    def in_same_crew(self, user: "User") -> bool:
        """
        Returns True if the user is in the same crew as the given user
        :param user: The user
        :return: True if the user is in the same crew as the given user
        """

        return self.crew is not None and user is not None and self.crew == user.crew

    def get_markdown_mention(self) -> str:
        """
        Returns the markdown mention of the user
        :return: The markdown mention of the user
        """

        from src.service.message_service import mention_markdown_v2

        return mention_markdown_v2(self.tg_user_id, self.tg_first_name)

    def get_you_markdown_mention(self):
        """
        Returns the markdown mention of the user
        :return: The markdown mention of the user
        """

        from src.service.message_service import mention_markdown_v2

        return mention_markdown_v2(self.tg_user_id, phrases.TEXT_YOU)

    def get_markdown_name(self):
        """
        Returns the markdown name of the user
        :return: The markdown name of the user
        """

        from src.service.message_service import escape_valid_markdown_chars

        return escape_valid_markdown_chars(self.tg_first_name)

    def get_max_bounty(self) -> int:
        """
        Returns the max bounty between the user and the crew average
        :return: The max bounty between the user and the crew average
        """

        if self.is_crew_member():
            return max(self.bounty, self.crew.get_average_bounty())

        return self.bounty

    def in_new_world(self):
        """
        Returns True if the user is in the New World
        :return: True if the user is in the New World
        """

        from src.model.enums.Location import is_new_world_by_level

        return is_new_world_by_level(self.location_level)

    def has_higher_bounty_than_crew_average(self) -> bool:
        """
        Returns True if the user has a higher bounty than the crew average
        :return: True if the user has a higher bounty than the crew average
        """

        if self.is_crew_member():
            return self.bounty > self.crew.get_average_bounty()

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

        return (
            self.has_higher_bounty_than_crew_average() and not self.has_bounty_gain_limitations()
        )

    def is_in_paradise(self) -> bool:
        """
        Returns True if the user is in Paradise
        :return: True if the user is in Paradise
        """

        return is_paradise_by_level(self.location_level)

    def get_location(self) -> Location:
        """
        Returns the location of the user
        :return: The location of the user
        """

        return get_by_level(self.location_level)

    def get_location_name(self) -> str:
        """
        Returns the location name of the user
        :return: The location name of the user
        """

        return self.get_location().name

    def has_bounty_gain_limitations(self) -> bool:
        """
        Returns True if the user has bounty gain limitations
        This occurs when the user is in Paradise but has enough bounty to be in the New World, or
        their bounty is higher than that required to reach the final location
        :return: True if the user has bounty gain limitations
        """

        return (
            self.is_in_paradise()
            and (self.bounty + self.pending_bounty) >= get_first_new_world().required_bounty
        ) or ((self.bounty + self.pending_bounty) >= get_last_new_world().required_bounty)

    @staticmethod
    def get_has_bounty_gain_limitations_statement_condition() -> Any:
        """
        Returns the has bounty gain limitations statement condition
        :return: The has bounty gain limitations statement condition
        """

        return (
            (User.location_level < get_first_new_world().level)
            & ((User.bounty + User.pending_bounty) >= get_first_new_world().required_bounty)
        ) | ((User.bounty + User.pending_bounty) >= get_last_new_world().required_bounty)

    def get_in_same_crew_statement_condition(self, other_user: "User") -> Any:
        """
        Returns the in same crew statement condition
        :param other_user: The other user
        :return: The in same crew statement condition
        """

        return (
            User.select(fn.COUNT(User.id)).where(
                (other_user.crew.is_null(False))
                & (other_user.crew == self.crew)
                & (other_user == User.id)
            )
            > 0
        )

    async def is_chat_admin(
        self, update: Update = None, context: ContextTypes.DEFAULT_TYPE = None, chat_id: str = None
    ) -> bool:
        """
        Returns True if the user is an admin of the chat
        :param update: The update
        :param context: The context
        :param chat_id: The chat id
        :return: True if the user is an admin of the chat
        """
        from src.service.user_service import user_is_chat_admin

        return await user_is_chat_admin(self, update=update, context=context, tg_group_id=chat_id)

    async def is_chat_member(self, context: ContextTypes.DEFAULT_TYPE, chat_id: str):
        """
        Returns True if the user is in the chat
        :param context: The context
        :param chat_id: The chat id
        :return: True if the user is in the chat
        """

        from src.service.user_service import user_is_chat_member

        return await user_is_chat_member(self, context=context, tg_group_id=chat_id)

    async def in_authorized_groups(self, context: ContextTypes.DEFAULT_TYPE):
        """
        Returns True if the user is in authorized groups
        :param context: The context
        :return: True if the user is in authorized groups
        """

        group_ids = Env.AUTHORIZED_GROUPS.get_list()
        for group_id in group_ids:
            if await self.is_chat_member(context, group_id):
                return True

        return False

    @staticmethod
    def get_context_data(
        context: ContextTypes.DEFAULT_TYPE,
        key: ContextDataKey,
        tolerate_key_exception: bool = True,
        inner_key: str = None,
    ) -> any:
        """
        Get user data from context
        :param context: The context
        :param key: The key
        :param tolerate_key_exception: If the key is not found, raise CommonChatException instead
        of KeyError
        :param inner_key: The inner key
        :return: The value
        """

        return get_user_context_data(
            context, key, tolerate_key_exception=tolerate_key_exception, inner_key=inner_key
        )

    @staticmethod
    def get_context_data_or_none(
        context: ContextTypes.DEFAULT_TYPE, key: ContextDataKey, inner_key: str = None
    ) -> any:
        """
        Get user data from context or None
        :param context: The context
        :param key: The key
        :param inner_key: The inner key
        :return: The value
        """
        try:
            return get_user_context_data(
                context, key, tolerate_key_exception=False, inner_key=inner_key
            )
        except KeyError:
            return None

    @staticmethod
    def set_context_data(
        context: ContextTypes.DEFAULT_TYPE, key: ContextDataKey, value: Any, inner_key: str = None
    ) -> Any:
        """
        Set user data to context
        :param context: The context
        :param key: The key
        :param value: The value
        :param inner_key: The inner key
        """

        return set_user_context_data(context, key, value, inner_key=inner_key)

    @staticmethod
    def remove_context_data(
        context: ContextTypes.DEFAULT_TYPE, key: ContextDataKey, inner_key: str = None
    ):
        """
        Remove user data from context
        :param context: The context
        :param key: The key
        :param inner_key: The inner key
        """

        try:
            remove_context_data(context, ContextDataType.USER, key, inner_key=inner_key)
        except KeyError:
            pass

    @staticmethod
    def clear_context_filters(context: ContextTypes.DEFAULT_TYPE):
        """
        Clear the context filters
        :param context: The context
        """

        # Clear context filters
        remove_context_data(context, ContextDataType.USER, ContextDataKey.FILTER)
        remove_context_data(context, ContextDataType.USER, ContextDataKey.INBOUND_KEYBOARD)

    def get_expired_bounty_loans(self) -> list:
        """
        Get the expired bounty loans
        :return: The expired bounty loans
        """

        from src.model.enums.BountyLoanStatus import BountyLoanStatus
        from src.model.BountyLoan import BountyLoan

        return self.bounty_borrowers.where(BountyLoan.status == BountyLoanStatus.EXPIRED).order_by(
            BountyLoan.date.asc()
        )

    def has_expired_bounty_loans(self) -> bool:
        """
        Returns True if the user has expired bounty loans
        :return: True if the user has expired bounty loans
        """

        return len(self.get_expired_bounty_loans()) > 0

    def get_expired_bounty_loans_cumulative_percentage(self) -> int:
        """
        Returns the cumulative percentage of the expired bounty loans
        :return: The cumulative percentage of the expired bounty loans
        """

        from src.utils.math_utils import format_percentage_value

        return format_percentage_value(
            get_cumulative_percentage_sum(
                [Env.BOUNTY_LOAN_GARNISH_PERCENTAGE.get_float()]
                * len(self.get_expired_bounty_loans())
            )
        )

    def get_bounty_plus_pending_bounty(self) -> int:
        """
        Returns the bounty plus the pending bounty
        :return: The bounty plus the pending bounty
        """

        return self.bounty + self.pending_bounty

    def has_income_tax(self):
        """
        Returns True if the user has income tax
        :return: True if the user has income tax
        """

        return self.get_income_tax_percentage() > 0

    def reduce_tax_bracket(self, levels_down: int = 1) -> None:
        """
        Reduces the tax bracket by the given amount
        :param levels_down: The number of levels down
        :return: None
        """

        # Get previous tax bracket
        previous_tax_bracket = IncomeTaxBracket.get_previous_bracket(
            self.total_gained_bounty, levels_down
        )

        # Update user
        self.total_gained_bounty = previous_tax_bracket.min_amount
        self.save()

    def get_income_tax_percentage(self) -> float:
        """
        Returns the income tax percentage
        :return: The income tax percentage
        """

        from src.utils.math_utils import format_percentage_value

        return format_percentage_value(
            IncomeTaxBracket.get_bracket(self.total_gained_bounty).percentage
        )

    @staticmethod
    def get_active_interactive_users() -> list:
        """
        Get the active users who interacted with the system
        :return: The active interactive users
        """

        return User.select().where(
            User.last_system_interaction_date
            > datetime.datetime.now()
            - datetime.timedelta(days=Env.INACTIVE_GROUP_USER_DAYS.get_int())
        )

    def get_timezone(self) -> ZoneInfo:
        """
        Returns the timezone of the user
        :return: The timezone of the user
        """

        return ZoneInfo(self.timezone or Env.TZ.get())

    def get_current_time(self) -> datetime.datetime:
        """
        Returns the current time of the user
        :return: The current time of the user
        """

        return datetime.datetime.now(self.get_timezone())

    def get_datetime_formatted(self, date: datetime.datetime) -> str:
        """
        Returns the formatted datetime of the user in their timezone

        :param date: The datetime
        :return: The formatted datetime of the user
        """

        from src.service.date_service import default_datetime_format

        return default_datetime_format(date, self)

    def get_date_formatted(self, date: datetime.datetime) -> str:
        """
        Returns the formatted date of the user in their timezone

        :param date: The date
        :return: The formatted date of the user
        """

        from src.service.date_service import default_date_format

        return default_date_format(date, self)

    def get_crew_role(self):
        """
        Returns the crew role
        :return: The crew role
        """
        return CrewRole(self.crew_role) if self.crew_role is not None else None

    def get_crew_role_description(self):
        """
        Returns the crew role description
        :return: The crew role description
        """

        return self.get_crew_role().get_description()

    def is_legendary_pirate(self) -> bool:
        """
        Returns True if the user is a Legendary Pirate
        :return: True if the user is a Legendary Pirate
        """

        return self.legendary_pirates.count() > 0

    def is_warlord(self) -> bool:
        """
        Returns True if the user is a Warlord
        :return: True if the user is a Warlord
        """
        from src.model.Warlord import Warlord

        return self.warlords.where(Warlord.end_date > datetime.datetime.now()).count() > 0

    def get_mention_url(self) -> str:
        """
        Returns the mention url of the user
        :return: The mention url of the user
        """

        return f"tg://user?id={self.tg_user_id}"

    def get_conscription_remaining_time(self) -> str:
        """
        Get the conscription remaining time
        :return: The conscription remaining time
        """
        from src.service.date_service import get_remaining_duration

        return get_remaining_duration(self.conscription_end_date)

    @staticmethod
    def reset_daily_reward():
        """
        Reset the daily reward
        :return: None
        """

        User.update(can_collect_daily_reward=True).execute()


User.create_table()
