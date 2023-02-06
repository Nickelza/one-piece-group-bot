import os

import constants as c
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.SavedMediaType import SavedMediaType


class SavedMedia:
    """
    SavedMedia class
    """

    def __init__(self, media_type: SavedMediaType = None, media_id: str = None, name: SavedMediaName = None,
                 file_name: str = None):
        """
        Constructor
        :param media_type: Media type
        :param media_id: Media id
        :param name: Media name
        :param file_name: File name
        """
        self.type: SavedMediaType = media_type
        self.media_id: str = media_id
        self.name: SavedMediaName = name
        self.file_name: str = os.path.join(c.SAVED_MEDIA_DIR, file_name) if file_name else None

    @staticmethod
    def get_by_name(name: SavedMediaName) -> 'SavedMedia':
        """
        Get a SavedMedia by name
        :param name: Name of the SavedMedia
        :return: The SavedMedia
        """
        return SAVED_MEDIA_DICT[name]


SAVED_MEDIA_DICT = {}

CREW_INVITE = SavedMedia(
    media_type=SavedMediaType.PHOTO, name=SavedMediaName.CREW_INVITE, file_name='crew_invite.jpg')
SAVED_MEDIA_DICT[SavedMediaName.CREW_INVITE] = CREW_INVITE

CREW_JOIN = SavedMedia(
    media_type=SavedMediaType.PHOTO, name=SavedMediaName.CREW_JOIN, file_name='join_crew.jpg')
SAVED_MEDIA_DICT[SavedMediaName.CREW_JOIN] = CREW_JOIN

DOC_Q = SavedMedia(
    media_type=SavedMediaType.PHOTO, name=SavedMediaName.DOC_Q, file_name='docq.jpg')
SAVED_MEDIA_DICT[SavedMediaName.DOC_Q] = DOC_Q

FIGHT = SavedMedia(
    media_type=SavedMediaType.PHOTO, name=SavedMediaName.FIGHT, file_name='fight.jpg')
SAVED_MEDIA_DICT[SavedMediaName.FIGHT] = FIGHT

SILENCE = SavedMedia(
    media_type=SavedMediaType.PHOTO, name=SavedMediaName.SILENCE, file_name='silence.jpg')
SAVED_MEDIA_DICT[SavedMediaName.SILENCE] = SILENCE
