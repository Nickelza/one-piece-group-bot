from peewee import *

from src.model.BaseModel import BaseModel


class RedditGroupPost(BaseModel):
    """
    RedditGroupPost class
    """

    short_link = CharField(max_length=99, unique=True)
    message_id = BigIntegerField()

    class Meta:
        db_table = "reddit_group_post"


RedditGroupPost.create_table()
