from datetime import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat
from src.model.Prediction import Prediction


class PredictionGroupChatMessage(BaseModel):
    """
    Prediction group chat message class
    """

    prediction = ForeignKeyField(
        Prediction,
        backref="prediction_group_chat_messages",
        on_delete="CASCADE",
        on_update="CASCADE",
    )
    group_chat = ForeignKeyField(
        GroupChat,
        backref="prediction_group_chat_messages",
        on_delete="CASCADE",
        on_update="CASCADE",
    )
    message_id = BigIntegerField()
    date = DateTimeField(default=datetime.now)

    class Meta:
        db_table = "prediction_group_chat_message"


PredictionGroupChatMessage.create_table()
