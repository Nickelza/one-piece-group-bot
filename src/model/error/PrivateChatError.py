import resources.phrases as phrases
from src.model.error.Error import Error
from src.model.error.ErrorSource import ErrorSource


class PrivateChatError(Error):
    source = ErrorSource.PRIVATE_CHAT

    USER_NOT_IN_DB = Error(1, phrases.USER_NOT_FOUND, source, True)
    UNRECOGNIZED_SCREEN = Error(2, phrases.UNRECOGNIZED_SCREEN, source, True)
    UNKNOWN_EXTRA_STEP = Error(3, phrases.UNKNOWN_EXTRA_STEP, source, True)
