import base64
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
from src.chat.group.group_chat_manager import manage as manage_group_chat
from src.chat.inline_query.inline_query_manager import manage as manage_inline_query
from src.chat.private.private_chat_manager import manage as manage_private_chat
from src.chat.tgrest.tgrest_chat_manager import manage as manage_tgrest_chat
from src.model.Group import Group
from src.model.GroupChat import GroupChat
from src.model.GroupUser import GroupUser
from src.model.User import User
from src.model.enums.ContextDataKey import ContextDataType, ContextDataKey
from src.model.enums.Feature import Feature
from src.model.enums.MessageSource import MessageSource
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CommonChatError import CommonChatException
from src.model.error.CustomException import CommandValidationException, NavigationLimitReachedException
from src.model.error.GroupChatError import GroupChatException
from src.model.error.PrivateChatError import PrivateChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.bot_service import get_context_data, set_context_data
from src.service.date_service import get_datetime_in_future_seconds
from src.service.group_service import feature_is_enabled, get_group_or_topic_text, is_main_group
from src.service.message_service import full_message_send, is_command, delete_message, get_message_source, \
    full_message_or_media_send_or_edit, message_is_reply, escape_valid_markdown_chars
from src.service.user_service import user_is_boss, user_is_muted


def init() -> MySQLDatabase:
    """
    Initializes the group chat chat manager
    :return: Database connection
    :rtype: MySQLDatabase
    """
    db_obj = Database()
    db = db_obj.get_db()

    return db


def end(db: MySQLDatabase) -> None:
    """
    Ends the group chat chat manager
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

    context.application.create_task(manage(update, context, False))


async def manage_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Manage a callback message
    :param update: The update
    :param context: The context
    :return: None
    """

    context.application.create_task(manage(update, context, True))


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

    if is_callback:
        try:
            await update.callback_query.answer()
        except BadRequest:
            pass


