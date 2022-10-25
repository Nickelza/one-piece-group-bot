import asyncio
import threading

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import CallbackContext

import resources.Environment as Env
import resources.phrases as phrases
from src.model.Game import Game
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.Notification import GameTurnNotification
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.error.GroupChatError import GroupChatError, GroupChatException
from src.model.game.GameOutcome import GameOutcome
from src.model.game.GameTurn import GameTurn
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_belly_formatted, add_bounty
from src.service.message_service import full_message_send, mention_markdown_user
from src.service.notification_service import send_notification


def get_game_from_keyboard(inbound_keyboard: Keyboard) -> Game:
    """
    Get the game from the keyboard
    :param inbound_keyboard: The keyboard
    :return: The game
    """

    try:
        game: Game = Game.get_by_id(inbound_keyboard.info[ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY])
        return game
    except IndexError:
        raise GroupChatException(GroupChatError.GAME_NOT_FOUND)


def end_game(game: Game, game_outcome: GameOutcome) -> Game:
    """
    End the game, set the status and return the game
    :param game: The game
    :param game_outcome: The outcome
    :return: The game
    """

    challenger: User = game.challenger
    opponent: User = game.opponent
    half_wager: int = game.wager / 2

    if game_outcome == GameOutcome.CHALLENGER_WON:
        game.status = GameStatus.WON
        add_bounty(challenger, game.wager, pending_belly_amount=half_wager)
    elif game_outcome == GameOutcome.OPPONENT_WON:
        game.status = GameStatus.LOST
        add_bounty(opponent, game.wager, pending_belly_amount=half_wager)
    else:
        game.status = GameStatus.DRAW
        add_bounty(challenger, half_wager, pending_belly_amount=half_wager)
        add_bounty(opponent, half_wager, pending_belly_amount=half_wager)

    challenger.pending_bounty -= half_wager
    opponent.pending_bounty -= half_wager

    # Refresh
    game.challenger = challenger
    game.opponent = opponent

    challenger.save()
    opponent.save()
    game.save()

    return game


def get_game_authorized_tg_user_ids(game: Game) -> list[int]:
    """
    Get the authorized tg user ids
    :param game: The game
    :return: The authorized tg user ids
    """

    challenger: User = game.challenger
    opponent: User = game.opponent

    return [challenger.tg_user_id, opponent.tg_user_id]


def get_text(game: Game, game_name: str, is_finished: bool, game_outcome: GameOutcome = None, user_turn: User = None
             ) -> str:
    """
    Get the text
    :param game: The game object
    :param game_name: The game name
    :param is_finished: Is the game finished
    :param game_outcome: The game outcome
    :param user_turn: The user turn
    :return: The text
    """

    if is_finished:
        if game_outcome is GameOutcome.CHALLENGER_WON:
            added_ot_text = phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.challenger))
        elif game_outcome is GameOutcome.OPPONENT_WON:
            added_ot_text = phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.opponent))
        else:
            added_ot_text = phrases.GAME_RESULT_DRAW
    else:
        added_ot_text = phrases.GAME_TURN.format(mention_markdown_user(user_turn))

    return phrases.GAME_TEXT.format(game_name,
                                    mention_markdown_user(game.challenger),
                                    mention_markdown_user(game.opponent),
                                    get_belly_formatted(game.wager),
                                    added_ot_text)


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
    challenger.can_initiate_game = True
    challenger.bounty += game.wager
    challenger.pending_bounty -= game.wager
    challenger.save()

    # Delete game
    game.delete_instance()


def reset_can_initiate_game() -> None:
    """
    Reset the user's can_change_region flag

    :return: None
    """

    User.update(can_initiate_game=True).where(User.can_initiate_game is True).execute()


def validate_game(update: Update, context: CallbackContext, inbound_keyboard: Keyboard, game: Game = None
                  ) -> Game | None:
    """
    Validate the game
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The keyboard
    :param game: The game
    :return: The game if valid, None otherwise
    """

    # Get the game
    if game is None:
        game = get_game_from_keyboard(inbound_keyboard)

    if game.status == GameStatus.FORCED_END:
        full_message_send(context, phrases.GAME_FORCED_END, update=update)
        return None

    if GameStatus(game.status).is_finished():
        full_message_send(context, phrases.GAME_ENDED, update=update, answer_callback=True, show_alert=True)
        return None

    return game


def force_end_all_active() -> None:
    """
    Force all games in progress to end

    :return: None
    """

    active_games = Game.select().where(Game.status.not_in(GameStatus.get_finished()))

    for game in active_games:
        game.status = GameStatus.FORCED_END
        game.save()


def notify_game_turn(context: CallbackContext, game: Game, game_turn: GameTurn):
    """
    Notify a user that it's their turn

    :param context: The context
    :param game: The game
    :param game_turn: The game turn
    :return: None
    """

    if game_turn == GameTurn.CHALLENGER:
        user_turn: User = game.challenger
        opponent: User = game.opponent
    else:
        user_turn: User = game.opponent
        opponent: User = game.challenger

    # Fire and forget
    t = threading.Thread(target=run_async_loop_in_thread, args=(context, user_turn, opponent, game))
    t.start()


def run_async_loop_in_thread(context: CallbackContext, user: User, opponent: User, game: Game):
    """
    Run the async loop in a thread

    :param context: The context
    :param user: The user
    :param opponent: The opponent
    :param game: The game
    :return: None
    """
    asyncio.run(enqueue_game_turn_notification(context, user, opponent, game))


async def enqueue_game_turn_notification(context: CallbackContext, user: User, opponent: User, game: Game):
    """
    Enqueue a game turn notification. Waits for N time and if the game board is still the same, sends the notification

    :param context: The context
    :param user: The user
    :param opponent: The opponent
    :param game: The game
    :return: None
    """

    # Wait for N time
    await asyncio.sleep(Env.GAME_TURN_NOTIFICATION_TIME.get_int())

    updated_game = Game.get_by_id(game.id)

    # Check if the game board is still the same
    if updated_game.board == game.board:
        send_notification(context, user, GameTurnNotification(game, opponent))


def get_game_name(game_type: GameType) -> str:
    match game_type:
        case GameType.ROCK_PAPER_SCISSORS:
            return phrases.ROCK_PAPER_SCISSORS_GAME_NAME

        case GameType.RUSSIAN_ROULETTE:
            return phrases.RUSSIAN_ROULETTE_GAME_NAME

        case _:
            return phrases.GAME_UNKNOWN_NAME
