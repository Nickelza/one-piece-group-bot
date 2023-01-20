from peewee import *

from src.model.BaseModel import BaseModel
from src.model.enums.PredictionStatus import PredictionStatus


class Prediction(BaseModel):
    """
    Prediction class
    """
    id = PrimaryKeyField()
    type = CharField(max_length=20, null=False)
    status = SmallIntegerField(default=PredictionStatus.NEW)
    question = CharField(max_length=999, unique=True)
    send_date = DateTimeField(null=True)
    end_date = DateTimeField(null=True)
    cut_off_date = DateTimeField(null=True)
    refund_wager = BooleanField()
    max_refund_wager = IntegerField(null=True)
    allow_multiple_choices = BooleanField()
    can_withdraw_bet = BooleanField()
    message_id = IntegerField(null=True)
    result_set_date = DateTimeField(null=True)

    class Meta:
        db_table = 'prediction'

    def is_open(self) -> bool:
        """If the prediction is open for betting"""
        return PredictionStatus(self.status) is PredictionStatus.SENT

    def is_closed(self) -> bool:
        """If the prediction is closed for betting"""
        return PredictionStatus(self.status) is PredictionStatus.BETS_CLOSED

    def is_result_set(self) -> bool:
        """If the prediction has a result set"""
        return PredictionStatus(self.status) is PredictionStatus.RESULT_SET


Prediction.create_table()
