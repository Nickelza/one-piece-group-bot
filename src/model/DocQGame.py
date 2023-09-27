import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.GameStatus import GameStatus


class DocQGame(BaseModel):
    """
    Doc Q Game class
    """
    id = PrimaryKeyField()
    user = ForeignKeyField(User, backref='doc_q_game_users', on_delete='CASCADE', on_update='CASCADE')
    date = DateTimeField(default=datetime.datetime.now)
    status = SmallIntegerField(default=GameStatus.IN_PROGRESS)
    correct_choices_index = CharField(max_length=99, null=True)
    group_chat = ForeignKeyField(GroupChat, null=True, backref='doc_q_game_groups_chats', on_delete='RESTRICT',
                                 on_update='CASCADE')
    message_id = IntegerField(null=True)
    belly = BigIntegerField(null=True)

    class Meta:
        db_table = 'doc_q_game'

    @staticmethod
    def get_total_win_or_loss(user: User, status: GameStatus) -> int:
        """
        Get the total amount of wins or losses a user has
        param user: The user
        param status: The status (won or lost)
        return: The total amount of wins or losses
        """

        return DocQGame().select().where((DocQGame.user == user) & (DocQGame.status == status)).count()

    @staticmethod
    def get_total_belly_won_or_lost(user: User, status: GameStatus) -> int:
        """
        Get the total amount of belly a user has won or lost
        param user: The user
        param status: The status (won or lost)
        return: The total amount of belly won or lost
        """

        return (DocQGame().select(fn.SUM(DocQGame.belly))
                .where((DocQGame.user == user) & (DocQGame.status == status))).scalar()

    @staticmethod
    def get_max_won_or_lost(user: User, status: GameStatus) -> 'DocQGame':
        """
        Get the DocQGame with the max amount of belly won or lost
        param user: The user
        param status: The status (won or lost)
        return: The max amount of belly won or lost
        """

        return (DocQGame().select()
                .where((DocQGame.user == user) & (DocQGame.status == status))
                .order_by(DocQGame.belly.desc())
                .first())


DocQGame.create_table()
