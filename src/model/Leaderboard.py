from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Group import Group


class Leaderboard(BaseModel):
    """
    Leaderboard class
    """

    id = PrimaryKeyField()
    year = SmallIntegerField()
    week = SmallIntegerField()
    group: Group = ForeignKeyField(Group, null=True, backref="leaderboards")
    global_message_id = IntegerField(null=True)

    class Meta:
        db_table = "leaderboard"

    @staticmethod
    def get_latest_n(n: int = 1, group: Group = None) -> list["Leaderboard"]:
        """
        Gets the latest n leaderboards
        :param n: The number of leaderboards to get
        :param group: The group to get the leaderboards for
        :return: The leaderboards
        """

        return list(
            Leaderboard.select()
            .where(Leaderboard.group == group)
            .order_by(Leaderboard.year.desc(), Leaderboard.week.desc())
            .limit(n)
            .execute()
        )


Leaderboard.create_table()
