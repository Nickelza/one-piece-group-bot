from peewee import *

from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.BountyGiftRole import BountyGiftRole
from src.model.enums.BountyGiftStatus import BountyGiftStatus


class BountyGift(BaseModel):
    """
    BountyGift class
    """

    sender = ForeignKeyField(
        User, backref="bounty_gift_senders", on_delete="CASCADE", on_update="CASCADE"
    )
    receiver = ForeignKeyField(
        User, backref="bounty_gift_receivers", on_delete="CASCADE", on_update="CASCADE"
    )
    amount = BigIntegerField()
    tax_percentage = FloatField()
    status = SmallIntegerField(default=BountyGiftStatus.AWAITING_CONFIRMATION)
    group_chat = ForeignKeyField(
        GroupChat,
        null=True,
        backref="bounty_gift_groups_chats",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    message_id = IntegerField(null=True)

    @staticmethod
    def get_total_belly_sent_or_received(user: User, role: BountyGiftRole) -> int:
        """
        Get the total amount of belly sent or received by a user
        param user: The user
        param role: The role (sender or receiver)
        return: The total amount of belly sent or received
        """

        if role is BountyGiftRole.SENDER:
            return (
                BountyGift()
                .select(fn.SUM(BountyGift.amount))
                .where(
                    (BountyGift.sender == user) & (BountyGift.status == BountyGiftStatus.CONFIRMED)
                )
                .scalar()
            )

        return (
            BountyGift()
            .select(fn.SUM(BountyGift.amount))
            .where(
                (BountyGift.receiver == user) & (BountyGift.status == BountyGiftStatus.CONFIRMED)
            )
            .scalar()
        )

    @staticmethod
    def get_highest_belly_sent_or_received(user: User, role: BountyGiftRole) -> "BountyGift":
        """
        Get the highest bounty sent or received by a user
        param user: The user
        param role: The role (sender or receiver)
        return: The highest bounty sent or received
        """

        if role is BountyGiftRole.SENDER:
            return (
                BountyGift()
                .select()
                .where(
                    (BountyGift.sender == user) & (BountyGift.status == BountyGiftStatus.CONFIRMED)
                )
                .order_by(BountyGift.amount.desc())
                .first()
            )

        return (
            BountyGift()
            .select()
            .where(
                (BountyGift.receiver == user) & (BountyGift.status == BountyGiftStatus.CONFIRMED)
            )
            .order_by(BountyGift.amount.desc())
            .first()
        )

    @staticmethod
    def get_top_givers_or_receiver(user: User, role: BountyGiftRole) -> (User, int):
        """
        Get the top user who was given the most belly or gave the most belly by/to a user and the total amount
        param user: The user
        param role: The role (sender or receiver)
        return: The top user and the total amount
        """

        if role is BountyGiftRole.SENDER:
            top_receiver = (
                BountyGift()
                .select(BountyGift.receiver, fn.SUM(BountyGift.amount).alias("total"))
                .where(
                    (BountyGift.sender == user) & (BountyGift.status == BountyGiftStatus.CONFIRMED)
                )
                .group_by(BountyGift.receiver)
                .order_by(fn.SUM(BountyGift.amount).desc())
                .first()
            )
            return top_receiver.receiver, top_receiver.total

        top_sender = (
            BountyGift()
            .select(BountyGift.sender, fn.SUM(BountyGift.amount).alias("total"))
            .where(
                (BountyGift.receiver == user) & (BountyGift.status == BountyGiftStatus.CONFIRMED)
            )
            .group_by(BountyGift.sender)
            .order_by(fn.SUM(BountyGift.amount).desc())
            .first()
        )
        return top_sender.sender, top_sender.total

    def get_status(self) -> BountyGiftStatus:
        """
        Get the status
        :return: The status
        """
        return BountyGiftStatus(self.status)

    class Meta:
        db_table = "bounty_gift"


BountyGift.create_table()
