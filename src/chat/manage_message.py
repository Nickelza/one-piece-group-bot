import logging
from datetime import datetime

from peewee import MySQLDatabase, DoesNotExist
from telegram import Update, User as TelegramUser
from telegram.error import BadRequest
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
import src.model.enums.Command as Command
from resources.Database import Database
from src.chat.admin.admin_chat_manager import manage as manage_admin_chat
from src.chat.group.group_chat_manager import manage as manage_group_chat
from src.chat.private.private_chat_manager import manage as manage_private_chat
from src.chat.tgrest.tgrest_chat_manager import manage as manage_tgrest_chat
from src.model.Group import Group
from src.model.Topic import Topic
from src.model.User import User
from src.model.enums.MessageSource import MessageSource
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.error.AdminChatError import AdminChatException
from src.model.error.CommonChatError import CommonChatException
from src.model.error.CustomException import CommandValidationException, NavigationLimitReachedException
from src.model.error.GroupChatError import GroupChatException
from src.model.error.PrivateChatError import PrivateChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.group_service import feature_is_enabled, get_group_or_topic_text
from src.service.message_service import full_message_send, is_command, delete_message, get_message_source, \
    full_message_or_media_send_or_edit, message_is_reply
from src.service.user_service import user_is_boss, user_is_muted


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


async def manage_regular(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Manage a regular message
    :param update: The update
    :param context: The context
    :return: None
    """

    await manage(update, context, False)


async def manage_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Manage a callback message
    :param update: The update
    :param context: The context
    :return: None
    """

    await manage(update, context, True)
    await update.callback_query.answer()


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool) -> None:
    """
    Manage a regular message
    :param update: The update
    :param context: The context
    :param is_callback: True if the message is a callback
    :return: None
    """
    db = init()
    try:
        await manage_after_db(update, context, is_callback)
    except Exception as e:
        logging.error(update)
        logging.error(e, exc_info=True)
    finally:
        end(db)


