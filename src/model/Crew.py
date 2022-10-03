import datetime

from peewee import *

import resources.Environment as Env
from src.model.BaseModel import BaseModel


class Crew(BaseModel):
    """
    Crew class
    """
    id = PrimaryKeyField()
    name = CharField(max_length=Env.CREW_NAME_MAX_LENGTH.get_int(), unique=True)
    creation_date = DateTimeField(default=datetime.datetime.now)
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

    def get_members(self) -> list:
        """
        Returns the crew members
        :return: The crew member
        """

        from src.model.User import User
        return self.crew_members.select().order_by(User.crew_join_date.asc())

    @staticmethod
    def get_by_name(name: str) -> 'Crew':
        """
        Returns the crew by name, case-insensitive
        :param name: The name
        :return: The crew
        """

        return Crew.get_or_none(Crew.name ** name)


Crew.create_table()
