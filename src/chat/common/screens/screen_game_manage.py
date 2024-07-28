import logging

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
from src.chat.common.screens.screen_game_gol import (
    get_boards as get_boards_gol,
    run_game as run_game_gol,
    issue_life_if_possible as issue_hint_if_possible_gol,
)
from src.chat.common.screens.screen_game_pr import (
    run_game as run_game_pr,
    issue_hint_if_possible as issue_hint_if_possible_pr,
)
from src.chat.common.screens.screen_game_rps import manage as manage_rps
from src.chat.common.screens.screen_game_rr import manage as manage_rr
from src.chat.common.screens.screen_game_ww import (
    run_game as run_game_ww,
    reduce_level_if_possible as issue_hint_if_possible_ww,
)
from src.model.Game import Game
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.Screen import Screen
from src.model.error.GroupChatError import GroupChatException, GroupChatError
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.date_service import (
    datetime_is_after,
    get_datetime_in_future_seconds,
    get_elapsed_seconds,
)
from src.service.game_service import (
    guess_game_countdown_to_start,
    validate_game,
    challenger_has_finished_or_opponent_timeout,
    get_generic_boards_for_guess_game,
    enqueue_timeout_opponent_guess_game,
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

        case GameType.PUNK_RECORDS:
            run_game_function = run_game_pr
            get_boards_function = get_generic_boards_for_guess_game

        # case GameType.SHAMBLES:
        #     run_game_function = run_game_shambles
        #     get_boards_function = get_generic_boards_for_guess_game

        case GameType.WHOS_WHO:
            run_game_function = run_game_ww
            get_boards_function = get_generic_boards_for_guess_game

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


async def dispatch_game(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    inbound_keyboard: Keyboard,
    game: Game,
    should_start_immediately: bool = False,
) -> None:
    """
    Dispatch game
    :param update: The update
    :param context: The context
    :param user: The user
    :param inbound_keyboard: The inbound keyboard
    :param game: The game
    :param should_start_immediately: If the game should be started immediately, from challenger/opponent confirmation
    :return: None
    """
    # Opponent just started, enqueue timeout if challenger has already finished. In case they have not
    # the timeout will be enqueued when they do
    if game.is_global() and should_start_immediately and game.is_opponent(user):
        if game.is_opponent(user):
            context.application.create_task(enqueue_timeout_opponent_guess_game(context, game))

    context.application.create_task(restart_hint_thread_if_down(context, game, user=user))

    game_type: GameType = GameType(game.type)
    match game_type:
        case GameType.ROCK_PAPER_SCISSORS:
            await manage_rps(update, context, user, inbound_keyboard, game)

        case GameType.RUSSIAN_ROULETTE:
            await manage_rr(update, context, user, inbound_keyboard, game)

        case (
            GameType.SHAMBLES | GameType.WHOS_WHO | GameType.GUESS_OR_LIFE | GameType.PUNK_RECORDS
        ):
            await manage(
                update,
                context,
                inbound_keyboard,
                user,
                game,
                should_start_immediately=should_start_immediately,
            )

        case _:
            raise GroupChatException(GroupChatError.INVALID_GAME)


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

    if not game.is_guess_based():
        return

    if game.is_finished():
        return

    match game.get_type():
        case GameType.GUESS_OR_LIFE:
            issue_hint_if_possible_function = issue_hint_if_possible_gol
            run_game_function = run_game_gol

        case GameType.PUNK_RECORDS:
            issue_hint_if_possible_function = issue_hint_if_possible_pr
            run_game_function = run_game_pr

        # TODO
        # case GameType.SHAMBLES:
        #     issue_hint_if_possible_function = issue_hint_if_possible_shambles
        #     run_game_function = run_game_shambles
        #

        case GameType.WHOS_WHO:
            issue_hint_if_possible_function = issue_hint_if_possible_ww
            run_game_function = run_game_ww

        case _:
            raise ValueError(f"Unsupported game type: {game.get_type()}")

    # No user given (so from timer), if is global game, then also try restarting for opponent
    if user is None and game.is_global() and game.has_opponent():
        context.application.create_task(restart_hint_thread_if_down(context, game, game.opponent))

    if user is None:
        user = game.challenger

    # User is challenger and they have finished
    if game.is_global() and user and game.is_challenger(user) and game.challenger_has_finished():
        return

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
            context,
            game,
            user,
            hint_wait_seconds=(hint_every_seconds - hint_seconds_remaining),
        )
    )
