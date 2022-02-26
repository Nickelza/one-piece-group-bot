import datetime

from peewee import *

from src.model.BaseModel import BaseModel


class RedditGroupPost(BaseModel):
    """
    RedditGroupPost class
    """
    id = PrimaryKeyField()
    short_link = CharField(max_length=99, unique=True)
    datetime = DateTimeField(null=False, default=datetime.datetime.now)
    message_id = BigIntegerField(null=False)

    class Meta:
        db_table = 'reddit_group_post'


RedditGroupPost.create_table()
