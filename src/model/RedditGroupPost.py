import datetime

from src.model.BaseModel import BaseModel
from peewee import *


class RedditGroupPost(BaseModel):
    """
    RedditGroupPost class
    """
    id = PrimaryKeyField()
    short_link = CharField(max_length=99, unique=True)
    datetime = DateTimeField(null=False, default=datetime.datetime.now)
    message_id = BigIntegerField(null=False)


RedditGroupPost.create_table()
