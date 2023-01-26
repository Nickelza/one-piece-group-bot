from peewee import *

from src.model.BaseModel import BaseModel
from src.model.Topic import Topic


class TopicDisabledFeature(BaseModel):
    """
    Topic Disabled Feature class
    """
    id = PrimaryKeyField()
    topic = ForeignKeyField(Topic, backref='disabled_features', on_delete='CASCADE', on_update='CASCADE')
    feature = SmallIntegerField()

    class Meta:
        db_table = 'topic_disabled_feature'


TopicDisabledFeature.create_table()
