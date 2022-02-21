from telegram import Update
from telegram.ext import CallbackContext

from peewee import MySQLDatabase

from resources.Database import Database
from src.chat.private.screens.screen_start import manage as manage_screen_start


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

    if update.message.text == '/start':
        manage_screen_start(update, context)

    end(db)

