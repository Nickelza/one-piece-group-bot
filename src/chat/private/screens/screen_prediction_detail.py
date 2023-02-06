from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.private.screens.screen_prediction import PredictionListPage
from src.model.Prediction import Prediction
from src.model.User import User
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send
from src.service.prediction_service import user_has_bet_on_prediction


class PredictionDetailReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    PREDICTION_ID = 'a'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the prediction detail screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    prediction_list_page = PredictionListPage()

    prediction_list_page.user = user
    prediction_list_page.set_object(inbound_keyboard.get_int(PredictionDetailReservedKeys.PREDICTION_ID))

    prediction: Prediction = prediction_list_page.object
    inline_keyboard: list[list[Keyboard]] = []

    if prediction.is_open():
        if should_show_place_bet_button(prediction, user):
            button_info = {PredictionDetailReservedKeys.PREDICTION_ID: prediction.id}
            inline_keyboard.append([Keyboard(phrases.PVT_KEY_PREDICTION_DETAIL_PLACE_BET,
                                             screen=Screen.PVT_PREDICTION_DETAIL_PLACE_BET,
                                             info=button_info)])

        if should_show_remove_bet_button(prediction, user):
            button_info = {PredictionDetailReservedKeys.PREDICTION_ID: prediction.id}
            inline_keyboard.append([Keyboard(phrases.PVT_KEY_PREDICTION_DETAIL_REMOVE_BET,
                                             screen=Screen.PVT_PREDICTION_DETAIL_REMOVE_BET,
                                             info=button_info)])

    await full_message_send(context, prediction_list_page.get_item_detail_text(), update=update,
                            keyboard=inline_keyboard, inbound_keyboard=inbound_keyboard)


def should_show_place_bet_button(prediction: Prediction, user: User) -> bool:
    """
    Check if the user should see the place bet button.
    :param prediction: The prediction
    :param user: The user
    :return: True if the user should see the place bet button
    """

    # Accepts multiple bets
    if prediction.allow_multiple_choices:
        return True

    # Prediction does not accept multiple bets, show button if user has not bet
    return not user_has_bet_on_prediction(prediction, user)


def should_show_remove_bet_button(prediction: Prediction, user: User) -> bool:
    """
    Check if the user should see the remove bet button.
    :param prediction: The prediction
    :param user: The user
    :return: True if the user should see the remove bet button
    """

    # Does not accept bet withdrawal
    if not prediction.can_withdraw_bet:
        return False

    # Prediction accepts bet withdrawal, show button if user has bet
    return user_has_bet_on_prediction(prediction, user)
