import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.common.screens.screen_game_gol import (
    run_game as run_game_gol,
    validate_answer as validate_answer_gol,
    issue_life_if_possible as issue_hint_if_possible_gol,
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
from src.service.date_service import (
    get_datetime_in_future_seconds,
    get_elapsed_seconds,
    datetime_is_after,
)
from src.service.game_service import (
    get_game_from_keyboard,
    guess_game_validate_answer,
    challenger_has_finished_or_opponent_timeout,
)
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
                    user=user,
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

    if await challenger_has_finished_or_opponent_timeout(context, game, user):
        return

    # Regular input
    match game_type:
        case GameType.GUESS_OR_LIFE:
            await validate_answer_gol(update, context, game, user)

        case GameType.PUNK_RECORDS:
            await validate_answer_pr(update, context, game, user)
        case _:
            await guess_game_validate_answer(update, context, game, user)

    # Try restarting the run game thread if it's down
    context.application.create_task(restart_hint_thread_if_down(context, game, user))


async def restart_hint_thread_if_down(
    context: ContextTypes.DEFAULT_TYPE, game: Game, user: User = None
) -> None:
    """
    Restart the hint thread if it's down
    :param context: The context object
    :param game: The game object
    :param user: The user
    :return: None
    """

    if game.is_finished():
        return

    match game.get_type():
        case GameType.GUESS_OR_LIFE:
            issue_hint_if_possible_function = issue_hint_if_possible_gol
            run_game_function = run_game_gol

        case _:
            raise ValueError(f"Unsupported game type: {game.get_type()}")

    # No user given (so from timer), if is global game, then also try restarting for opponent
    if user is None and game.is_global() and game.has_opponent():
        context.application.create_task(restart_hint_thread_if_down(context, game, game.opponent))

    if user is None:
        user = game.challenger

    last_hint_date = (
        game.last_hint_opponent_date
        if game.is_global() and user and game.is_opponent(user)
        else game.last_hint_date
    )

    hint_every_seconds = game.get_seconds_for_every_hint()

    # Give a 10-second margin in case in the same moment the hint is being issued by the regular thread
    if last_hint_date is None or datetime_is_after(
        get_datetime_in_future_seconds(hint_every_seconds + 10, start_time=last_hint_date)
    ):
        return

    seconds_since_last_hint = get_elapsed_seconds(last_hint_date)
    hints_to_issue, hint_seconds_remaining = divmod(seconds_since_last_hint, hint_every_seconds)

    # Issue all missing hints
    for _ in range(hints_to_issue):
        if not issue_hint_if_possible_function(game, user):
            if _ == 0:  # No hints were issued
                return
            break

    game.thread_restart_count += 1
    game.save()

    logging.info(
        f"Restart hint thread for game {game.id} after {seconds_since_last_hint} seconds delay and {hints_to_issue} "
        f"missed hints for user {user.id}"
    )

    # Send message, waiting the remaining amount of time till the next hint
    context.application.create_task(
        run_game_function(
            context, game, user, hint_wait_seconds=(hint_every_seconds - hint_seconds_remaining)
        )
    )
