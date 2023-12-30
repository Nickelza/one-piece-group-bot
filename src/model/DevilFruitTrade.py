import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.DevilFruit import DevilFruit
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.devil_fruit.DevilFruitTradeStatus import DevilFruitTradeStatus


class DevilFruitTrade(BaseModel):
    """
    Devil Fruit Trade class
    """

    id = PrimaryKeyField()
    devil_fruit = ForeignKeyField(
        DevilFruit,
        null=True,
        backref="devil_fruit_trades",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    giver = ForeignKeyField(
        User,
        null=True,
        backref="devil_fruit_trade_givers",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    receiver = ForeignKeyField(
        User,
        null=True,
        backref="devil_fruit_trade_receivers",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    source = SmallIntegerField()
    price = BigIntegerField(null=True)
    tax_percentage = FloatField(null=True)
    reason = CharField(max_length=100, null=True)
    date = DateTimeField(default=datetime.datetime.now)
    status = SmallIntegerField(default=DevilFruitTradeStatus.PENDING)
    group_chat = ForeignKeyField(
        GroupChat,
        null=True,
        backref="devil_fruit_trade_group_chats",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    message_id = IntegerField(null=True)

    class Meta:
        db_table = "devil_fruit_trade"


DevilFruitTrade.create_table()
