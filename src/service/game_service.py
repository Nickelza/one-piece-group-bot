import asyncio
from typing import Tuple

from telegram import Update
from telegram.ext import ContextTypes

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
from src.model.game.whoswho.Character import Character
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_belly_formatted, add_bounty
from src.service.cron_service import convert_seconds_to_time
from src.service.message_service import full_message_send, mention_markdown_user, delete_message
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


async def end_game(game: Game, game_outcome: GameOutcome) -> Game:
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
        await add_bounty(challenger, game.wager, pending_belly_amount=half_wager)
    elif game_outcome == GameOutcome.OPPONENT_WON:
        game.status = GameStatus.LOST
        await add_bounty(opponent, game.wager, pending_belly_amount=half_wager)
    else:
        game.status = GameStatus.DRAW
        await add_bounty(challenger, half_wager, pending_belly_amount=half_wager)
        await add_bounty(opponent, half_wager, pending_belly_amount=half_wager)

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


def get_text(game: Game, game_name: str, is_finished: bool, game_outcome: GameOutcome = None, user_turn: User = None,
             is_turn_based: bool = True, character: Character = None, remaining_seconds_to_start: int = None,
             is_played_in_private_chat: bool = False) -> str:
    """
    Get the text
    :param game: The game object
    :param game_name: The game name
    :param is_finished: Is the game finished
    :param game_outcome: The game outcome
    :param user_turn: The user turn
    :param is_turn_based: Is the game turn based
    :param character: The character, in case of Who's Who
    :param remaining_seconds_to_start: The remaining seconds to start
    :param is_played_in_private_chat: Is the game played in private chat
    :return: The text
    """

    added_ot_text = ""
    if is_finished:
        if game_outcome is GameOutcome.CHALLENGER_WON:
            added_ot_text = phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.challenger))
        elif game_outcome is GameOutcome.OPPONENT_WON:
            added_ot_text = phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.opponent))
        else:
            added_ot_text = phrases.GAME_RESULT_DRAW

        if not is_turn_based and character is not None:
            added_ot_text += phrases.GAME_RESULT_CHARACTER.format(character.get_markdown_mention())
    else:
        if is_turn_based:
            added_ot_text = phrases.GAME_TURN.format(mention_markdown_user(user_turn))
        else:
            if remaining_seconds_to_start is not None:
                added_ot_text = phrases.GAME_COUNTDOWN.format(convert_seconds_to_time(remaining_seconds_to_start))
            elif is_played_in_private_chat:
                added_ot_text = phrases.GAME_STARTED

    return phrases.GAME_TEXT.format(game_name,
                                    mention_markdown_user(game.challenger),
                                    mention_markdown_user(game.opponent),
                                    get_belly_formatted(game.wager),
                                    added_ot_text)


async def delete_game(context: ContextTypes.DEFAULT_TYPE, game: Game, should_delete_message: bool = True,
                      show_timeout_message: bool = False) -> None:
    """
    Delete game
    :param context: The context
    :param game: The game
    :param should_delete_message: If the message should be deleted
    :param show_timeout_message: If the message should be edited showing timeout
    :return: None
    """

    if should_delete_message and show_timeout_message:
        raise ValueError("should_delete_message and show_timeout_message cannot be both True")

    if show_timeout_message:
        await full_message_send(context=context, group_chat=game.group_chat, text=phrases.GAME_TIMEOUT,
                                edit_message_id=game.message_id)
    elif should_delete_message:
        # Try to delete message
        if should_delete_message:
            await delete_message(context=context, group_chat=game.group_chat, message_id=game.message_id)

    # Return wager to challenger
    challenger: User = game.challenger
    challenger.game_cooldown_end_date = None
    challenger.bounty += game.wager
    challenger.pending_bounty -= game.wager
    challenger.save()

    # Delete game
    game.delete_instance()


async def validate_game(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard,
                        game: Game = None) -> Game | None:
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
        await full_message_send(context, phrases.GAME_FORCED_END, update=update)
        return None

    if GameStatus(game.status).is_finished():
        await full_message_send(context, phrases.GAME_ENDED, update=update, answer_callback=True, show_alert=True)
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


async def notify_game_turn(context: ContextTypes.DEFAULT_TYPE, game: Game, game_turn: GameTurn):
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
    context.application.create_task(enqueue_game_turn_notification(context, user_turn, opponent, game))


async def enqueue_game_turn_notification(context: ContextTypes.DEFAULT_TYPE, user: User, opponent: User, game: Game):
    """
    Enqueue a game turn notification. Waits for N time and if the game board stays unchanged, sends the notification

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
        await send_notification(context, user, GameTurnNotification(game, opponent))


def get_game_name(game_type: GameType) -> str:
    match game_type:
        case GameType.ROCK_PAPER_SCISSORS:
            return phrases.ROCK_PAPER_SCISSORS_GAME_NAME

        case GameType.RUSSIAN_ROULETTE:
            return phrases.RUSSIAN_ROULETTE_GAME_NAME

        case GameType.WHOS_WHO:
            return phrases.WHOS_WHO_GAME_NAME

        case _:
            return phrases.GAME_UNKNOWN_NAME


async def enqueue_game_timeout(context: ContextTypes.DEFAULT_TYPE, game: Game):
    """
    Enqueue a game timeout. Waits for N time and if the opponent doesn't accept, the game is deleted
    :param context: The context
    :param game: The game
    :return: None
    """

    # Wait for N time
    await asyncio.sleep(Env.GAME_CONFIRMATION_TIMEOUT.get_int())

    updated_game = Game.get_by_id(game.id)

    # Check if the game is still in the same state
    if GameStatus(updated_game.status) == GameStatus.AWAITING_OPPONENT_CONFIRMATION:
        await delete_game(context, updated_game, should_delete_message=False, show_timeout_message=True)


def get_participants(game: Game) -> Tuple[User, User]:
    """
    Get the participants of a game

    :param game: The game
    :return: The participants
    """

    return game.challenger, game.opponent
