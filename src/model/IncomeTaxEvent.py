import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.User import User
from src.model.enums.income_tax.IncomeTaxReduction import IncomeTaxReduction


class IncomeTaxEvent(BaseModel):
    """
    IncomeTaxEvent class
    """
    id = PrimaryKeyField()
    user = ForeignKeyField(User, backref='income_tax_events')
    event_id = IntegerField()
    event_type = CharField()
    date = DateTimeField(default=datetime.datetime.now)
    starting_amount = BigIntegerField()
    amount = BigIntegerField()
    breakdown_list = TextField()
    reduction_list = TextField()

    class Meta:
        db_table = 'income_tax_event'

    def get_tax_reduction_list(self) -> list[IncomeTaxReduction]:
        """
        Get the tax reduction list
        :return: The tax reduction list
        """
        return IncomeTaxReduction.from_string(str(self.reduction_list))


IncomeTaxEvent.create_table()