async def manage_after_db(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool = False) -> None:
    """
    Manage a regular message after the database is initialized
    :param update: The update
    :param context: The context
    :param is_callback: True if the message is a callback
    :return: None
    """

    user = User()
    if update.effective_user is not None:
        user: User = get_user(update.effective_user)

        # Check if the user is authorized
        if Env.LIMIT_TO_AUTHORIZED_USERS.get_bool() and user.tg_user_id not in Env.AUTHORIZED_USERS.get_list():
            return

    # Recast necessary for match case to work, don't ask me why
    message_source: MessageSource = MessageSource(get_message_source(update))

    # Leave chat if not recognized
    if message_source is MessageSource.ND:
        logging.error(f'Unknown message source for {update.effective_chat.id}: Leaving chat')
        await update.effective_chat.leave()
        return

    # Group
    # noinspection PyTypeChecker
    group = topic = None
    if message_source is MessageSource.GROUP:
        group: Group = add_or_update_group(update)
        topic: Topic = add_or_update_topic(update, group)

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
            keyboard = Keyboard.get_from_callback_query(update.callback_query, message_source)

            if not keyboard.info:
                # No provided info, do nothing
                return

            if keyboard.screen is not None:
                try:
                    command = Command.get_by_screen(keyboard.screen)
                except ValueError:
                    # For commands without screen, example "delete"
                    command = Command.Command(None, keyboard.screen)

    target_user: User | None = None
    if keyboard is None:
        try:
            if message_is_reply(update):  # REPLY_TO_MESSAGE_BUG_FIX
                target_user: User = get_user(update.effective_message.reply_to_message.from_user)
        except AttributeError:
            pass

    if command != Command.ND or is_callback:
        if not await validate(update, context, command, user, keyboard, target_user, is_callback, message_source,
                              group, topic):
            return

    if command is not None:
        command.message_source = message_source

    try:
        match message_source:
            case MessageSource.PRIVATE:
                await manage_private_chat(update, context, command, user, keyboard)
            case MessageSource.GROUP:
                await manage_group_chat(update, context, command, user, keyboard, target_user, is_callback, group,
                                        topic)
            case MessageSource.ADMIN:
                await manage_admin_chat(update, context, command)
            case MessageSource.TG_REST:
                await manage_tgrest_chat(update, context)
            case _:
                raise ValueError('Invalid message source')
    except DoesNotExist:
        await full_message_send(context, phrases.ITEM_NOT_FOUND, update=update)
        raise ValueError('Item not found')
    except (PrivateChatException, GroupChatException, AdminChatException, CommonChatException) as ce:
        # Manages system errors
        try:
            await full_message_send(context, str(ce), update=update)
        except BadRequest:
            await full_message_or_media_send_or_edit(context, str(ce), update=update)
    except NavigationLimitReachedException:
        await full_message_send(context, phrases.NAVIGATION_LIMIT_REACHED, update=update, answer_callback=True,
                                show_alert=True)

    if user.should_update_model and user.tg_user_id is not None:
        user.save()


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE, command: Command.Command, user: User,
                   inbound_keyboard: Keyboard, target_user: User, is_callback: bool, message_source: MessageSource,
                   group: Group, topic: Topic) -> bool:
    """
    Validate the command
    :param update: Telegram update
    :param context: Telegram context
    :param command: The command
    :param user: The user
    :param inbound_keyboard: The keyboard
    :param target_user: The target user in case of a reply
    :param is_callback: True if the message is a callback
    :param message_source: The message source
    :param group: The group
    :param topic: The topic
    :return: True if the command is valid
    """

    # Validate keyboard interaction
    if is_callback and ReservedKeyboardKeys.AUTHORIZED_USER in inbound_keyboard.info:
        if int(user.id) not in inbound_keyboard.info[ReservedKeyboardKeys.AUTHORIZED_USER]:  # Unauthorized
            await full_message_send(context, phrases.KEYBOARD_USE_UNAUTHORIZED, update, answer_callback=True,
                                    show_alert=True)
            return False

        # Delete request, best effort
        if ReservedKeyboardKeys.DELETE in inbound_keyboard.info:
            await delete_message(update)
            return False

    # Is active
    try:
        if not command.active:
            if command.replaced_by is not None:
                raise CommandValidationException(
                    phrases.COMMAND_NOT_ACTIVE_WITH_REPLACEMENT_ERROR.format(command.get_replaced_by_formatted()))

            raise CommandValidationException(phrases.COMMAND_NOT_ACTIVE_ERROR)

        # Cannot be used while arrested
        if not command.allow_while_arrested:
            if user.is_arrested():
                raise CommandValidationException(phrases.COMMAND_WHILE_ARRESTED_ERROR)

        # Required location
        if command.required_location is not None:
            if user.location_level < command.required_location.level:
                if command.required_location.is_first_new_world():
                    raise CommandValidationException(phrases.COMMAND_FOR_NEW_WORLD_USERS_ERROR)

                raise CommandValidationException(
                    phrases.COMMAND_FOR_USERS_AFTER_LOCATION_ERROR.format(command.required_location.name))

        # Can only be used in reply to a message
        if command.only_in_reply:
            try:
                if message_is_reply(update):  # REPLY_TO_MESSAGE_BUG_FIX
                    if update.message.reply_to_message is None:
                        raise CommandValidationException(phrases.COMMAND_NOT_IN_REPLY_ERROR)
            except AttributeError:
                pass

        # Cannot be in reply to yourself
        if not command.allow_self_reply:
            try:
                if message_is_reply(update):  # REPLY_TO_MESSAGE_BUG_FIX
                    if update.message.reply_to_message.from_user.id == update.message.from_user.id:
                        raise CommandValidationException(phrases.COMMAND_IN_REPLY_TO_ERROR)
            except AttributeError:
                pass

        # Cannot be in reply to a Bot
        if not command.allow_reply_to_bot and not is_callback:
            try:
                if message_is_reply(update):  # REPLY_TO_MESSAGE_BUG_FIX
                    if update.effective_message.reply_to_message.from_user.is_bot:
                        raise CommandValidationException(phrases.COMMAND_IN_REPLY_TO_BOT_ERROR)
            except AttributeError:
                pass

        # Cannot be in reply to an arrested user
        if not command.allow_reply_to_arrested:
            try:
                if target_user.is_arrested():
                    raise CommandValidationException(phrases.COMMAND_IN_REPLY_TO_ARRESTED_ERROR)
            except AttributeError:
                pass

        # Can only be used by a Crew Captain
        if command.only_by_crew_captain:
            if not user.is_crew_captain():
                raise CommandValidationException(phrases.COMMAND_ONLY_BY_CREW_CAPTAIN_ERROR)

        # Can only be used by a boss
        if command.only_by_boss:
            if not await user_is_boss(user, update):
                raise CommandValidationException(phrases.COMMAND_ONLY_BY_BOSS_ERROR)

        # Can only be used by a chat admin
        if command.only_by_chat_admin:
            if not await user.is_chat_admin(update):
                raise CommandValidationException(phrases.COMMAND_ONLY_BY_CHAT_ADMIN_ERROR)

        if not is_callback:
            # Can only be used in reply to a message from a Crew Member
            if command.only_in_reply_to_crew_member:
                # AttributeError not managed because it's already managed by only_in_reply
                if not target_user.is_crew_member():
                    raise CommandValidationException(phrases.COMMAND_NOT_IN_REPLY_TO_CREW_MEMBER_ERROR)

        if command.feature is not None and message_source is MessageSource.GROUP:
            if not feature_is_enabled(group, topic, command.feature):
                raise CommandValidationException(phrases.COMMAND_FEATURE_DISABLED_ERROR.format(
                    get_group_or_topic_text(topic)
                ))

    except CommandValidationException as cve:
        if not command.answer_callback and await user_is_muted(user, update):
            await delete_message(update)
        else:
            if (command.answer_callback and is_callback) or command.send_message_if_error:
                await full_message_or_media_send_or_edit(context, str(cve), update=update, add_delete_button=True,
                                                         answer_callback=command.answer_callback,
                                                         show_alert=command.show_alert)
        return False

    return True


