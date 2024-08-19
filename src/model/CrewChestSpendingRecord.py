from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Crew import Crew
from src.model.User import User


class CrewChestSpendingRecord(BaseModel):
    """
    CrewChestSpendingRecord class
    """

    crew = ForeignKeyField(Crew, backref="crew_chest_spending_records")
    amount = BigIntegerField()
    reason = CharField()
    by_user = ForeignKeyField(User, backref="crew_chest_spending_records")
    to_user = ForeignKeyField(User, backref="crew_chest_spending_records", null=True)

    class Meta:
        db_table = "crew_chest_spending_record"


CrewChestSpendingRecord.create_table()
