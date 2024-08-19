from datetime import datetime

from peewee import *

from resources.Database import Database

db_obj = Database()


class BaseModel(Model):
    """
    BaseModel class
    Used to manage Entities and Database connection
    """

    id: int | PrimaryKeyField = PrimaryKeyField()
    date = DateTimeField(default=datetime.now)

    class Meta:
        database = db_obj.get_db()
        only_save_dirty = True
