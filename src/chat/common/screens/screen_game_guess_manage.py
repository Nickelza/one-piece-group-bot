from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
from src.chat.common.screens.screen_game_gol import (
    get_boards as get_boards_gol,
    run_game as run_game_gol,
)
from src.model.Game import Game
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.Screen import Screen
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.game_service import (
    guess_game_countdown_to_start,
    validate_game,
    challenger_has_finished_or_opponent_timeout,
)


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
    user: User,
    game: Game,
    should_start_immediately: bool = False,
) -> None:
    """
    Manage guessing games
    :param update: The update object
    :param context: The context object
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :param game: The game object
    :param should_start_immediately: If to start without waiting
    :return: None
    """

    # Get the game from validation, will handle error messages
    game = await validate_game(update, context, inbound_keyboard, game)
    if game is None:
        return

    match game.get_type():
        case GameType.GUESS_OR_LIFE:
            run_game_function = run_game_gol
            get_boards_function = get_boards_gol

        case _:
            raise ValueError(f"Unsupported game type: {game.get_type()}")

    # Initialize board
    get_boards_function(game)

    if should_start_immediately:
        # No need to set status, since countdown time is 0, it will be set immediately to IN_PROGRESS
        context.application.create_task(
            guess_game_countdown_to_start(update, context, game, 0, run_game_function, user)
        )
        return

    # From opponent confirmation in group, start countdown
    if inbound_keyboard.screen == Screen.GRP_GAME_OPPONENT_CONFIRMATION:
        game.status = GameStatus.COUNTDOWN_TO_START
        game.save()
        context.application.create_task(
            guess_game_countdown_to_start(
                update, context, game, Env.GAME_START_WAIT_TIME.get_int(), run_game_function, user
            )
        )
        return

    if await challenger_has_finished_or_opponent_timeout(context, game, user):
        return

    await run_game_function(
        context, game, user, should_send_to_all_players=False, schedule_next_send=False
    )
