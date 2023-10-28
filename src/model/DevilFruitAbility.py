from typing import Optional

from peewee import *

from src.model import User
from src.model.BaseModel import BaseModel
from src.model.DevilFruit import DevilFruit
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.enums.devil_fruit.DevilFruitStatus import DevilFruitStatus


class DevilFruitAbility(BaseModel):
    """
    Devil Fruit Ability class
    """
    id = PrimaryKeyField()
    devil_fruit = ForeignKeyField(DevilFruit, backref='devil_fruit_abilities', on_delete='CASCADE', on_update='CASCADE')
    ability_type = SmallIntegerField()
    value = SmallIntegerField()

    class Meta:
        db_table = 'devil_fruit_ability'

    @staticmethod
    def get_user_ability(user: User, ability_type: DevilFruitAbilityType) -> Optional['DevilFruitAbility']:
        """
        Given a user and an ability type, get the ability of a Devil Fruit eaten by the user with the given ability type

        :param user: The user
        :param ability_type: The ability type
        :return: The ability, if any
        """

        return (DevilFruitAbility
                .select()
                .join(DevilFruit)
                .where((DevilFruit.owner == user)
                       & (DevilFruit.status == DevilFruitStatus.EATEN)
                       & (DevilFruitAbility.ability_type == ability_type))
                .get_or_none())


DevilFruitAbility.create_table()
