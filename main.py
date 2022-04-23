import logging
import sys
import time

import pytz
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, Defaults, \
    CallbackQueryHandler

import constants as c
import resources.Environment as Env
from src.chat.manage_message import manage as manage_message, manage_callback as manage_callback_message
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
    full_message_send(context, str(update.effective_chat.id), update)


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

    if Env.DB_LOG_QUERIES.get_bool():
        # Set Peewee logger
        logger = logging.getLogger('peewee')
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO, stream=sys.stdout)

    """Instantiate a Defaults object"""
    defaults = Defaults(parse_mode=c.TG_DEFAULT_PARSE_MODE, tzinfo=pytz.timezone(Env.TZ.get()))

    updater = Updater(Env.BOT_TOKEN.get(), use_context=True, defaults=defaults)
    dispatcher = updater.dispatcher

    # Add handlers
    # Chat id handler
    chat_id_handler = CommandHandler('chatid', chat_id)
    dispatcher.add_handler(chat_id_handler)

    # Regular message handler
    message_handler = MessageHandler(Filters.all, manage_message)
    dispatcher.add_handler(message_handler)

    # Callback query handler
    callback_handler = CallbackQueryHandler(manage_callback_message)
    dispatcher.add_handler(callback_handler)

    updater.start_polling(drop_pending_updates=Env.BOT_DROP_PENDING_UPDATES.get_bool())

    # Activate timers
    set_timers(dispatcher)

    updater.idle()


if __name__ == '__main__':
    main()
