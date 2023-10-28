import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType


class CrewAbility(BaseModel):
    """
    CrewAbility class
    """
    id = PrimaryKeyField()
    crew = ForeignKeyField(Crew, backref='crew_abilities')
    ability_type = SmallIntegerField()
    value = SmallIntegerField()
    acquired_method = SmallIntegerField()
    acquired_user = ForeignKeyField(User, backref='crew_abilities', null=True)
    acquired_date = DateTimeField(default=datetime.datetime.now)
    expiration_date = DateTimeField(null=True)

    class Meta:
        db_table = 'crew_ability'

    def get_ability_type(self):
        """
        Returns the ability type
        :return: The ability type
        """
        return DevilFruitAbilityType(self.ability_type)

    def get_description(self):
        """
        Returns the description of the ability
        :return: The description
        """
        return self.get_ability_type().get_description()


CrewAbility.create_table()
