from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.chat.group.screens.screen_game_rps import manage as manage_rps
from src.chat.group.screens.screen_game_rr import manage as manage_rr
from src.model.Game import Game
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.error.GroupChatError import GroupChatError, GroupChatException
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.game_service import delete_game, validate_game
from src.service.message_service import full_message_send, mention_markdown_user


def manage(update: Update, context: CallbackContext, user: User, inbound_keyboard: Keyboard) -> None:
    """
    Manage the game screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    # Get the game from validation, will handle error messages
    game = validate_game(update, context, inbound_keyboard)
    if game is None:
        return

    # User clicked on cancel button
    if ReservedKeyboardKeys.DELETE in inbound_keyboard.info or inbound_keyboard.info['b'] == 0:
        delete_message = True
        if 'b' in inbound_keyboard.info:
            delete_message = False
            ot_text = phrases.GAME_CHALLENGE_REJECTED.format(mention_markdown_user(game.opponent))
            full_message_send(context, ot_text, update=update, authorized_users=[game.challenger, game.opponent],
                              add_delete_button=True)

        delete_game(update, context, game, delete_message=delete_message)
        return

    # Opponent does not have enough bounty
    if user.bounty < game.wager:
        delete_game(update, context, game, delete_message=False)
        full_message_send(context, phrases.ACTION_INSUFFICIENT_BOUNTY, update=update, add_delete_button=True)
        return

    user.bounty -= game.wager
    user.pending_bounty += game.wager
    game.wager += game.wager
    game.save()

    dispatch_game(update, context, user, inbound_keyboard, game)


def dispatch_game(update: Update, context: CallbackContext, user: User, inbound_keyboard: Keyboard, game: Game) -> None:
    """
    Dispatch game
    :param update: The update
    :param context: The context
    :param user: The user
    :param inbound_keyboard: The inbound keyboard
    :param game: The game
    :return: None
    """

    game_type: GameType = GameType(game.type)
    match game_type:
        case GameType.ROCK_PAPER_SCISSORS:
            manage_rps(update, context, user, inbound_keyboard, game)

        case GameType.RUSSIAN_ROULETTE:
            manage_rr(update, context, user, inbound_keyboard, game)
        case _:
            raise GroupChatException(GroupChatError.INVALID_GAME)
