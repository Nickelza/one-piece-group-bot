from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import constants as c
import resources.phrases as phrases
from src.model.Prediction import Prediction
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.model.enums.ListPage import ListPage
from src.model.enums.PredictionStatus import PredictionStatus
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.english_phrase_service import determine_article
from src.service.list_service import get_items_text_keyboard
from src.service.message_service import full_message_send, escape_valid_markdown_chars
from src.service.prediction_service import get_user_prediction_status_emoji, get_prediction_text, \
    get_user_prediction_status_text


class PredictionReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    ITEM_ID = 'a'


class PredictionListPage(ListPage):
    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.object: Prediction = Prediction()

    def set_object(self, object_id: int) -> None:
        self.object = Prediction.get(Prediction.id == object_id)

    def get_items(self, page) -> list[Prediction]:
        """Get predictions that are open or closed/result set but user bet on them"""

        return (self.object
                .select()
                .where((Prediction.status == PredictionStatus.SENT) |
                       (Prediction.status.in_([PredictionStatus.BETS_CLOSED, PredictionStatus.RESULT_SET]) &
                        (Prediction.id.in_(PredictionOptionUser.select(PredictionOptionUser.prediction)
                                           .where(PredictionOptionUser.user == self.user)
                                           ))))
                .order_by(Prediction.send_date.desc())
                .paginate(page, c.STANDARD_LIST_SIZE))

    def get_total_items_count(self) -> int:
        return (self.object
                .select()
                .where((Prediction.status == PredictionStatus.SENT) |
                       (Prediction.status.in_([PredictionStatus.BETS_CLOSED, PredictionStatus.RESULT_SET]) &
                        (Prediction.id.in_(PredictionOptionUser.select(PredictionOptionUser.prediction)
                                           .where(PredictionOptionUser.user == self.user)
                                           ))))
                .count())

    def get_item_text(self) -> str:
        return phrases.PREDICTION_ITEM_TEXT.format(get_user_prediction_status_emoji(self.object, self.user),
                                                   escape_valid_markdown_chars(self.object.question))

    def get_item_detail_text(self) -> str:
        return phrases.PREDICTION_ITEM_DETAIL_TEXT.format(
            get_prediction_text(self.object, add_bets_command=False, user=self.user),
            get_user_prediction_status_text(self.object, self.user, add_bets_command=False))


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the prediction list screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    prediction_list_page: PredictionListPage = PredictionListPage()
    prediction_list_page.user = user

    items_text, items_keyboard = get_items_text_keyboard(inbound_keyboard, prediction_list_page,
                                                         PredictionReservedKeys.ITEM_ID, Screen.PVT_PREDICTION_DETAIL)

    ot_text = phrases.LIST_OVERVIEW.format(determine_article(phrases.PREDICTION_ITEM_TEXT_FILL_IN),
                                           phrases.PREDICTION_ITEM_TEXT_FILL_IN, items_text)

    await full_message_send(context, ot_text, update=update, keyboard=items_keyboard,
                            inbound_keyboard=inbound_keyboard,
                            excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE])
