from peewee import *

from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat
from src.model.Prediction import Prediction


class PredictionGroupChatMessage(BaseModel):
    """
    Prediction group chat message class
    """

    id = PrimaryKeyField()
    prediction = ForeignKeyField(Prediction, backref='prediction_group_chat_messages', on_delete='CASCADE',
                                 on_update='CASCADE')
    group_chat = ForeignKeyField(GroupChat, backref='prediction_group_chat_messages', on_delete='CASCADE',
                                 on_update='CASCADE')
    message_id = BigIntegerField()

    class Meta:
        db_table = 'prediction_group_chat_message'


PredictionGroupChatMessage.create_table()
