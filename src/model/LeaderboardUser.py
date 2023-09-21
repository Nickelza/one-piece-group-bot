from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Leaderboard import Leaderboard
from src.model.User import User


class LeaderboardUser(BaseModel):
    """
    Leaderboard class
    """
    leaderboard = ForeignKeyField(Leaderboard, backref='leaderboard_users', on_delete='CASCADE', on_update='CASCADE')
    user = ForeignKeyField(User, backref='leaderboard_users', on_delete='CASCADE', on_update='CASCADE')
    position = IntegerField()
    bounty = BigIntegerField()
    rank_index = SmallIntegerField()

    class Meta:
        db_table = 'leaderboard_user'

    @staticmethod
    def get_appearances_as_rank(user: User, rank_index: int):
        """
        Get the appearances of a user as a rank
        param user: The user
        param rank: The rank
        return: The appearances
        """

        return (LeaderboardUser().select()
                .where((LeaderboardUser.user == user) & (LeaderboardUser.rank_index == rank_index)).count())

    @staticmethod
    def get_max_rank_attained(user: User) -> 'LeaderboardUser':
        """
        Get the highest rank attained by a user
        param user: The user
        return: The highest rank attained
        """

        return (LeaderboardUser().select()
                .where(LeaderboardUser.user == user)
                .order_by(LeaderboardUser.rank_index.asc()).first())

    @staticmethod
    def get_max_bounty_attained(user: User) -> 'LeaderboardUser':
        """
        Get the highest bounty attained by a user
        param user: The user
        return: The highest bounty attained
        """

        return (LeaderboardUser().select()
                .where(LeaderboardUser.user == user)
                .order_by(LeaderboardUser.bounty.desc()).first())


LeaderboardUser.create_table()
