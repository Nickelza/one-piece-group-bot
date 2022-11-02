import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.User import User
from src.model.enums.BountyGiftStatus import BountyGiftStatus


class BountyGift(BaseModel):
    """
    BountyGift class
    """
    id = PrimaryKeyField()
    sender = ForeignKeyField(User, backref='bounty_gift_senders', on_delete='CASCADE', on_update='CASCADE')
    receiver = ForeignKeyField(User, backref='bounty_gift_receivers', on_delete='CASCADE', on_update='CASCADE')
    amount = BigIntegerField()
    tax_percentage = IntegerField()
    date = DateTimeField(default=datetime.datetime.now)
    status = SmallIntegerField(default=BountyGiftStatus.AWAITING_CONFIRMATION)
    message_id = IntegerField(null=True)

    class Meta:
        db_table = 'bounty_gift'


BountyGift.create_table()