def get_user(effective_user: TelegramUser) -> User:
    """
    Create or update the user
    :param effective_user: The Telegram user
    :return: The user
    """

    # Insert or update user
    user = User.get_or_none(User.tg_user_id == effective_user.id)
    if user is None:
        user = User()
        user.tg_user_id = effective_user.id

    user.tg_first_name = effective_user.first_name
    user.tg_last_name = effective_user.last_name
    user.tg_username = effective_user.username
    user.last_message_date = datetime.now()

    user.save()

    return user


def add_or_update_group(update) -> Group:
    """
    Adds or updates a group
    :param update: Telegram update
    :return: Group object
    """
    group = Group.get_or_none(Group.tg_group_id == update.effective_chat.id)

    if group is None:
        group = Group()
        group.tg_group_id = update.effective_chat.id

    # If the group has been migrated, update the ID
    try:
        if update.message.migrate_to_chat_id is not None:
            group.tg_group_id = update.message.migrate_to_chat_id
    except AttributeError:
        pass

    group.tg_group_name = update.effective_chat.title
    group.tg_group_username = update.effective_chat.username
    group.last_message_date = datetime.now()
    group.save()

    return group


def add_or_update_topic(update, group: Group) -> Topic | None:
    """
    Adds or updates a topic
    :param update: Telegram update
    :param group: Group object
    :return: Topic object
    """
    if not update.effective_chat.is_forum or update.effective_message.message_thread_id is None:
        return None

    topic = Topic.get_or_none((Topic.group == group) &
                              (Topic.tg_topic_id == update.effective_message.message_thread_id))

    if topic is None:
        topic = Topic()
        topic.group = group
        topic.tg_topic_id = update.effective_message.message_thread_id

    topic.last_message_date = datetime.now()
    topic.save()

    return topic
