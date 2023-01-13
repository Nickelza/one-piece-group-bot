import datetime
from typing import Any

from peewee import *

import resources.Environment as Env
from src.model.BaseModel import BaseModel
from src.model.enums.CrewRole import CrewRole


class Crew(BaseModel):
    """
    Crew class
    """
    id = PrimaryKeyField()
    name = CharField(max_length=Env.CREW_NAME_MAX_LENGTH.get_int(), unique=True)
    creation_date = DateTimeField(default=datetime.datetime.now)
    can_accept_new_members = BooleanField(default=True)
    is_active = BooleanField(default=True)

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
    def get_by_name(name: str) -> 'Crew':
        """
        Returns the crew by name, case-insensitive
        :param name: The name
        :return: The crew
        """

        return Crew.get_or_none(Crew.name ** name)

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

    def get_member_count(self) -> int:
        """
        Returns the number of crew members
        :return: The number of crew members
        """

        return self.crew_members.select().count()


Crew.create_table()
