from telegram.error import Forbidden
from telegram.ext import ContextTypes

from src.model.tgrest.TgRest import TgRestException
from src.model.tgrest.TgRestPrivateMessage import TgRestPrivateMessage
from src.service.message_service import full_message_send


async def manage(
    context: ContextTypes.DEFAULT_TYPE, tg_rest_private_message: TgRestPrivateMessage
):
    """
    Main function for the TG Rest private message manager
    :param context: Telegram context
    :param tg_rest_private_message: TG Rest Private Message
    """

    try:
        await full_message_send(
            context, tg_rest_private_message.message, chat_id=tg_rest_private_message.tg_user_id
        )
    except Forbidden:  # User blocked the bot in private chat
        pass
    except Exception as e:
        raise TgRestException(str(e))
