from telegram.error import Unauthorized
from telegram.ext import CallbackContext

from src.model.tgrest.TgRest import TgRestException
from src.model.tgrest.TgRestPrivateMessage import TgRestPrivateMessage
from src.service.message_service import full_message_send


def manage(context: CallbackContext, tg_rest_private_message: TgRestPrivateMessage):
    """
    Main function for the TG Rest private message manager
    :param context: Telegram context
    :param tg_rest_private_message: TG Rest Private Message
    """

    try:
        full_message_send(context, tg_rest_private_message.message, chat_id=tg_rest_private_message.tg_user_id)
    except Unauthorized:  # User blocked the bot in private chat
        pass
    except Exception as e:
        raise TgRestException(str(e))
