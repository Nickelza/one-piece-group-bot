import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.GameStatus import GameStatus


class Fight(BaseModel):
    """
    Fight class
    """
    id = PrimaryKeyField()
    challenger = ForeignKeyField(User, backref='fight_challengers', on_delete='CASCADE', on_update='CASCADE')
    opponent = ForeignKeyField(User, backref='fight_opponents', on_delete='CASCADE', on_update='CASCADE')
    win_probability = FloatField()
    date = DateTimeField(default=datetime.datetime.now)
    status = SmallIntegerField(default=GameStatus.IN_PROGRESS)
    group_chat = ForeignKeyField(GroupChat, null=True, backref='fight_groups_chats', on_delete='RESTRICT',
                                 on_update='CASCADE')
    message_id = IntegerField(null=True)
    belly = IntegerField(null=True)

    class Meta:
        db_table = 'fight'

    def get_win_probability(self, user: User) -> float:
        """
        Get the win probability given a user

        :param user: The user
        :return: The win probability
        """

        if user.id == self.challenger.id:
            return float(str(self.win_probability))
        else:
            return 100 - self.win_probability


Fight.create_table()
