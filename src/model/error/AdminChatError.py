import resources.phrases as phrases
from src.model.error.Error import Error
from src.model.error.ErrorSource import ErrorSource


class AdminChatError(Error):
    source = ErrorSource.ADMIN_CHAT

    USER_NOT_IN_DB = Error(1, phrases.USER_NOT_FOUND, source, True)
    UNRECOGNIZED_SCREEN = Error(2, phrases.UNRECOGNIZED_SCREEN, source, True)
