import logging
import time

import pytz
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, Defaults, \
    CallbackQueryHandler

import constants as c
import resources.Environment as Env
from src.chat.admin.admin_chat_manager import manage as manage_admin_chat
from src.chat.group.group_chat_manager import manage as manage_group_chat
from src.chat.manage_callback import manage as manage_callback
from src.chat.private.private_chat_manager import manage as manage_private_chat
from src.service.message_service import full_message_send
from src.service.timer_service import set_timers


def chat_id(update: Update, context: CallbackContext) -> None:
    """
    Send chat id of current chat
    :param update: Telegram update
    :type update: Update
    :param context: Telegram context
    :type context: CallbackContext
    :return: None
    :rtype: None
    """
    full_message_send(context, update.effective_chat.id, update)


def main() -> None:
    """
    Main function. Starts the bot
    :return: None
    :rtype: None
    """
    # Set timezone: Only on linux
    try:
        time.tzset()
    except AttributeError:
        pass

    # Set Peewee logger
    # logger = logging.getLogger('peewee')
    # logger.addHandler(logging.StreamHandler())
    # logger.setLevel(logging.DEBUG)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    """Instantiate a Defaults object"""
    defaults = Defaults(parse_mode=c.TG_DEFAULT_PARSE_MODE, tzinfo=pytz.timezone(Env.TZ.get()))

    updater = Updater(Env.TOKEN.get(), use_context=True, defaults=defaults)
    dispatcher = updater.dispatcher

    # Add handlers

    # Chat id handler
    chat_id_handler = CommandHandler('chatid', chat_id)
    dispatcher.add_handler(chat_id_handler)

    # Admin chat message handler
    admin_group_message_handler = MessageHandler(Filters.chat(Env.ADMIN_GROUP_ID.get()),
                                                 manage_admin_chat)
    dispatcher.add_handler(admin_group_message_handler)

    # Private chat
    start_handler = MessageHandler(Filters.chat_type.private, manage_private_chat)
    dispatcher.add_handler(start_handler)

    # Group message handler
    group_message_handler = MessageHandler(Filters.chat(Env.OPD_GROUP_ID.get()), manage_group_chat)
    dispatcher.add_handler(group_message_handler)

    # Callback query handler
    callback_handler = CallbackQueryHandler(manage_callback)
    dispatcher.add_handler(callback_handler)

    updater.start_polling(drop_pending_updates=True)

    # Activate timers
    set_timers(dispatcher)

    updater.idle()


if __name__ == '__main__':
    main()
