from telegram import Update, TelegramError
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.chat.group.screens.screen_game_rps import manage as manage_rps
from src.model.Game import Game
from src.model.User import User
from src.model.error.GroupChatError import GroupChatError
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
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

    try:
        game: Game = Game.get_by_id(inbound_keyboard.info['a'])
    except IndexError:
        full_message_send(context, GroupChatError.GAME_NOT_FOUND.build(), update=update)
        return

    # User clicked on cancel button
    if 'x' in inbound_keyboard.info or inbound_keyboard.info['b'] == 0:
        delete_message = True
        if 'b' in inbound_keyboard.info:
            delete_message = False
            ot_text = phrases.GAME_CHALLENGE_REJECTED.format(mention_markdown_user(game.opponent))
            full_message_send(context, ot_text, update=update, authorized_users=[game.challenger, game.opponent],
                              add_delete_button=True)

        delete_game(update, context, game, delete_message=delete_message)
        return

    # Challenger does not have enough bounty
    if user.bounty < game.wager:
        full_message_send(context, phrases.GAME_INSUFFICIENT_BOUNTY, update=update, add_delete_button=True)
        return

    user.bounty -= game.wager
    user.pending_bounty += game.wager
    user.save()
    game.wager += game.wager
    game.save()

    dispatch_game(update, context, user, inbound_keyboard, game)


def delete_game(update: Update, context: CallbackContext, game: Game, delete_message: bool = True) -> None:
    """
    Delete game
    :param update: The update
    :param context: The context
    :param game: The game
    :param delete_message: If the message should be deleted
    :return: None
    """
    # Try to delete message
    if delete_message:
        try:
            context.bot.delete_message(update.effective_chat.id, game.message_id)
        except TelegramError:
            pass

    # Return wager to challenger
    challenger: User = game.challenger
    challenger.bounty += game.wager
    challenger.pending_bounty -= game.wager
    challenger.save()

    # Delete game
    game.delete_instance()


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
        case _:
            full_message_send(context, GroupChatError.INVALID_GAME.build(), update=update)
