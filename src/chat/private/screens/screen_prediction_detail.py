from strenum import StrEnum
from telegram import Update
from telegram.ext import ContextTypes

from src.chat.private.screens.screen_prediction import PredictionListPage
from src.model.User import User
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


class PredictionDetailReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    ITEM_ID = 'a'


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
    prediction_list_page.set_object(inbound_keyboard.get_int(PredictionDetailReservedKeys.ITEM_ID))

    await full_message_send(context, prediction_list_page.get_item_detail_text(), update=update,
                            inbound_keyboard=inbound_keyboard)
