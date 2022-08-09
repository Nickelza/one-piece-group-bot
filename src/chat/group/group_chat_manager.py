from telegram import Update
from telegram.ext import CallbackContext

import resources.Environment as Env
import src.model.enums.Command as Command
from src.chat.group.screens.screen_change_region import manage as manage_screen_change_region
from src.chat.group.screens.screen_doc_q_game import manage as manage_screen_doc_q_game
from src.chat.group.screens.screen_fight import manage as manage_screen_fight
from src.chat.group.screens.screen_game import manage as manage_screen_game
from src.chat.group.screens.screen_game_opponent_confirmation import manage as manage_screen_game_opponent_confirmation
from src.chat.group.screens.screen_game_rps import manage as manage_screen_game_rps
from src.chat.group.screens.screen_game_rr import manage as manage_screen_game_rr
from src.chat.group.screens.screen_game_selection import manage as manage_screen_game_selection
from src.chat.group.screens.screen_prediction_bet import manage as manage_screen_prediction_bet
from src.chat.group.screens.screen_prediction_bet_remove import manage as manage_screen_prediction_bet_remove
from src.chat.group.screens.screen_status import manage as manage_screen_show_status
from src.model.User import User
from src.model.enums.Screen import Screen
from src.model.error.GroupChatError import GroupChatError
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import add_bounty
from src.service.bounty_service import get_message_belly
from src.service.message_service import full_message_send, delete_message


def update_user_bounty(update: Update, context: CallbackContext, user: User) -> User:
    """
    Creates a new user or updates an existing user
    :param update: Telegram update
    :param context: Telegram context
    :param user: User object
    :return: Updated user
    """

    user = add_bounty(user, get_message_belly(update, user), context=context, update=update,
                      should_update_location=True)
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

    if not validate(update, user):
        return

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
                manage_screen_show_status(update, context, command)

            case Screen.GRP_DOC_Q_GAME:  # Doc Q Game
                manage_screen_doc_q_game(update, context, user, keyboard=keyboard)

            case Screen.GRP_CHANGE_REGION:  # Change region
                manage_screen_change_region(update, context, user, keyboard=keyboard, command=command)

            case Screen.GRP_FIGHT:  # Fight
                manage_screen_fight(update, context, user, keyboard=keyboard)

            case Screen.GRP_GAME:  # Game
                manage_screen_game(update, context, user, command)

            case Screen.GRP_GAME_SELECTION:  # Game selection
                manage_screen_game_selection(update, context, inbound_keyboard=keyboard)

            case Screen.GRP_GAME_OPPONENT_CONFIRMATION:  # Game opponent confirmation
                manage_screen_game_opponent_confirmation(update, context, user, inbound_keyboard=keyboard)

            case Screen.GRP_ROCK_PAPER_SCISSORS_GAME:  # Game Rock Paper Scissors
                manage_screen_game_rps(update, context, user, inbound_keyboard=keyboard)

            case Screen.GRP_RUSSIAN_ROULETTE_GAME:  # Game Russian Roulette
                manage_screen_game_rr(update, context, user, inbound_keyboard=keyboard)

            case Screen.GRP_PREDICTION_BET:  # Prediction bet
                manage_screen_prediction_bet(update, context, user, command)

            case Screen.GRP_PREDICTION_BET_REMOVE:  # Prediction bet remove
                manage_screen_prediction_bet_remove(update, context, user, command)

            case _:  # Unknown screen
                if update.callback_query is not None:
                    full_message_send(context, GroupChatError.UNRECOGNIZED_SCREEN.build(), update, new_message=True)


def validate(update: Update, user: User) -> bool:
    """
    Validates the message, deleting it if it's not valid
    :param update: Telegram update
    :param user: User object
    :return: True if valid, False otherwise
    """

    # Stickers
    try:
        if update.message.sticker is not None \
                and user.location_level < Env.REQUIRED_LOCATION_LEVEL_SEND_STICKER.get_int():
            delete_message(update)
            return False
    except AttributeError:
        pass

    # Animations
    try:
        if update.message.animation is not None \
                and user.location_level < Env.REQUIRED_LOCATION_LEVEL_SEND_ANIMATION.get_int():
            delete_message(update)
            return False
    except AttributeError:
        pass

    # Forwarded
    try:
        if update.message.forward_from is not None \
                and user.location_level < Env.REQUIRED_LOCATION_LEVEL_FORWARD_MESSAGE.get_int() \
                and str(update.message.forward_from.id) not in Env.WHITELIST_FORWARD_MESSAGE.get_list():
            delete_message(update)
            return False
    except AttributeError:
        pass

    return True
