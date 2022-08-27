import json

from telegram import Update
from telegram.ext import CallbackContext

from src.chat.tgrest.screens.screen_prediction import manage as manage_screen_prediction
from src.chat.tgrest.screens.screen_send_private_message import manage as manage_screen_send_private_message
from src.model.tgrest.TgRest import TgRest, TgRestException
from src.model.tgrest.TgRestObjectType import TgRestObjectType
from src.model.tgrest.TgRestPrediction import TgRestPrediction
from src.model.tgrest.TgRestPrivateMessage import TgRestPrivateMessage
from src.service.message_service import full_message_send, escape_valid_markdown_chars


def manage(update: Update, context: CallbackContext) -> None:
    """
    Main function for the group chat manager
    :param update: Telegram update
    :param context: Telegram context
    :return: None
    """

    try:
        # Try parsing object
        try:
            # If starts with "Error", ignore
            if update.effective_message.text.startswith("Error"):
                return

            tg_rest_dict = json.loads(update.effective_message.text)
            tg_rest = TgRest(**tg_rest_dict)
        except Exception as tgre:
            raise TgRestException(str(tgre))

        # If not intended recipient, ignore
        if int(tg_rest.bot_id) != int(update.effective_message.bot.id):
            return

        match tg_rest.object_type:
            case TgRestObjectType.PREDICTION:
                tg_rest_prediction = TgRestPrediction(**tg_rest_dict)
                manage_screen_prediction(context, tg_rest_prediction)

            case TgRestObjectType.PRIVATE_MESSAGE:
                tg_rest_private_message = TgRestPrivateMessage(**tg_rest_dict)
                manage_screen_send_private_message(context, tg_rest_private_message)

            case _:
                raise TgRestException("Unknown object type")
        full_message_send(context, "Request received", update=update, quote=True)
    except TgRestException as e:
        full_message_send(context, "Error: " + escape_valid_markdown_chars(e.message), update=update, quote=True)
        return
