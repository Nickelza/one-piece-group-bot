import resources.phrases as phrases
from src.model.error.Error import Error
from src.model.error.ErrorSource import ErrorSource


class GroupChatError(Error):
    source = ErrorSource.GROUP_CHAT

    USER_NOT_IN_DB = Error(1, phrases.USER_NOT_FOUND, source, True)
    UNRECOGNIZED_SCREEN = Error(2, phrases.UNRECOGNIZED_SCREEN, source, True)
    DOC_Q_MEDIA_NOT_FOUND = Error(3, phrases.DOC_Q_MEDIA_NOT_FOUND, source, True)
    DOC_Q_GAME_NOT_FOUND = Error(4, phrases.DOC_Q_GAME_NOT_FOUND, source, True)
    DOC_Q_KEYBOARD_NOT_FOUND = Error(5, phrases.KEYBOARD_NOT_FOUND, source, True)
