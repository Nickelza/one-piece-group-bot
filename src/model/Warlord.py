import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.User import User


class Warlord(BaseModel):
    """
    Warlord class
    """

    user = ForeignKeyField(User, backref="warlords", on_delete="CASCADE", on_update="CASCADE")
    epithet = CharField(max_length=99, null=True)
    reason = CharField(max_length=999, null=True)
    end_date = DateTimeField()
    original_end_date = DateTimeField()  # In case it was ended early
    revoke_reason = CharField(max_length=999, null=True)

    class Meta:
        db_table = "warlord"

    @staticmethod
    def get_active() -> list["Warlord"]:
        """
        Get active warlords
        :return: Active warlords
        """

        return Warlord.select().where(Warlord.end_date > datetime.datetime.now())

    @staticmethod
    def get_active_order_by_bounty() -> list["Warlord"]:
        """
        Get active warlords
        :return: Active warlords
        """

        return (
            Warlord.select()
            .join(User)
            .where(Warlord.end_date > datetime.datetime.now())
            .order_by(User.bounty.desc())
        )

    @staticmethod
    def get_active_user_ids() -> list[int]:
        """
        Get active warlords
        :return: Active warlords
        """

        return [warlord.user.id for warlord in Warlord.get_active()]

    @staticmethod
    def get_latest_active_by_user(user: User) -> "Warlord":
        """
        Get the latest active warlord by user
        :param user: The user
        :return: The warlord
        """

        return (
            Warlord.select()
            .where((Warlord.user == user) & (Warlord.end_date > datetime.datetime.now()))
            .order_by(Warlord.end_date.desc())
            .first()
        )


Warlord.create_table()
