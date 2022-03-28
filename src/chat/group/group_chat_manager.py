import datetime

from peewee import MySQLDatabase
from telegram import Update, TelegramError
from telegram.ext import CallbackContext

import constants as c
import resources.Environment as Env
import resources.phrases as phrases
from resources.Database import Database
from src.chat.group.screens.screen_change_region import manage as manage_screen_change_region
from src.chat.group.screens.screen_doc_q_game import manage as manage_screen_doc_q_game
from src.chat.group.screens.screen_fight import manage as manage_screen_fight
from src.chat.group.screens.screen_show_bounty import manage as manage_screen_show_bounty
from src.chat.group.screens.screen_status import manage as manage_screen_show_status
from src.model.User import User
from src.model.enums.Command import Command
from src.model.enums.GroupScreen import GroupScreen, COMMAND_TO_GROUP_SCREEN
from src.model.error.GroupChatError import GroupChatError
from src.model.pojo.Keyboard import Keyboard, get_keyboard_from_callback_query
from src.service.bounty_service import add_bounty
from src.service.bounty_service import get_message_belly
from src.service.message_service import full_message_send, is_command


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


def update_group_user(update: Update, context: CallbackContext) -> User:
    """
    Creates a new user or updates an existing user
    :param update: Telegram update
    :param context: Telegram context
    :return: User object
    """

    # Insert or update user
    user = User.get_or_none(User.tg_user_id == update.effective_user.id)
    if user is None:
        user = User()
        user.tg_user_id = update.effective_user.id

    user.tg_first_name = update.effective_user.first_name
    user.tg_last_name = update.effective_user.last_name
    user = add_bounty(context, user, get_message_belly(update, user), update)
    user.last_message_date = datetime.datetime.now()
    user.save()

    return user


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
    screen = GroupScreen.UNKNOWN

    keyboard = None
    if update.callback_query is not None:
        keyboard = get_keyboard_from_callback_query(update.callback_query)

    # Insert or update user, with message count
    try:
        # Ignore self bot messages or from linked channel
        if update.effective_user.is_bot or update.message.sender_chat.id == Env.OPD_CHANNEL_ID.get_int():
            return
    except AttributeError:
        pass

    # Text message
    command = Command.ND
    if update.message is not None and update.message.text is not None and is_command(update.message.text):
        # Remove command prefix
        command_message = update.message.text[1:].lower()
        try:
            command: Command = Command(command_message)
            screen = COMMAND_TO_GROUP_SCREEN.get(command)
        except ValueError:
            pass

    # Screen still unknown, get from callback query
    if screen == GroupScreen.UNKNOWN:
        if keyboard is not None:
            screen = keyboard.screen

    user = update_group_user(update, context)

    # Validate keyboard interaction
    if keyboard is not None and 'u' in keyboard.info:
        if user.tg_user_id not in str(keyboard.info['u']).split(c.KEYBOARD_USER_SPLIT_CHAR):  # Unauthorized
            full_message_send(context, phrases.KEYBOARD_USE_UNAUTHORIZED, update, answer_callback=True, show_alert=True)
            return

        # Delete request, best effort
        if 'del' in keyboard.info:
            try:
                update.effective_message.delete()
            except TelegramError:
                pass
            return

    dispatch_screens(update, context, user, screen, keyboard, command=command)

    # End
    end(db)


def dispatch_screens(update: Update, context: CallbackContext, user: User, screen: GroupScreen, keyboard: Keyboard,
                     command: Command = None) -> None:
    match screen:
        case GroupScreen.USER_STATUS:  # User status
            manage_screen_show_status(update, context)

        case GroupScreen.DOC_Q_GAME:  # Doc Q Game
            manage_screen_doc_q_game(update, context, user, keyboard)

        case GroupScreen.SHOW_BOUNTY:  # Show bounty
            manage_screen_show_bounty(update, context)

        case GroupScreen.CHANGE_REGION:  # Change region
            manage_screen_change_region(update, context, user, keyboard, command)

        case GroupScreen.FIGHT:  # Fight
            manage_screen_fight(update, context, user, keyboard, command)

        case _:  # Unknown screen
            if update.callback_query is not None:
                full_message_send(context, GroupChatError.UNRECOGNIZED_SCREEN.build(), update, new_message=True)
