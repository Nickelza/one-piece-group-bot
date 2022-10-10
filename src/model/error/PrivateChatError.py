import resources.phrases as phrases
from src.model.error.Error import Error
from src.model.error.ErrorSource import ErrorSource


class PrivateChatError(Error):
    source = ErrorSource.PRIVATE_CHAT

    USER_NOT_IN_DB = Error(1, phrases.USER_NOT_FOUND, source)
    UNRECOGNIZED_SCREEN = Error(2, phrases.UNRECOGNIZED_SCREEN, source)
    UNKNOWN_EXTRA_STEP = Error(3, phrases.UNKNOWN_EXTRA_STEP, source)
    PRIVATE_STEP_NOT_SET = Error(4, phrases.PRIVATE_STEP_NOT_SET, source)


class PrivateChatException(Exception):
    def __init__(self, error: PrivateChatError):
        self.message = error.build()
        super().__init__(self.message)
