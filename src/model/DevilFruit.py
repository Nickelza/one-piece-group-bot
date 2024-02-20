import datetime
from typing import Optional

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.devil_fruit.DevilFruitCategory import DevilFruitCategory
from src.model.enums.devil_fruit.DevilFruitStatus import DevilFruitStatus
from src.model.enums.devil_fruit.DevilFruitTradeStatus import DevilFruitTradeStatus


class DevilFruit(BaseModel):
    """
    DevilFruit class
    """

    id: int | PrimaryKeyField = PrimaryKeyField()
    category: int | DevilFruitCategory = SmallIntegerField()
    name: str | CharField = CharField(max_length=50)
    model: str | CharField = CharField(max_length=50, null=True, unique=True)
    status: DevilFruitTradeStatus | SmallIntegerField = SmallIntegerField(
        default=DevilFruitStatus.NEW
    )
    owner: User | ForeignKeyField = ForeignKeyField(
        User, null=True, backref="devil_fruit_owners", on_delete="RESTRICT", on_update="CASCADE"
    )
    collection_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    eaten_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    expiration_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    release_group_chat: GroupChat | ForeignKeyField = ForeignKeyField(
        GroupChat,
        null=True,
        backref="devil_fruit_release_groups_chats",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    release_date = DateTimeField(null=True)
    release_message_id = IntegerField(null=True)
    should_show_abilities = BooleanField(default=False)

    class Meta:
        db_table = "devil_fruit"

    def get_full_name(self) -> str:
        """
        Get fruit full name
        :return: Fruit full name
        """
        if self.model:
            return f"{self.name}, Model: {self.model}"

        if self.get_category() is DevilFruitCategory.SMILE:
            return f"{self.name} SMILE"

        return str(self.name)

    @staticmethod
    def get_by_owner_if_eaten(user: User) -> Optional["DevilFruit"]:
        """
        Get the devil fruit eaten by the user
        :param user: The user
        :return: The devil fruit
        """

        return DevilFruit.get_or_none(
            DevilFruit.owner == user, DevilFruit.status == DevilFruitStatus.EATEN
        )

    def get_average_price(self) -> int:
        """
        Get the average price of the sold fruits of the same category
        :return: The average price
        """

        from src.model.DevilFruitTrade import DevilFruitTrade

        return DevilFruitTrade.get_average_price(self.category)

    def get_category(self) -> DevilFruitCategory:
        """
        Get the category of the devil fruit
        :return: The category
        """
        return DevilFruitCategory(self.category)

    def get_status(self) -> DevilFruitStatus:
        """
        Get the status of the devil fruit
        :return: The status
        """
        return DevilFruitStatus(self.status)


DevilFruit.create_table()
