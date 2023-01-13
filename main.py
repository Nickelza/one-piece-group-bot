import logging

import pytz
import sys
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, Defaults, CallbackQueryHandler, \
    ContextTypes

import constants as c
import resources.Environment as Env
from src.chat.manage_message import manage_regular as manage_regular_message, manage_callback as manage_callback_message
from src.service.message_service import full_message_send
from src.service.timer_service import set_timers


async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send chat id of current chat
    :param update: Telegram update
    :param context: Telegram context
    :return: None
    """
    await full_message_send(context, str(update.effective_chat.id), update)


def main() -> None:
    """
    Main function. Starts the bot
    :return: None
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

    defaults = Defaults(parse_mode=c.TG_DEFAULT_PARSE_MODE, tzinfo=pytz.timezone(Env.TZ.get()))

    application = (Application
                   .builder()
                   .token(Env.BOT_TOKEN.get())
                   .defaults(defaults)
                   .build())

    # Chat id handler
    application.add_handler(CommandHandler('chatid', chat_id))

    # Regular message handler
    application.add_handler(MessageHandler(filters.ALL, manage_regular_message))

    # Callback query handler
    application.add_handler(CallbackQueryHandler(manage_callback_message))

    # Activate timers
    set_timers(application)
    logging.getLogger('apscheduler.executors.default').propagate = False

    application.run_polling(drop_pending_updates=Env.BOT_DROP_PENDING_UPDATES.get_bool())


if __name__ == '__main__':
    main()
