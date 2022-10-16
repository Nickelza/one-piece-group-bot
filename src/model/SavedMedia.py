from peewee import *

from src.model.BaseModel import BaseModel
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.error.CommonChatError import CommonChatError, CommonChatException


class SavedMedia(BaseModel):
    """
    SavedMedia class
    """
    id = PrimaryKeyField()
    name = CharField(unique=True)
    media_id = CharField()
    type = SmallIntegerField()

    class Meta:
        db_table = 'saved_media'

    @staticmethod
    def logical_get(name: SavedMediaName) -> 'SavedMedia':
        """
        Returns the SavedMedia by name, or raises an error if not found
        :param name: The name of the media
        :return: The SavedMedia
        """
        try:
            saved_media = SavedMedia.get(SavedMedia.name == name)
        except DoesNotExist:
            raise CommonChatException(CommonChatError.SAVED_MEDIA_NOT_FOUND)

        return saved_media


SavedMedia.create_table()
