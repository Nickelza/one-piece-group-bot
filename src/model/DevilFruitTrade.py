import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.DevilFruit import DevilFruit
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.devil_fruit.DevilFruitCategory import DevilFruitCategory
from src.model.enums.devil_fruit.DevilFruitSource import DevilFruitSource
from src.model.enums.devil_fruit.DevilFruitTradeStatus import DevilFruitTradeStatus


class DevilFruitTrade(BaseModel):
    """
    Devil Fruit Trade class
    """

    id = PrimaryKeyField()
    devil_fruit: DevilFruit | ForeignKeyField = ForeignKeyField(
        DevilFruit,
        null=True,
        backref="devil_fruit_trades",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    giver: User | ForeignKeyField = ForeignKeyField(
        User,
        null=True,
        backref="devil_fruit_trade_givers",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    receiver: User | ForeignKeyField = ForeignKeyField(
        User,
        null=True,
        backref="devil_fruit_trade_receivers",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    source: DevilFruitSource | SmallIntegerField = SmallIntegerField()
    price: int | BigIntegerField = BigIntegerField(null=True)
    tax_percentage: float | FloatField = FloatField(null=True)
    reason: str | CharField = CharField(max_length=100, null=True)
    date: datetime.datetime | DateTimeField = DateTimeField(default=datetime.datetime.now)
    date_sold: datetime.datetime | DateTimeField = DateTimeField(null=True)
    status: DevilFruitTradeStatus | SmallIntegerField = SmallIntegerField(
        default=DevilFruitTradeStatus.PENDING
    )
    group_chat: GroupChat | ForeignKeyField = ForeignKeyField(
        GroupChat,
        null=True,
        backref="devil_fruit_trade_group_chats",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    message_id: int = IntegerField(null=True)

    class Meta:
        db_table = "devil_fruit_trade"

    @staticmethod
    def get_average_price(devil_fruit_category: DevilFruitCategory) -> int:
        """
        Get the average price of the sold fruits in a category
        :return: The average price
        """

        avg = (
            DevilFruitTrade.select(fn.AVG(DevilFruitTrade.price))
            .join(DevilFruit)
            .where(
                (DevilFruit.category == devil_fruit_category)
                & (DevilFruitTrade.price.is_null(False))
                & (DevilFruitTrade.status == DevilFruitTradeStatus.COMPLETED)
                & (DevilFruitTrade.price > 0)
            )
            .scalar()
        )

        return int(avg) if avg is not None else None

    def get_source(self) -> DevilFruitSource:
        """
        Get the source of the trade
        :return: The source
        """
        return DevilFruitSource(self.source)

    def get_status(self) -> DevilFruitTradeStatus:
        """
        Get the status of the trade
        :return: The status
        """
        return DevilFruitTradeStatus(self.status)

    @staticmethod
    def delete_pending_trades(devil_fruit: DevilFruit):
        """
        Delete pending trades of a devil fruit
        :param devil_fruit: The devil fruit
        :return: None
        """
        DevilFruitTrade.delete().where(
            (DevilFruitTrade.devil_fruit == devil_fruit)
            & (DevilFruitTrade.status == DevilFruitTradeStatus.PENDING)
        ).execute()

    @staticmethod
    def delete_pending_trades_in_shop(devil_fruit: DevilFruit):
        """
        Delete pending trades of a devil fruit in the shop
        :param devil_fruit: The devil fruit
        :return: None
        """
        DevilFruitTrade.delete().where(
            (DevilFruitTrade.devil_fruit == devil_fruit)
            & (DevilFruitTrade.status == DevilFruitTradeStatus.PENDING)
            & (DevilFruitTrade.source == DevilFruitSource.SHOP)
        ).execute()

    @staticmethod
    def delete_pending_trades_in_group(
        devil_fruit: DevilFruit, group_chat: GroupChat, exclude_id: int
    ):
        """
        Delete pending trades of a devil fruit in a group chat
        :param devil_fruit: The devil fruit
        :param group_chat: The group chat
        :param exclude_id: The id to exclude
        :return: None
        """
        DevilFruitTrade.delete().where(
            (DevilFruitTrade.devil_fruit == devil_fruit)
            & (DevilFruitTrade.status == DevilFruitTradeStatus.PENDING)
            & (DevilFruitTrade.group_chat == group_chat)
            & (DevilFruitTrade.id != exclude_id)
        ).execute()

    @staticmethod
    def get_pending_in_shop(devil_fruit: DevilFruit) -> "DevilFruitTrade":
        """
        Get a pending trade in the shop
        :param devil_fruit: The devil fruit
        :return: The trade
        """

        return DevilFruitTrade.get_or_none(
            DevilFruitTrade.devil_fruit == devil_fruit,
            DevilFruitTrade.status == DevilFruitTradeStatus.PENDING,
            DevilFruitTrade.source == DevilFruitSource.SHOP,
        )

    @staticmethod
    def get_all_selling_in_shop_or_group(
        group_chat: GroupChat = None, user: User = None
    ) -> list["DevilFruitTrade"]:
        """
        Get all trades in the shop
        :param group_chat: The group chat
        :param user: The user
        :return: The trades
        """
        return DevilFruitTrade.select().where(
            # Only non completed trades
            (DevilFruitTrade.devil_fruit.is_null(False))
            & (DevilFruitTrade.status == DevilFruitTradeStatus.PENDING)
            & (
                # Is in shop
                (DevilFruitTrade.source == DevilFruitSource.SHOP)
                | (
                    # Is in the given group chat
                    (DevilFruitTrade.source == DevilFruitSource.USER)
                    & (DevilFruitTrade.group_chat == group_chat)
                    # Not reserved to a specific user or reserved to the given user
                    & ((DevilFruitTrade.receiver.is_null()) | (DevilFruitTrade.receiver == user))
                )
            )
        )


DevilFruitTrade.create_table()
