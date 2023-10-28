from peewee import *

from resources.Database import Database

db_obj = Database()


class BaseModel(Model):
    """
    BaseModel class
    Used to manage Entities and Database connection
    """

    class Meta:
        database = db_obj.get_db()
        only_save_dirty = True
