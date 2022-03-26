import datetime

from peewee import *

from src.model.BaseModel import BaseModel
from src.model.User import User


class UserLocationBountyPoster(BaseModel):
    """
    User location bounty poster model
    """
    user = ForeignKeyField(User, backref='user_location_bounty_poster_users', on_delete='CASCADE', on_update='CASCADE')
    location_level = SmallIntegerField()
    sent_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        db_table = 'user_location_bounty_poster'


UserLocationBountyPoster.create_table()
