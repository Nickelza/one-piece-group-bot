import datetime
from typing import Any

from peewee import *

import resources.Environment as Env
from src.model.BaseModel import BaseModel
from src.model.enums.crew.CrewRole import CrewRole
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType


class Crew(BaseModel):
    """
    Crew class
    """
    id = PrimaryKeyField()
    name = CharField(max_length=Env.CREW_NAME_MAX_LENGTH.get_int())
    creation_date = DateTimeField(default=datetime.datetime.now)
    can_accept_new_members = BooleanField(default=True)
    is_active = BooleanField(default=True)
    disband_date = DateTimeField(null=True)
    chest_amount = BigIntegerField(default=0)
    powerup_counter = IntegerField(default=0)
    max_abilities = IntegerField(default=1)
    can_promote_first_mate = BooleanField(default=True)

    class Meta:
        db_table = 'crew'

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
            return self.crew_members.select().order_by(User.crew_join_date.asc()).paginate(page, limit)

        return self.crew_members.select().order_by(User.crew_join_date.asc())

    @staticmethod
    def get_by_name_if_active(name: str) -> 'Crew':
        """
        Returns the crew by name, case-insensitive
        :param name: The name
        :return: The crew
        """

        return Crew.get_or_none((Crew.name ** name) & (Crew.is_active == True))

    def is_full(self) -> bool:
        """
        Returns True if the crew is full
        :return: True if the crew is full
        """

        return len(self.get_members()) >= Env.CREW_MAX_MEMBERS.get_int()

    @staticmethod
    def logical_get(crew_id: int) -> 'Crew':
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
        return self.crew_members.select().where(User.crew_role == CrewRole.FIRST_MATE).get_or_none()

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

        return self.crew_member_chest_contributions.select().order_by(CrewMemberChestContribution.amount.desc())

    def get_powerup_price(self) -> int:
        """
        Returns the next powerup price
        :return: The next powerup price
        """

        if self.powerup_counter == 0:
            return Env.CREW_POWERUP_BASE_PRICE.get_int()

        return Env.CREW_POWERUP_BASE_PRICE.get_int() * (2 ** int(str(self.powerup_counter)))

    def get_powerup_price_formatted(self) -> str:
        """
        Returns the next powerup price formatted
        :return: The next powerup price formatted
        """

        from src.service.bounty_service import get_belly_formatted

        return get_belly_formatted(self.get_powerup_price())

    def can_powerup(self) -> bool:
        """
        Returns True if the crew can powerup
        :return: True if the crew can powerup
        """

        return self.chest_amount >= self.get_powerup_price()

    def get_crew_chest_formatted(self) -> str:
        """
        Returns the crew chest formatted
        :return: The crew chest formatted
        """

        from src.service.bounty_service import get_belly_formatted

        return get_belly_formatted(int(str(self.chest_amount)))

    def get_active_abilities(self) -> list:
        """
        Returns the crew active abilities
        :return: The crew active abilities
        """

        from src.model.CrewAbility import CrewAbility

        return self.crew_abilities.select().where(CrewAbility.expiration_date > datetime.datetime.now())

    def get_active_ability(self, ability_type: DevilFruitAbilityType) -> list:
        """
        Returns the crew active ability of the given type
        :param ability_type: The ability type
        :return: The crew active ability
        """

        from src.model.CrewAbility import CrewAbility

        return self.crew_abilities.select().where((CrewAbility.expiration_date > datetime.datetime.now())
                                                  & (CrewAbility.ability_type == ability_type.value))


Crew.create_table()
