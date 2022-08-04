from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Prediction import Prediction


class PredictionOption(BaseModel):
    """
    User class
    """
    id = PrimaryKeyField()
    prediction = ForeignKeyField(Prediction, backref='prediction_options', on_delete='CASCADE', on_update='CASCADE')
    number = IntegerField()
    option = CharField(max_length=999)
    is_correct = BooleanField(default=False)

    class Meta:
        db_table = 'prediction_option'


PredictionOption.create_table()
