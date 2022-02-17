from src.model.BaseModel import BaseModel
from peewee import *


class User(BaseModel):
    """
    User class
    """
    id = PrimaryKeyField()
    tg_user_id = CharField(max_length=99, unique=True)
    tg_username = CharField(max_length=99)
    tg_first_name = CharField(max_length=99)
    message_count = IntegerField(default=0)
    last_message_date = DateTimeField(null=True)


User.create_table()
