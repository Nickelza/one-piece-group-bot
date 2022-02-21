import logging
import os
import time

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

import constants as const
from src.chat.group.group_chat_manager import manage as manage_group_chat
from src.chat.private.private_chat_manager import manage as manage_private_chat
from src.service.timers import set_timers


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
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.effective_chat.id)


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

    # logger = logging.getLogger('peewee')
    # logger.addHandler(logging.StreamHandler())
    # logger.setLevel(logging.DEBUG)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    updater = Updater(token=os.environ[const.ENV_TOKEN], use_context=True)
    dispatcher = updater.dispatcher

    # Add handlers

    # Chat id handler
    chat_id_handler = CommandHandler('chatid', chat_id)
    dispatcher.add_handler(chat_id_handler)

    # Private chat
    start_handler = MessageHandler(Filters.chat_type.private, manage_private_chat)
    dispatcher.add_handler(start_handler)

    # Group message handler
    group_message_handler = MessageHandler(Filters.chat(int(os.environ[const.ENV_OPD_GROUP_ID])), manage_group_chat)
    dispatcher.add_handler(group_message_handler)

    updater.start_polling()

    # Activate timers
    set_timers(dispatcher)

    updater.idle()


if __name__ == '__main__':
    main()
