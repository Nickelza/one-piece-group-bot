from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.Prediction import Prediction
from src.model.enums.PredictionStatus import PredictionStatus
from src.model.error.CustomException import PredictionException


def send(update: Update, context: CallbackContext, prediction: Prediction) -> None:
    """
    Send prediction
    :param update: Telegram update
    :param context: Telegram context
    :param prediction: Prediction
    """
    if PredictionStatus(prediction.status) is not PredictionStatus.NEW:
        raise PredictionException(phrases.PREDICTION_NOT_IN_NEW_STATUS)


def close_bets(update: Update, context: CallbackContext, prediction: Prediction) -> None:
    """
    Close bets
    :param update: Telegram update
    :param context: Telegram context
    :param prediction: Prediction
    """
    if PredictionStatus(prediction.status) is not PredictionStatus.SENT:
        raise PredictionException(phrases.PREDICTION_NOT_IN_SENT_STATUS)


def set_results(update: Update, context: CallbackContext, prediction: Prediction) -> None:
    """
    Set results
    :param update: Telegram update
    :param context: Telegram context
    :param prediction: Prediction
    """
    if PredictionStatus(prediction.status) is not PredictionStatus.BETS_CLOSED:
        raise PredictionException(phrases.PREDICTION_NOT_IN_BETS_CLOSED_STATUS)


def refresh(update: Update, context: CallbackContext, prediction: Prediction) -> None:
    """
    Refresh prediction
    :param update: Telegram update
    :param context: Telegram context
    :param prediction: Prediction
    """
    if PredictionStatus(prediction.status) is not PredictionStatus.NEW:
        raise PredictionException(phrases.PREDICTION_NOT_IN_NEW_STATUS)
