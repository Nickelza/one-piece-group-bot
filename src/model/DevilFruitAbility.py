from peewee import *

from src.model.BaseModel import BaseModel
from src.model.DevilFruit import DevilFruit


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


DevilFruitAbility.create_table()
