from telegram import Update
from telegram.ext import CallbackContext

from resources import phrases
from src.model.Prediction import Prediction
from src.model.error.CustomException import PredictionException
from src.model.error.TgRestChatError import TgRestChatError
from src.model.tgrest.TgRest import TgRestException
from src.model.tgrest.TgRestPrediction import TgRestPrediction, TgRestPredictionAction
from src.service.prediction_service import send, close_bets, set_results, refresh


def manage(update: Update, context: CallbackContext, tg_rest_prediction: TgRestPrediction):
    """
    Main function for the TG Rest chat manage
    :param update: Telegram update
    :param context: Telegram context
    :param tg_rest_prediction: TG Rest prediction
    """

    # Get prediction
    prediction: Prediction = Prediction.get_or_none(id=tg_rest_prediction.prediction_id)

    if prediction is None:
        raise TgRestException(phrases.PREDICTION_NOT_FOUND)

    try:
        match tg_rest_prediction.action:
            case TgRestPredictionAction.SEND:
                send(update, context, prediction)

            case TgRestPredictionAction.CLOSE_BETS:
                close_bets(update, context, prediction)

            case TgRestPredictionAction.SET_RESULTS:
                set_results(update, context, prediction)

            case TgRestPredictionAction.REFRESH:
                refresh(update, context, prediction)

            case _:
                raise TgRestException(TgRestChatError.UNKNOWN_PREDICTION_ACTION.build())
    except PredictionException as e:
        raise TgRestException(e.message)