async def manage_after_db(update: Update, context: ContextTypes.DEFAULT_TYPE, is_callback: bool) -> None:
    """
    Manage a regular message after the database is initialized
    :param update: The update
    :param context: The context
    :param is_callback: True if the message is a callback
    :return: None
    """
    # Recast necessary for match case to work, don't ask me why
    message_source: MessageSource = MessageSource(get_message_source(update))

    user = User()
    if update.effective_user is not None:
        user: User = get_user(update.effective_user, should_save=False)

        # Check if the user is authorized
        if Env.LIMIT_TO_AUTHORIZED_USERS.get_bool() and user.tg_user_id not in Env.AUTHORIZED_USERS.get_list():
            return

        # Check if user in authorized groups
        if Env.LIMIT_TO_AUTHORIZED_GROUPS.get_bool():
            group_ids = Env.AUTHORIZED_GROUPS.get_list()

            # Group not authorized
            if message_source is MessageSource.GROUP and str(update.effective_chat.id) not in group_ids:
                # Leave chat
                logging.error(f'Unauthorized group {update.effective_chat.id}: Leaving chat')
                await update.effective_chat.leave()
                return

            # User not a member of an authorized group
            if message_source is MessageSource.PRIVATE:
                for group_id in group_ids:
                    if await user.is_chat_member(context, group_id):
                        break
                else:
                    return

        user.private_screen_previous_step = user.private_screen_step
        user.save()

    # Leave chat if not recognized
    if message_source is MessageSource.ND:
        if str(update.effective_chat.id) != Env.UPDATES_CHANNEL_ID.get():
            logging.error(f'Unknown message source for {update.effective_chat.id}: Leaving chat')
            await update.effective_chat.leave()
        return

    # Group
    # noinspection PyTypeChecker
    group_chat = None
    if message_source is MessageSource.GROUP:
        group: Group = await add_or_update_group(update, (user if update.effective_user is not None else None))
        group_chat: GroupChat = add_or_update_group_chat(update, group)

    command: Command.Command = Command.ND
    keyboard = None
    try:
        if is_command(update.message.text):
            if '/start ' in update.message.text:  # Start with parameter
                start_parameter = update.message.text.replace('/start ', '')
                try:
                    parameter_decoded = base64.b64decode(start_parameter).decode('utf-8')
                    keyboard = Keyboard.get_from_callback_query_or_info(message_source, info_str=str(parameter_decoded),
                                                                        from_deeplink=True)
                    command = Command.get_by_screen(keyboard.screen)
                    command_name = command.name
                except (UnicodeDecodeError, ValueError):
                    command_name = start_parameter
            else:
                command_name = (update.message.text.split(' ')[0])[1:].lower()
                command_name = command_name.replace('@' + Env.BOT_USERNAME.get(), '')

            if keyboard is None:
                if command_name.strip() != '':
                    command = Command.get_by_name(command_name, message_source)

                try:
                    command.parameters = update.message.text.split(' ')[1:]
                except IndexError:
                    pass

    except (AttributeError, ValueError):
        if is_callback:
            keyboard = Keyboard.get_from_callback_query_or_info(message_source, update.callback_query)

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

    # Check for spam only if a valid command or private chat
    if command != Command.ND or message_source is MessageSource.PRIVATE:
        if await is_spam(update, context, message_source, command):
            logging.warning(f'Spam detected for chat {update.effective_chat.id}: Ignoring message')
            return

    if command != Command.ND or is_callback:
        if not await validate(update, context, command, user, keyboard, target_user, is_callback, message_source,
                              group_chat):
            return

    if command != Command.ND:
        command.message_source = message_source

    try:
        match message_source:
            case MessageSource.PRIVATE:
                await manage_private_chat(update, context, command, user, keyboard)
            case MessageSource.GROUP:
                await manage_group_chat(update, context, command, user, keyboard, target_user, is_callback, group_chat)
            case MessageSource.TG_REST:
                await manage_tgrest_chat(update, context)
            case MessageSource.INLINE_QUERY:
                await manage_inline_query(update, context)
            case _:
                raise ValueError('Invalid message source')
    except DoesNotExist:
        await full_message_or_media_send_or_edit(context, phrases.ITEM_NOT_FOUND, update=update)
    except (PrivateChatException, GroupChatException, CommonChatException) as ce:
        # Manages system errors
        previous_screens = (user.get_private_screen_list()[:-1]
                            if message_source is MessageSource.PRIVATE else None)
        try:
            await full_message_send(context, escape_valid_markdown_chars(str(ce)), update=update,
                                    previous_screens=previous_screens, from_exception=True)
        except BadRequest:
            await full_message_or_media_send_or_edit(context, escape_valid_markdown_chars(str(ce)), update=update,
                                                     previous_screens=previous_screens, from_exception=True)
    except NavigationLimitReachedException:
        await full_message_send(context, phrases.NAVIGATION_LIMIT_REACHED, update=update, answer_callback=True,
                                show_alert=True)

    if user.should_update_model and user.tg_user_id is not None:
        user.save()


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE, command: Command.Command, user: User,
                   inbound_keyboard: Keyboard, target_user: User, is_callback: bool, message_source: MessageSource,
                   group_chat: GroupChat) -> bool:
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
    :param group_chat: The group chat chat
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

    _message_is_reply = message_is_reply(update)
    _is_main_group = group_chat is not None and is_main_group(group_chat)
    is_restricted_feature_error = False

    # Is active
    try:
        if not command.active:
            if command.replaced_by is not None:
                raise CommandValidationException(
                    phrases.COMMAND_NOT_ACTIVE_WITH_REPLACEMENT_ERROR.format(command.get_replaced_by_formatted()))

            raise CommandValidationException(phrases.COMMAND_NOT_ACTIVE_ERROR)

        # Feature not allowed in group_chat
        if command.feature is not None and message_source is MessageSource.GROUP:
            if not feature_is_enabled(group_chat, command.feature):
                raise CommandValidationException(phrases.COMMAND_FEATURE_DISABLED_ERROR.format(
                    get_group_or_topic_text(group_chat)
                ))

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
                if not _message_is_reply or update.message.reply_to_message is None:  # REPLY_TO_MESSAGE_BUG_FIX
                    raise CommandValidationException(phrases.COMMAND_NOT_IN_REPLY_ERROR)
            except AttributeError:
                pass

        # Cannot be in reply to yourself
        if not command.allow_self_reply:
            try:
                if _message_is_reply and update.message.reply_to_message.from_user.id == update.message.from_user.id:
                    raise CommandValidationException(phrases.COMMAND_IN_REPLY_TO_ERROR)
            except AttributeError:
                pass

        # Cannot be in reply to a Bot
        if not command.allow_reply_to_bot and not is_callback:
            try:
                # REPLY_TO_MESSAGE_BUG_FIX
                if _message_is_reply and update.effective_message.reply_to_message.from_user.is_bot:
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
            if not user_is_boss(user):
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

        # Can only be used in main group_chat
        if command.feature is not None and message_source is MessageSource.GROUP:
            feature: Feature = command.feature
            if feature.is_restricted() and not _is_main_group:
                is_restricted_feature_error = True
                raise CommandValidationException("")

        # Keyboard from deep link to a screen that doesn't allow it
        if inbound_keyboard is not None and inbound_keyboard.from_deeplink:
            if not command.allow_deeplink:
                raise CommandValidationException(phrases.COMMAND_NOT_ALLOWED_FROM_DEEPLINK_ERROR)

    except CommandValidationException as cve:
        if is_restricted_feature_error:  # Restricted feature in group_chat, no error message
            return False
        if not command.answer_callback and user_is_muted(user, group_chat):
            await delete_message(update)
        else:
            if (command.answer_callback and is_callback) or command.send_message_if_error:
                await full_message_or_media_send_or_edit(
                    context, str(cve), update=update, add_delete_button=(inbound_keyboard is None),
                    answer_callback=command.answer_callback, show_alert=command.show_alert,
                    inbound_keyboard=inbound_keyboard)
        return False

    return True


