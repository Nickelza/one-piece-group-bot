import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Crew import Crew
from src.model.User import User


class CrewMemberChestContribution(BaseModel):
    """
    CrewMemberChestContribution class
    """
    id = PrimaryKeyField()
    crew = ForeignKeyField(Crew, backref='crew_member_chest_contributions')
    user = ForeignKeyField(User, backref='crew_member_chest_contributions')
    amount = BigIntegerField(default=0)
    last_contribution_date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'crew_member_chest_contribution'


CrewMemberChestContribution.create_table()
