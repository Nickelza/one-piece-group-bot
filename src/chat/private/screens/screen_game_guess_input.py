from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.common.screens.screen_game_gol import (
    run_game as run_game_gol,
    validate_answer as validate_answer_gol,
)
from src.chat.common.screens.screen_game_pr import (
    run_game as run_game_pr,
    validate_answer as validate_answer_pr,
)
from src.chat.common.screens.screen_game_shambles import run_game as run_game_shambles
from src.chat.common.screens.screen_game_ww import run_game as run_game_ww
from src.model.Game import Game
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.game_service import get_game_from_keyboard, guess_game_validate_answer
from src.service.message_service import full_message_send


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the game input screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    if inbound_keyboard is not None:  # From deep link
        game: Game = get_game_from_keyboard(inbound_keyboard)
    else:  # From private chat
        game: Game = Game.get_by_id(user.private_screen_in_edit_id)

    # User is not a player of the game
    if not game.is_player(user):
        await full_message_send(context, phrases.GAME_INPUT_NOT_PLAYER, update=update)
        return

    game_status: GameStatus = GameStatus(game.status)
    game_type: GameType = GameType(game.type)

    # Game is finished
    if game_status.is_finished():
        await full_message_send(context, phrases.GAME_INPUT_GAME_FINISHED, update=update)
        return

    game.last_interaction_date = datetime.now()
    game.save()

    # Game in countdown
    if game_status is GameStatus.COUNTDOWN_TO_START:
        await full_message_send(context, phrases.GAME_INPUT_COUNTDOWN, update=update)
        return

    if inbound_keyboard is not None:  # From deep link
        match game_type:
            case GameType.SHAMBLES:
                await run_game_shambles(
                    context,
                    game,
                    send_to_user=user,
                    should_send_to_all_players=False,
                    schedule_next_send=False,
                )
            case GameType.WHOS_WHO:
                await run_game_ww(
                    context,
                    game,
                    send_to_user=user,
                    should_send_to_all_players=False,
                    schedule_next_send=False,
                )

            case GameType.GUESS_OR_LIFE:
                await run_game_gol(
                    context,
                    game,
                    send_to_user=user,
                    should_send_to_all_players=False,
                    schedule_next_send=False,
                )

            case GameType.PUNK_RECORDS:
                await run_game_pr(
                    context,
                    game,
                    send_to_user=user,
                    should_send_to_all_players=False,
                    schedule_next_send=False,
                    is_first_run=False,
                )

            case _:
                raise ValueError(f"Game type {game.type} not supported")

        return

    # Regular input
    match game_type:
        case GameType.GUESS_OR_LIFE:
            return await validate_answer_gol(update, context, game, user)

        case GameType.PUNK_RECORDS:
            return await validate_answer_pr(update, context, game, user)
        case _:
            return await guess_game_validate_answer(update, context, game, user)
