from peewee import MySQLDatabase
from telegram import Update
from telegram.ext import CallbackContext

from resources.Database import Database
from src.chat.admin.screens.screen_save_media import manage as manage_screen_save_media


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

    if update.message.text is not None and update.message.text.startswith('/savemedia'):
        manage_screen_save_media(update, context)

    end(db)
