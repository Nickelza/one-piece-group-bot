from peewee import *

from src.model.BaseModel import BaseModel


class SavedMedia(BaseModel):
    """
    SavedMedia class
    """
    id = PrimaryKeyField()
    name = CharField()
    media_id = CharField()
    type = SmallIntegerField()

    class Meta:
        db_table = 'saved_media'


SavedMedia.create_table()
