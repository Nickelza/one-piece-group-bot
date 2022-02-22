from telegram import Update
from telegram.ext import CallbackContext

import datetime
from peewee import MySQLDatabase

from resources.Database import Database
from src.model.User import User


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


def update_group_user(tg_user_id: str, tg_first_name: str) -> None:
    """
    Creates a new user or updates an existing user
    :param tg_user_id: Telegram user id
    :type tg_user_id: str
    :param tg_first_name: Telegram first name
    :type tg_first_name: str
    :return: None
    :rtype: None
    """

    User \
        .insert(tg_user_id=tg_user_id,
                tg_first_name=tg_first_name,
                message_count=User.message_count + 1,
                last_message_date=datetime.datetime.now()) \
        .on_conflict(
            update={User.tg_first_name: tg_first_name,
                    User.message_count: User.message_count + 1,
                    User.last_message_date: datetime.datetime.now()}) \
        .execute()


def manage(update: Update, context: CallbackContext) -> None:
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
    if update.effective_user is not None:
        update_group_user(update.effective_user.id, update.effective_user.first_name)

    end(db)
