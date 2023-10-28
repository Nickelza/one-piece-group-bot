import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.User import User
from src.model.enums.income_tax.IncomeTaxBreakdown import IncomeTaxBreakdown
from src.model.enums.income_tax.IncomeTaxContribution import IncomeTaxContribution
from src.model.enums.income_tax.IncomeTaxDeduction import IncomeTaxDeduction
from src.model.enums.income_tax.IncomeTaxEventType import IncomeTaxEventType


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
    deduction_list = TextField()
    contribution_list = TextField()

    class Meta:
        db_table = 'income_tax_event'

    def get_tax_deduction_list(self) -> list[IncomeTaxDeduction]:
        """
        Get the tax deduction list
        :return: The tax deduction list
        """
        return IncomeTaxDeduction.from_string(str(self.deduction_list))

    def get_tax_breakdown_list(self) -> list[IncomeTaxBreakdown]:
        """
        Get the tax breakdown list
        :return: The tax breakdown list
        """
        return IncomeTaxBreakdown.from_string(str(self.breakdown_list))

    def get_tax_contribution_list(self) -> list[IncomeTaxContribution]:
        """
        Get the tax contribution list
        :return: The tax contribution list
        """
        return IncomeTaxContribution.from_string(str(self.contribution_list))

    def get_event_type(self) -> IncomeTaxEventType:
        """
        Get the event type
        :return: The event type
        """
        return IncomeTaxEventType(self.event_type)

    def get_event_type_description(self) -> str:
        """
        Get the event type description
        :return: The event type description
        """
        return self.get_event_type().get_description()


IncomeTaxEvent.create_table()