def get_user(effective_user: TelegramUser, should_save: bool = True) -> User:
    """
    Create or update the user
    :param effective_user: The Telegram user
    :param should_save: True if the user should be saved
    :return: The user
    """

    # Insert or update user
    user = User.get_or_none(User.tg_user_id == effective_user.id)
    if user is None:
        user = User()
        user.tg_user_id = effective_user.id
        user.bounty_message_limit = Env.BELLY_DAILY_BASE_LIMIT.get_int()

    user.tg_first_name = effective_user.first_name
    user.tg_last_name = effective_user.last_name
    user.tg_username = effective_user.username
    user.last_message_date = datetime.now()
    user.is_active = True

    if should_save:
        user.save()

    return user


async def add_or_update_group(update, user: User) -> Group:
    """
    Adds or updates a group_chat
    :param update: Telegram update
    :param user: User object
    :return: Group object
    """
    group = Group.get_or_none(Group.tg_group_id == update.effective_chat.id)

    if group is None:
        group = Group()
        group.tg_group_id = update.effective_chat.id

    # If the group chat has been migrated, update the ID
    try:
        if update.message.migrate_to_chat_id is not None:
            group.tg_group_id = update.message.migrate_to_chat_id
    except AttributeError:
        pass

    group.tg_group_name = update.effective_chat.title
    group.tg_group_username = update.effective_chat.username
    group.is_forum = update.effective_chat.is_forum is not None and update.effective_chat.is_forum
    group.last_message_date = datetime.now()
    group.is_active = True
    group.save()

    # Add or update the group user
    if user is not None:
        group_user = GroupUser.get_or_none((GroupUser.group == group) & (GroupUser.user == user))
        if group_user is None:
            group_user = GroupUser()
            group_user.group = group
            group_user.user = user

        group_user.last_message_date = datetime.now()
        group_user.is_active = True
        group_user.is_admin = await user.is_chat_admin(update)
        group_user.save()

    return group


def add_or_update_group_chat(update, group: Group) -> GroupChat:
    """
    Adds or updates a group_chat
    :param update: Telegram update
    :param group: Group object
    :return: GroupChat object
    """

    tg_topic_id = None
    if update.effective_chat.is_forum and update.effective_message.is_topic_message:
        tg_topic_id = update.effective_message.message_thread_id

    group_chat = GroupChat.get_or_none((GroupChat.group == group) &
                                       (GroupChat.tg_topic_id == tg_topic_id))

    if group_chat is None:
        group_chat = GroupChat()
        group_chat.group = group
        group_chat.tg_topic_id = tg_topic_id

    try:
        group_chat.tg_topic_name = update.message.reply_to_message.forum_topic_created.name
    except AttributeError:
        pass

    group_chat.last_message_date = datetime.now()
    group_chat.is_active = True
    group_chat.save()

    return group_chat


async def is_spam(update: Update, context: ContextTypes.DEFAULT_TYPE, message_source: MessageSource,
                  command: Command) -> bool:
    """
    Check if the message is spam, which would cause flooding
    :param update: Telegram update
    :param context: Telegram context
    :param message_source: The message source
    :param command: The command
    :return: True if the message is spam
    """

    if message_source is MessageSource.PRIVATE:
        context_data_type = ContextDataType.USER
        inner_key = None
    elif message_source is MessageSource.GROUP:
        context_data_type = ContextDataType.BOT
        inner_key = str(update.effective_chat.id)
    else:
        return False  # Not managing spam for other message sources

    # Game input, don't check for spam
    if command is Command.PVT_GAME_GUESS_INPUT:
        return False

    # Russian roulette, don't check for spam
    if command.screen is Screen.GRP_RUSSIAN_ROULETTE_GAME:
        return False

    # Get past messages date list
    try:
        past_messages_date_list: list[datetime] = get_context_data(
            context, context_data_type, ContextDataKey.PAST_MESSAGES_DATE, inner_key=inner_key)
    except CommonChatException:
        past_messages_date_list = []

    # Remove old messages
    now = datetime.now()
    past_messages_date_list = [
        x for x in past_messages_date_list
        if now < get_datetime_in_future_seconds(Env.ANTI_SPAM_TIME_INTERVAL_SECONDS.get_int(), start_time=x)]

    # Check if the message is spam
    spam_limit = (Env.ANTI_SPAM_PRIVATE_CHAT_MESSAGE_LIMIT.get_int() if message_source is MessageSource.PRIVATE
                  else Env.ANTI_SPAM_GROUP_CHAT_MESSAGE_LIMIT.get_int())

    if len(past_messages_date_list) >= spam_limit:
        # In case spam limit was just reached, send warning message just in private chat
        if len(past_messages_date_list) == spam_limit and message_source is MessageSource.PRIVATE:
            past_messages_date_list.append(now)
            set_context_data(context, context_data_type, ContextDataKey.PAST_MESSAGES_DATE, past_messages_date_list,
                             inner_key=inner_key)
            await full_message_send(context, phrases.ANTI_SPAM_WARNING, update=update, quote_if_group=False,
                                    new_message=True)
        return True

    # Add the message to the list
    past_messages_date_list.append(now)
    set_context_data(context, context_data_type, ContextDataKey.PAST_MESSAGES_DATE, past_messages_date_list,
                     inner_key=inner_key)

    return False
