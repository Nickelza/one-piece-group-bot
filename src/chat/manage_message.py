import logging
from datetime import datetime

from peewee import MySQLDatabase
from telegram import Update
from telegram.ext import CallbackContext

import resources.Environment as Env
import resources.phrases as phrases
import src.model.enums.Command as Command
from resources.Database import Database
from src.chat.admin.admin_chat_manager import manage as manage_admin_chat
from src.chat.group.group_chat_manager import manage as manage_group_chat
from src.chat.private.private_chat_manager import manage as manage_private_chat
from src.chat.tgrest.tgrest_chat_manager import manage as manage_tgrest_chat
from src.model.User import User
from src.model.enums.MessageSource import MessageSource
from src.model.pojo.Keyboard import Keyboard, get_keyboard_from_callback_query
from src.service.message_service import full_message_send, is_command, delete_message, get_message_source


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


def manage_callback(update: Update, context: CallbackContext) -> None:
    """
    Manage a regular message
    :param update: The update
    :param context: The context
    :return: None
    """

    manage(update, context, True)
    update.callback_query.answer()


def manage(update: Update, context: CallbackContext, is_callback: bool = False) -> None:
    """
    Manage a regular message
    :param update: The update
    :param context: The context
    :param is_callback: True if the message is a callback
    :return: None
    """
    db = init()
    try:
        manage_after_db(update, context, is_callback)
    except Exception as e:
        logging.error(update)
        logging.error(e, exc_info=True)
    finally:
        end(db)


def manage_after_db(update: Update, context: CallbackContext, is_callback: bool = False) -> None:
    """
    Manage a regular message after the database is initialized
    :param update: The update
    :param context: The context
    :param is_callback: True if the message is a callback
    :return: None
    """

    user = User()
    if update.effective_user is not None:
        user: User = get_user(update)

        # Check if the user is authorized
        if Env.LIMIT_TO_AUTHORIZED_USERS.get_bool() and user.tg_user_id not in Env.AUTHORIZED_USERS.get_list():
            return

    # Recast necessary for match case to work, don't ask me why
    message_source: MessageSource = MessageSource(get_message_source(update))
    if message_source is MessageSource.ND:
        return

    command: Command.Command = Command.ND
    keyboard = None
    try:
        if is_command(update.message.text):
            if '/start ' in update.message.text:  # Start with parameter
                command_name = update.message.text.replace('/start ', '').lower()
            else:
                command_name = (update.message.text.split(' ')[0])[1:].lower()
                command_name = command_name.replace('@' + Env.BOT_USERNAME.get(), '')
            command = Command.get_by_name(command_name, message_source)
            try:
                command.parameters = update.message.text.split(' ')[1:]
            except IndexError:
                pass
    except (AttributeError, ValueError):
        if is_callback:
            keyboard = get_keyboard_from_callback_query(update.callback_query, message_source)

            if not keyboard.info:
                # No provided info, do nothing
                return

            if keyboard.screen is not None:
                try:
                    command = Command.get_by_screen(keyboard.screen)
                except ValueError:
                    command = Command.Command('', keyboard.screen)

    if command != Command.ND or is_callback:
        if not validate(update, context, command, user, keyboard):
            return

    if command is not None:
        command.message_source = message_source
    match message_source:
        case MessageSource.PRIVATE:
            manage_private_chat(update, context, command, user, keyboard)
        case MessageSource.GROUP:
            manage_group_chat(update, context, command, user, keyboard)
        case MessageSource.ADMIN:
            manage_admin_chat(update, context, command)
        case MessageSource.TG_REST:
            manage_tgrest_chat(update, context)
        case _:
            raise ValueError('Invalid message source')


def validate(update: Update, context: CallbackContext, command: Command.Command, user: User, keyboard: Keyboard
             ) -> bool:
    """
    Validate the command
    :param update: Telegram update
    :param context: Telegram context
    :param command: The command
    :param user: The user
    :param keyboard: The keyboard
    :return: True if the command is valid
    """

    # Validate keyboard interaction
    if keyboard is not None and 'u' in keyboard.info:
        if int(user.id) not in keyboard.info['u']:  # Unauthorized
            full_message_send(context, phrases.KEYBOARD_USE_UNAUTHORIZED, update, answer_callback=True, show_alert=True)
            return False

        # Delete request, best effort
        if 'del' in keyboard.info:
            delete_message(update)
            return False

    # Is active
    if not command.active:
        if command.replaced_by is not None:
            ot_text = phrases.COMMAND_NOT_ACTIVE_WITH_REPLACEMENT_ERROR.format(command.get_replaced_by_formatted())
        else:
            ot_text = phrases.COMMAND_NOT_ACTIVE_ERROR

        full_message_send(context, ot_text, update=update, add_delete_button=True)
        return False

    # Cannot be used while arrested
    if not command.allow_while_arrested:
        if user.is_arrested():
            full_message_send(context, phrases.COMMAND_WHILE_ARRESTED_ERROR, update=update, add_delete_button=True)
            return False

    # Required location
    if command.required_location is not None:
        if user.location_level < command.required_location.level:
            if command.required_location.is_first_new_world():
                full_message_send(context, phrases.COMMAND_FOR_NEW_WORLD_USERS_ERROR, update=update,
                                  add_delete_button=True)
            else:
                full_message_send(context,
                                  phrases.COMMAND_FOR_USERS_AFTER_LOCATION_ERROR.format(command.required_location.name),
                                  update=update, add_delete_button=True)
            return False

    # Can only be used in reply to a message
    if command.only_in_reply:
        try:
            if update.message.reply_to_message is None:
                full_message_send(context, phrases.COMMAND_NOT_IN_REPLY_ERROR, update=update, add_delete_button=True)
                return False
        except AttributeError:
            pass

    # Cannot be in reply to yourself
    if not command.allow_self_reply:
        try:
            if update.message.reply_to_message.from_user.id == update.message.from_user.id:
                full_message_send(context, phrases.COMMAND_IN_REPLY_TO_ERROR, update=update,
                                  add_delete_button=True)
                return False
        except AttributeError:
            pass

    # Cannot be in reply to a Bot
    if not command.allow_reply_to_bot:
        try:
            if update.effective_message.reply_to_message.from_user.is_bot:
                full_message_send(context, phrases.COMMAND_IN_REPLY_TO_BOT_ERROR, update=update, add_delete_button=True)
                return False
        except AttributeError:
            pass

    return True


def get_user(update: Update) -> User:
    """
    Create or update the user
    :param update: Telegram update
    :return: The user
    """

    # Insert or update user
    user = User.get_or_none(User.tg_user_id == update.effective_user.id)
    if user is None:
        user = User()
        user.tg_user_id = update.effective_user.id

    user.tg_first_name = update.effective_user.first_name
    user.tg_last_name = update.effective_user.last_name
    user.tg_username = update.effective_user.username
    user.last_message_date = datetime.now()
    user.save()

    return user
