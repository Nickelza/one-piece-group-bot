from telegram.ext import ContextTypes

from resources import phrases
from src.model.Prediction import Prediction
from src.model.error.CustomException import PredictionException
from src.model.error.TgRestChatError import TgRestChatError
from src.model.tgrest.TgRest import TgRestException
from src.model.tgrest.TgRestPrediction import TgRestPrediction, TgRestPredictionAction
from src.service.prediction_service import send, close_bets, set_results, refresh


async def manage(context: ContextTypes.DEFAULT_TYPE, tg_rest_prediction: TgRestPrediction):
    """
    Main function for the TG Rest chat manage
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
                await send(context, prediction)

            case TgRestPredictionAction.CLOSE_BETS:
                await close_bets(context, prediction)

            case TgRestPredictionAction.SET_RESULTS:
                await set_results(context, prediction)

            case TgRestPredictionAction.REFRESH:
                await refresh(context, prediction)

            case TgRestPredictionAction.RESEND:
                await send(context, prediction, is_resent=True)

            case _:
                raise TgRestException(TgRestChatError.UNKNOWN_PREDICTION_ACTION.build())
    except PredictionException as e:
        raise TgRestException(e.message)
