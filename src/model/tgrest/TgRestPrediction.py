from enum import StrEnum

from src.model.tgrest.TgRest import TgRest
from src.model.tgrest.TgRestObjectType import TgRestObjectType


class TgRestPredictionAction(StrEnum):
    """
    Enum for the action of Telegram REST API request.
    """

    SEND = "send"
    CLOSE_BETS = "close_bets"
    SET_RESULTS = "set_results"
    REFRESH = "refresh"
    RESEND = "resend"


class TgRestPrediction(TgRest):
    """
    TgRestPrediction class is used to create a Telegram REST API request.
    """

    def __init__(
        self,
        bot_id: str,
        object_type: TgRestObjectType,
        action: TgRestPredictionAction,
        prediction_id: int,
    ):
        """
        Constructor
        :param action: The action
        :param prediction_id: The prediction id
        """
        super().__init__(bot_id, object_type)

        self.action: TgRestPredictionAction = action
        self.prediction_id: int = prediction_id
