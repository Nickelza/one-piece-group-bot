from peewee import *

from src.model.BaseModel import BaseModel
from src.model.User import User


class LegendaryPirate(BaseModel):
    """
    Legendary Pirate class
    """

    user = ForeignKeyField(
        User, backref="legendary_pirates", on_delete="CASCADE", on_update="CASCADE"
    )
    epithet = CharField(max_length=99, null=True)
    reason = CharField(max_length=999, null=True)

    class Meta:
        db_table = "legendary_pirate"


LegendaryPirate.create_table()
