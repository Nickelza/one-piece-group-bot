from peewee import *

from src.model.BaseModel import BaseModel
from src.model.enums.PredictionStatus import PredictionStatus


class Prediction(BaseModel):
    """
    Prediction class
    """
    id = PrimaryKeyField()
    type = CharField(max_length=20, null=False)
    status = SmallIntegerField(default=PredictionStatus.NEW.value)
    question = CharField(max_length=999, unique=True)
    send_date = DateTimeField(null=True)
    end_date = DateTimeField(null=True)
    cut_off_date = DateTimeField(null=True)
    refund_wager = BooleanField()
    allow_multiple_choices = BooleanField()
    can_withdraw_bet = BooleanField()
    message_id = IntegerField(null=True)
    result_set_date = DateTimeField(null=True)

    class Meta:
        db_table = 'prediction'


Prediction.create_table()
