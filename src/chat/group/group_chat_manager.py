from telegram import Update
from telegram.ext import CallbackContext

import resources.Environment as Env
import src.model.enums.Command as Command
from src.chat.group.screens.screen_change_region import manage as manage_screen_change_region
from src.chat.group.screens.screen_doc_q_game import manage as manage_screen_doc_q_game
from src.chat.group.screens.screen_fight import manage as manage_screen_fight
from src.chat.group.screens.screen_status import manage as manage_screen_show_status
from src.model.User import User
from src.model.enums.Screen import Screen
from src.model.error.GroupChatError import GroupChatError
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import add_bounty
from src.service.bounty_service import get_message_belly
from src.service.message_service import full_message_send


def update_user_bounty(update: Update, context: CallbackContext, user: User) -> User:
    """
    Creates a new user or updates an existing user
    :param update: Telegram update
    :param context: Telegram context
    :param user: User object
    :return: Updated user
    """

    user = add_bounty(context, user, get_message_belly(update, user), update)
    user.save()

    return user


def manage(update: Update, context: CallbackContext, command: Command.Command, user: User, keyboard: Keyboard = None
           ) -> None:
    """
    Main function for the group chat manager
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command to execute
    :param user: User object
    :param keyboard: Keyboard
    :return: None
    """

    # Insert or update user, with message count
    try:
        # Ignore self bot messages or from linked channel
        if update.effective_user.is_bot or update.message.sender_chat.id == Env.OPD_CHANNEL_ID.get_int():
            return
    except AttributeError:
        pass

    user = update_user_bounty(update, context, user)

    dispatch_screens(update, context, user, keyboard, command)


def dispatch_screens(update: Update, context: CallbackContext, user: User, keyboard: Keyboard,
                     command: Command.Command) -> None:
    """
    Dispatches the different screens
    :param update: Telegram update
    :param context: Telegram context
    :param user: User object
    :param keyboard: Keyboard to send
    :param command: Command to execute
    :return: None
    """

    if command is not Command.ND:
        match command.screen:
            case Screen.GRP_USER_STATUS:  # User status
                manage_screen_show_status(update, context)

            case Screen.GRP_DOC_Q_GAME:  # Doc Q Game
                manage_screen_doc_q_game(update, context, user, keyboard)

            case Screen.GRP_CHANGE_REGION:  # Change region
                manage_screen_change_region(update, context, user, keyboard, command)

            case Screen.GRP_FIGHT:  # Fight
                manage_screen_fight(update, context, user, keyboard, command)

            case _:  # Unknown screen
                if update.callback_query is not None:
                    full_message_send(context, GroupChatError.UNRECOGNIZED_SCREEN.build(), update, new_message=True)
