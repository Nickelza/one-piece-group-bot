from telegram import Update
from telegram.ext import CallbackContext

from peewee import MySQLDatabase

from resources.Database import Database


def init() -> MySQLDatabase:
    """
    Initializes the group chat manager
    :return: Database connection
    :rtype: MySQLDatabase
    """
    db_obj = Database()
    db = db_obj.get_db()

    return db


def end(db: MySQLDatabase) -> None:
    """
    Ends the group chat manager
    :param db: Database connection
    :type db: MySQLDatabase
    :return: None
    :rtype: None
    """
    db.close()


def manage(update: Update, context) -> None:
    """
    Main function for the group chat manager
    :param update: Telegram update
    :type update: Update
    :param context: Telegram context
    :type context: CallbackContext
    :return: None
    :rtype: None
    """
    # Initialize
    db = init()

    # Insert or update user, with message count
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

    end(db)

