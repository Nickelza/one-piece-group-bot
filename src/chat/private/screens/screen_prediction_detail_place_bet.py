from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.User import User
from src.model.enums.ListPage import ListPage
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.list_service import get_items_text_keyboard
from src.service.message_service import full_message_send, escape_valid_markdown_chars


class PredictionPlaceBetReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    PREDICTION_ID = "a"
    PREDICTION_OPTION_ID = "b"


class PredictionPlaceBetListPage(ListPage):
    def __init__(self, prediction: Prediction):
        """
        Constructor
        """

        super().__init__()

        self.object: PredictionOption = PredictionOption()
        self.prediction: Prediction = prediction

    def set_object(self, object_id: int) -> None:
        self.object = PredictionOption.get(PredictionOption.id == object_id)

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[PredictionOption]:
        """Get prediction options for the prediction"""

        return (
            self.object.select()
            .where(PredictionOption.prediction == self.prediction)
            .order_by(PredictionOption.number)
            .paginate(page, limit)
        )

    def get_total_items_count(self) -> int:
        return self.object.select().where(PredictionOption.prediction == self.prediction).count()

    def get_item_text(self) -> str:
        return phrases.PREDICTION_PLACE_BET_TEXT.format(
            escape_valid_markdown_chars(self.object.option)
        )

    def get_item_detail_text(self) -> str:
        """Managed by send amount screen"""


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the prediction detail screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    prediction: Prediction = Prediction.get(
        Prediction.id == inbound_keyboard.get(PredictionPlaceBetReservedKeys.PREDICTION_ID)
    )
    prediction_place_bet_list_page: PredictionPlaceBetListPage = PredictionPlaceBetListPage(
        prediction
    )
    prediction_place_bet_list_page.user = user

    ot_text, items_keyboard = get_items_text_keyboard(
        inbound_keyboard,
        prediction_place_bet_list_page,
        PredictionPlaceBetReservedKeys.PREDICTION_OPTION_ID,
        Screen.PVT_PREDICTION_DETAIL_PLACE_BET_SEND_AMOUNT,
        text_overview=phrases.PREDICTION_PLACE_BET_LIST_OVERVIEW,
    )

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=items_keyboard,
        inbound_keyboard=inbound_keyboard,
        excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE],
    )
