import resources.phrases as phrases
from src.model.error.Error import Error
from src.model.error.ErrorSource import ErrorSource


class AdminChatError(Error):
    source = ErrorSource.ADMIN_CHAT

    UNRECOGNIZED_SCREEN = Error(1, phrases.UNRECOGNIZED_SCREEN, source)


class AdminChatException(Exception):
    def __init__(self, error: AdminChatError):
        self.message = error.build()
        super().__init__(self.message)
