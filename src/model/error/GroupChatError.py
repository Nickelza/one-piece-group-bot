import resources.phrases as phrases
from src.model.error.Error import Error
from src.model.error.ErrorSource import ErrorSource


class GroupChatError(Error):
    source = ErrorSource.GROUP_CHAT

    USER_NOT_IN_DB = Error(1, phrases.USER_NOT_FOUND, source, True)
    UNRECOGNIZED_SCREEN = Error(2, phrases.UNRECOGNIZED_SCREEN, source, True)
    SAVED_MEDIA_NOT_FOUND = Error(3, phrases.SAVED_MEDIA_NOT_FOUND, source, True)
    DOC_Q_GAME_NOT_FOUND = Error(4, phrases.DOC_Q_GAME_NOT_FOUND, source, True)
    KEYBOARD_NOT_FOUND = Error(5, phrases.KEYBOARD_NOT_FOUND, source, True)
    INVALID_CHANGE_REGION_REQUEST = Error(6, phrases.LOCATION_INVALID_CHANGE_REGION_REQUEST, source, True)
    FIGHT_NOT_FOUND = Error(7, phrases.FIGHT_NOT_FOUND, source, True)
    FIGHT_OPPONENT_NOT_FOUND = Error(8, phrases.FIGHT_OPPONENT_NOT_FOUND, source, True)
    GAME_NOT_FOUND = Error(9, phrases.GAME_NOT_FOUND, source, True)
    INVALID_GAME = Error(10, phrases.GAME_INVALID, source, True)
    PREDICTION_NOT_FOUND = Error(11, phrases.PREDICTION_NOT_FOUND, source, True)
