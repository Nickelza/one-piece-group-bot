import datetime
from typing import Any

from peewee import *

import resources.Environment as Env
from src.model.BaseModel import BaseModel
from src.model.enums.crew.CrewChestSpendingReason import CrewChestSpendingReason
from src.model.enums.crew.CrewLevelUpgradeType import CrewLevelUpgradeType
from src.model.enums.crew.CrewRole import CrewRole
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType


class Crew(BaseModel):
    """
    Crew class
    """

    id: int = PrimaryKeyField()
    name: str | CharField = CharField(max_length=Env.CREW_NAME_MAX_LENGTH.get_int())
    creation_date: datetime.datetime = DateTimeField(default=datetime.datetime.now)
    can_accept_new_members: bool = BooleanField(default=True)
    is_active: bool = BooleanField(default=True)
    disband_date: datetime.datetime = DateTimeField(null=True)
    chest_amount: int = BigIntegerField(default=0)
    level: int = IntegerField(default=1)
    max_abilities: int = IntegerField(default=1)
    can_promote_first_mate: bool = BooleanField(default=True)
    max_members: int = IntegerField(default=Env.CREW_MAX_MEMBERS.get_int())

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

    def is_full(self) -> bool:
        """
        Returns True if the crew is full
        :return: True if the crew is full
        """

        return len(self.get_members()) >= self.max_members

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

        from src.service.bounty_service import get_belly_formatted

        return get_belly_formatted(self.get_powerup_price(reason))

    def get_crew_chest_formatted(self) -> str:
        """
        Returns the crew chest formatted
        :return: The crew chest formatted
        """

        from src.service.bounty_service import get_belly_formatted

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
        elif upgrade_type is CrewLevelUpgradeType.ABILITY:
            self.max_abilities += 1

        self.level += 1

        self.save()


Crew.create_table()
