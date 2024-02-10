import datetime
from typing import Any

from peewee import *

import resources.Environment as Env
from src.model.BaseModel import BaseModel, db_obj
from src.model.enums.GameStatus import GameStatus
from src.model.enums.crew.CrewChestSpendingReason import CrewChestSpendingReason
from src.model.enums.crew.CrewLevelUpgradeType import CrewLevelUpgradeType
from src.model.enums.crew.CrewRole import CrewRole
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType


class Crew(BaseModel):
    """
    Crew class
    """

    id: int | PrimaryKeyField = PrimaryKeyField()
    name: str | CharField = CharField(max_length=Env.CREW_NAME_MAX_LENGTH.get_int())
    creation_date: datetime.datetime | DateTimeField = DateTimeField(default=datetime.datetime.now)
    can_accept_new_members: bool | BooleanField = BooleanField(default=True)
    is_active: bool | BooleanField = BooleanField(default=True)
    disband_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    chest_amount: int | BigIntegerField = BigIntegerField(default=0)
    total_gained_chest_amount: int | BigIntegerField = BigIntegerField(default=0)
    level: int | IntegerField = IntegerField(default=1)
    max_abilities: int | IntegerField = IntegerField(default=Env.CREW_MAX_ABILITIES.get_int())
    can_promote_first_mate: bool = BooleanField(default=True)
    max_members: int | IntegerField = IntegerField(default=Env.CREW_MAX_MEMBERS.get_int())
    description: str | CharField = CharField(
        max_length=Env.CREW_DESCRIPTION_MAX_LENGTH.get_int(), null=True
    )
    required_bounty: int | BigIntegerField = BigIntegerField(default=0)
    allow_view_in_search: bool | BooleanField = BooleanField(default=True)
    allow_join_from_search: bool | BooleanField = BooleanField(default=True)
    is_full: bool | BooleanField = BooleanField(default=False)

    class Meta:
        db_table = "crew"

    def get_average_bounty(self) -> int:
        """
        Returns the average bounty of the crew
        :return: The average bounty
        """

        from src.model.User import User

        return self.crew_members.select(fn.Avg(User.bounty)).scalar()

    def get_average_location_level(self) -> int:
        """
        Returns the average location level of the crew
        :return: The average location level
        """

        from src.model.User import User

        return self.crew_members.select(fn.Avg(User.location_level)).scalar()

    def get_members(self, limit: int = None, page: int = 1) -> list:
        """
        Returns the crew members ordered by join date

        :param limit: The number of members to return. If None, returns all members
        :param page: The page to return. If None, returns the first page
        :return: The crew member
        """

        from src.model.User import User

        if limit is not None:
            return (
                self.crew_members.select()
                .order_by(User.crew_join_date.asc())
                .paginate(page, limit)
            )

        return self.crew_members.select().order_by(User.crew_join_date.asc())

    @staticmethod
    def get_by_name_if_active(name: str) -> "Crew":
        """
        Returns the crew by name, case-insensitive
        :param name: The name
        :return: The crew
        """

        return Crew.get_or_none((Crew.name**name) & (Crew.is_active == True))

    @staticmethod
    def logical_get(crew_id: int) -> "Crew":
        """
        Returns the Crew if it exists and is active
        :param crew_id: The crew id
        :return: The crew
        """

        return Crew.get_or_none((Crew.id == crew_id) & (Crew.is_active == True))

    def get_captain(self) -> Any:
        """
        Returns the crew captain
        :return: The crew captain
        """

        from src.model.User import User

        return self.crew_members.select().where(User.crew_role == CrewRole.CAPTAIN).get()

    def get_first_mate(self) -> Any:
        """
        Returns the crew first mate
        :return: The crew first mate
        """

        from src.model.User import User

        return (
            self.crew_members.select().where(User.crew_role == CrewRole.FIRST_MATE).get_or_none()
        )

    def has_first_mate(self) -> bool:
        """
        Returns True if the crew has a first mate
        :return: True if the crew has a first mate
        """

        return self.get_first_mate() is not None

    def get_member_count(self) -> int:
        """
        Returns the number of crew members
        :return: The number of crew members
        """

        return self.crew_members.select().count()

    def get_chest_contributions(self) -> list:
        """
        Returns the crew members ordered by contribution
        :return: The crew members
        """

        from src.model.CrewMemberChestContribution import CrewMemberChestContribution

        return self.crew_member_chest_contributions.select().order_by(
            CrewMemberChestContribution.amount.desc()
        )

    def get_powerup_price(self, reason: CrewChestSpendingReason) -> int:
        """
        Returns the next powerup price
        :param reason: The reason
        :return: The next powerup price
        """

        # Not level up, price is current level * BASE_PRICE
        if reason is not CrewChestSpendingReason.LEVEL_UP:
            return Env.CREW_POWERUP_BASE_PRICE.get_int() * self.level

        # Level up, price is double the previous
        return Env.CREW_POWERUP_BASE_PRICE.get_int() * (2 ** (self.level - 1))

    def get_powerup_price_formatted(self, reason: CrewChestSpendingReason) -> str:
        """
        Returns the next powerup price formatted
        :param reason: The reason
        :return: The next powerup price formatted
        """

        from src.service.string_service import get_belly_formatted

        return get_belly_formatted(self.get_powerup_price(reason))

    def get_crew_chest_formatted(self) -> str:
        """
        Returns the crew chest formatted
        :return: The crew chest formatted
        """

        from src.service.string_service import get_belly_formatted

        return get_belly_formatted(self.chest_amount)

    def get_active_abilities(self) -> list:
        """
        Returns the crew active abilities
        :return: The crew active abilities
        """

        from src.model.CrewAbility import CrewAbility

        return self.crew_abilities.select().where(
            CrewAbility.expiration_date > datetime.datetime.now()
        )

    def get_active_ability(self, ability_type: DevilFruitAbilityType) -> list:
        """
        Returns the crew active ability of the given type
        :param ability_type: The ability type
        :return: The crew active ability
        """

        from src.model.CrewAbility import CrewAbility

        return self.crew_abilities.select().where(
            (CrewAbility.expiration_date > datetime.datetime.now())
            & (CrewAbility.ability_type == ability_type.value)
        )

    def get_next_level_upgrade_type(self):
        """
        Returns the next level upgrade type
        :return: The next level upgrade type
        """

        return CrewLevelUpgradeType.get_by_level(self.level + 1)

    def get_upgrade_type_count(self, upgrade_type: CrewLevelUpgradeType) -> int:
        """
        Returns the number of upgrades of the given type
        :param upgrade_type: The upgrade type
        :return: The number of upgrades
        """

        if upgrade_type is CrewLevelUpgradeType.MEMBER:
            return self.max_members

        return self.max_abilities

    def level_up(self):
        """
        Level up the crew
        :return: None
        """
        # Increase max members or abilities
        upgrade_type = self.get_next_level_upgrade_type()

        if upgrade_type is CrewLevelUpgradeType.MEMBER:
            self.max_members += 1
            self.can_accept_new_members = True
            self.set_is_full()
        elif upgrade_type is CrewLevelUpgradeType.ABILITY:
            self.max_abilities += 1

        self.level += 1

        self.save()

    @staticmethod
    def reset_level() -> None:
        """
        Reset the crew level
        :return: None
        """

        # Reset level
        conditions: list[tuple[bool, int]] = [
            # If level / 2 is higher than allowed after reset, set to max
            (
                (Crew.level / 2) > Env.CREW_MAX_LEVEL_AFTER_RESET.get_int(),
                Env.CREW_MAX_LEVEL_AFTER_RESET.get_int(),
            ),
            # If level / 2 is lower than 1 after reset, set to 1
            ((Crew.level / 2) < 1, 1),
        ]

        # Else, set to level / 2
        case_stmt = Case(None, conditions, Crew.level / 2)
        Crew.update(level=case_stmt).execute()

        # Reset max allowed members and abilities
        Crew.update(
            max_members=(Env.CREW_MAX_MEMBERS.get_int() + fn.ROUND((Crew.level - 1) / 2)),
            max_abilities=(Env.CREW_MAX_ABILITIES.get_int() + fn.FLOOR((Crew.level - 1) / 2)),
        ).execute()

        # Reset is full attribute
        Crew.set_is_full_for_all_crews()

    def get_name_escaped(self) -> str:
        """
        Returns the crew name escaped
        :return: The crew name escaped
        """

        from src.service.message_service import escape_valid_markdown_chars

        return escape_valid_markdown_chars(self.name)

    def get_description_escaped(self) -> str:
        """
        Returns the crew description escaped
        :return: The crew description escaped
        """

        from src.service.message_service import escape_valid_markdown_chars

        return escape_valid_markdown_chars(self.description)

    def get_required_bounty_formatted(self) -> str:
        """
        Returns the crew required bounty formatted
        :return: The crew required bounty formatted
        """

        from src.service.string_service import get_belly_formatted

        return get_belly_formatted(self.required_bounty)

    def set_is_full(self) -> None:
        """
        Set the crew as full
        :return: None
        """
        if self.get_member_count() >= self.max_members:
            self.is_full = True
        else:
            self.is_full = False

        self.save()

    @staticmethod
    def set_is_full_for_all_crews() -> None:
        """
        Set the crew as full for all crews
        :return: None
        """

        raw_query = (
            "update crew"
            " set is_full = IF(((select count(*) from user where crew_id = crew.id) <"
            " crew.max_members), 0, 1)"
            " where true;"
        )
        db_obj.get_db().execute_sql(raw_query)

    def get_active_davy_back_fight(self) -> Any:
        """
        Returns the current Davy Back Fight
        :return: The current Davy Back Fight
        """
        from src.model.DavyBackFight import DavyBackFight

        return (
            DavyBackFight.select()
            .where(
                ((DavyBackFight.challenger_crew == self) | (DavyBackFight.opponent_crew == self))
                & (
                    (DavyBackFight.status == GameStatus.COUNTDOWN_TO_START)
                    | (DavyBackFight.status == GameStatus.IN_PROGRESS)
                )
            )
            .get_or_none()
        )

    def get_in_progress_davy_back_fight(self) -> Any:
        """
        Returns the in progress Davy Back Fight
        :return: The in progress Davy Back Fight
        """

        from src.model.DavyBackFight import DavyBackFight

        return (
            DavyBackFight.select()
            .where(
                ((DavyBackFight.challenger_crew == self) | (DavyBackFight.opponent_crew == self))
                & (DavyBackFight.status == GameStatus.IN_PROGRESS)
            )
            .get_or_none()
        )

    def get_pending_davy_back_fight(self) -> Any:
        """
        Returns the pending Davy Back Fight as challenger
        :return: The pending Davy Back Fight
        """

        from src.model.DavyBackFight import DavyBackFight

        return (
            self.davy_back_fights_challengers.select()
            .where(DavyBackFight.status == GameStatus.AWAITING_OPPONENT_CONFIRMATION)
            .get_or_none()
        )

    def get_penalty_davy_back_fight(self) -> Any:
        """
        Returns the penalty Davy Back Fight
        :return: The penalty Davy Back Fight
        """

        from src.model.DavyBackFight import DavyBackFight

        return (
            DavyBackFight.select()
            .where(
                (
                    (
                        (DavyBackFight.challenger_crew == self)
                        & (DavyBackFight.status == GameStatus.LOST)
                    )
                    | (
                        (DavyBackFight.opponent_crew == self)
                        & (DavyBackFight.status == GameStatus.WON)
                    )
                )
                & (
                    DavyBackFight.end_date
                    > (
                        datetime.datetime.now()
                        - datetime.timedelta(
                            hours=Env.DAVY_BACK_FIGHT_LOSE_PENALTY_DURATION.get_int()
                        )
                    )
                )
            )
            .get_or_none()
        )

    def get_name_with_deeplink(self, add_level: bool = True):
        """
        Returns the crew name with deeplink
        :param add_level: Whether to add the level to the name
        :return: The crew name with deeplink
        """

        from src.service.crew_service import get_crew_name_with_deeplink

        return get_crew_name_with_deeplink(self, add_level=add_level)

    def has_active_davy_back_fight(self) -> bool:
        """
        Returns True if the crew has an active Davy Back Fight
        :return: True if the crew has an active Davy Back Fight
        """

        return self.get_active_davy_back_fight() is not None

    def has_penalty_davy_back_fight(self) -> bool:
        """
        Returns True if the crew has a penalty Davy Back Fight
        :return: True if the crew has a penalty Davy Back Fight
        """

        return self.get_penalty_davy_back_fight() is not None


Crew.create_table()
