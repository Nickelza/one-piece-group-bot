from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import constants as c
import resources.phrases as phrases
from src.chat.private.screens.screen_prediction_detail import manage as manage_prediction_detail
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.model.enums.ListPage import ListPage
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.list_service import get_items_text_keyboard
from src.service.message_service import full_message_send, escape_valid_markdown_chars


class PredictionRemoveBetReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    PREDICTION_ID = 'a'
    PREDICTION_OPTION_ID = 'b'


class PredictionRemoveBetListPage(ListPage):
    def __init__(self, prediction: Prediction):
        """
        Constructor
        """

        super().__init__()

        self.object: PredictionOption = PredictionOption()
        self.prediction: Prediction = prediction

    def set_object(self, object_id: int) -> None:
        self.object = PredictionOption.get(PredictionOption.id == object_id)

    def get_items(self, page) -> list[PredictionOption]:
        """Get prediction options that are bet on by the user"""

        return (self.object
                .select()
                .join(PredictionOptionUser)
                .where((PredictionOptionUser.prediction == self.prediction) & (PredictionOptionUser.user == self.user))
                .order_by(PredictionOption.number.asc())
                .paginate(page, c.STANDARD_LIST_SIZE))

    def get_total_items_count(self) -> int:
        return (self.object
                .select()
                .join(PredictionOptionUser)
                .where((PredictionOptionUser.prediction == self.prediction) & (PredictionOptionUser.user == self.user))
                .count())

    def get_item_text(self) -> str:
        return phrases.PREDICTION_REMOVE_BET_TEXT.format(escape_valid_markdown_chars(self.object.option))

    def get_item_detail_text(self) -> str:
        """No detail screen"""


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User,
                 called_from_remove_confirm: bool = False) -> None:
    """
    Manage the prediction detail screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :param called_from_remove_confirm: Whether this screen was called from the remove confirm screen. If so,
            the user won't be redirected to the prediction detail screen
    :return: None
    """

    from src.chat.private.screens.screen_prediction_detail_remove_bet_confirm import validate_and_delete

    prediction: Prediction = Prediction.get(
        Prediction.id == inbound_keyboard.get(PredictionRemoveBetReservedKeys.PREDICTION_ID))
    prediction_remove_bet_list_page: PredictionRemoveBetListPage = PredictionRemoveBetListPage(prediction)
    prediction_remove_bet_list_page.user = user

    if called_from_remove_confirm:
        # Set this screen as the current screen
        inbound_keyboard.screen = Screen.PVT_PREDICTION_DETAIL_REMOVE_BET
        inbound_keyboard.previous_screen_list.pop()

    items = prediction_remove_bet_list_page.get_items(1)
    if len(items) == 0 or (len(items) == 1 and not called_from_remove_confirm):
        if len(items) == 1:  # If only one item, directly remove bet
            prediction_option: PredictionOption = items[0]
            await validate_and_delete(context, prediction_option, update, user)

        inbound_keyboard.previous_screen_list.pop()
        await manage_prediction_detail(update, context, inbound_keyboard, user)
        return

    ot_text, items_keyboard = get_items_text_keyboard(
        inbound_keyboard, prediction_remove_bet_list_page, PredictionRemoveBetReservedKeys.PREDICTION_OPTION_ID,
        Screen.PVT_PREDICTION_DETAIL_REMOVE_BET_CONFIRM, text_overview=phrases.PREDICTION_REMOVE_BET_LIST_OVERVIEW)

    await full_message_send(context, ot_text, update=update, keyboard=items_keyboard, inbound_keyboard=inbound_keyboard,
                            excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE])
