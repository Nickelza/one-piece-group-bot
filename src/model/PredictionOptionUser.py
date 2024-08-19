from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Prediction import Prediction
from src.model.PredictionGroupChatMessage import PredictionGroupChatMessage
from src.model.PredictionOption import PredictionOption
from src.model.User import User


class PredictionOptionUser(BaseModel):
    """
    Prediction option user class
    """

    prediction = ForeignKeyField(
        Prediction, backref="prediction_options_users", on_delete="RESTRICT", on_update="RESTRICT"
    )
    prediction_option = ForeignKeyField(
        PredictionOption,
        backref="prediction_options_users",
        on_delete="RESTRICT",
        on_update="RESTRICT",
    )
    user = ForeignKeyField(
        User, backref="prediction_options_users", on_delete="CASCADE", on_update="CASCADE"
    )
    wager = BigIntegerField()
    max_refund_wager_boost = IntegerField(default=0)
    prediction_group_chat_message = ForeignKeyField(
        PredictionGroupChatMessage,
        null=True,
        backref="prediction_options_users",
        on_delete="RESTRICT",
        on_update="RESTRICT",
    )

    class Meta:
        db_table = "prediction_option_user"


PredictionOptionUser.create_table()
