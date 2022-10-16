import resources.phrases as phrases
from src.model.error.Error import Error
from src.model.error.ErrorSource import ErrorSource


class CommonChatError(Error):
    source = ErrorSource.COMMON

    SAVED_MEDIA_NOT_FOUND = Error(1, phrases.SAVED_MEDIA_NOT_FOUND, source)


class CommonChatException(Exception):
    def __init__(self, error: CommonChatError):
        self.message = error.build()
        super().__init__(self.message)
