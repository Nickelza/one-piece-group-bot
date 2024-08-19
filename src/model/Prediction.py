from peewee import *

from src.model.BaseModel import BaseModel
from src.model.User import User
from src.model.enums.PredictionStatus import PredictionStatus


class Prediction(BaseModel):
    """
    Prediction class
    """

    type = CharField(max_length=20, null=False)
    status = SmallIntegerField(default=PredictionStatus.NEW)
    question = CharField(max_length=999)
    send_date = DateTimeField(null=True)
    end_date = DateTimeField(null=True)
    cut_off_date = DateTimeField(null=True)
    refund_wager = BooleanField(default=False)
    max_refund_wager = BigIntegerField(null=True)
    allow_multiple_choices = BooleanField(default=True)
    can_withdraw_bet = BooleanField(default=True)
    result_set_date = DateTimeField(null=True)
    creator = ForeignKeyField(
        User, null=True, backref="predictions", on_delete="CASCADE", on_update="CASCADE"
    )
    is_public = BooleanField(default=False)

    options: list[str] = []  # For saving in context when creating a private prediction
    should_save: bool = True

    # Backref
    prediction_options = None

    class Meta:
        db_table = "prediction"

    def is_open(self) -> bool:
        """If the prediction is open for betting"""
        return PredictionStatus(self.status) is PredictionStatus.SENT

    def is_closed(self) -> bool:
        """If the prediction is closed for betting"""
        return PredictionStatus(self.status) is PredictionStatus.BETS_CLOSED

    def is_result_set(self) -> bool:
        """If the prediction has a result set"""
        return PredictionStatus(self.status) is PredictionStatus.RESULT_SET

    def is_new_or_sent(self) -> bool:
        """If the prediction is editable"""
        return PredictionStatus(self.status) in [PredictionStatus.NEW, PredictionStatus.SENT]

    def get_status(self) -> PredictionStatus:
        """Get the prediction status"""
        return PredictionStatus(self.status)


Prediction.create_table()
