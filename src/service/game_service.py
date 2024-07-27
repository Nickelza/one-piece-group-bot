import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Tuple, Callable

from peewee import DoesNotExist
from telegram import Update
from telegram.error import RetryAfter
from telegram.ext import ContextTypes

import constants as c
from resources import phrases as phrases, Environment as Env
from src.model.Game import Game
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.ContextDataKey import ContextDataKey
from src.model.enums.Emoji import Emoji
from src.model.enums.GameStatus import GameStatus
from src.model.enums.Notification import GameTurnNotification, GameOutcomeNotification
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.SavedMedia import SavedMedia
from src.model.enums.SavedMediaType import SavedMediaType
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.enums.income_tax.IncomeTaxEventType import IncomeTaxEventType
from src.model.error.CommonChatError import CommonChatException
from src.model.game.GameBoard import GameBoard
from src.model.game.GameOutcome import GameOutcome
from src.model.game.GameTurn import GameTurn
from src.model.game.GameType import GameType
from src.model.game.punkrecords.PunkRecords import PunkRecords
from src.model.game.shambles.Shambles import Shambles
from src.model.game.whoswho.WhosWho import WhosWho
from src.model.pojo.Keyboard import Keyboard
from src.model.wiki.Character import Character
from src.model.wiki.SupabaseRest import SupabaseRest
from src.model.wiki.Terminology import Terminology
from src.service.bot_service import get_bot_context_data, set_bot_context_data
from src.service.bounty_service import add_or_remove_bounty, validate_amount
from src.service.date_service import (
    convert_seconds_to_duration,
    get_remaining_duration,
    get_elapsed_duration,
)
from src.service.devil_fruit_service import get_ability_adjusted_datetime
from src.service.message_service import (
    mention_markdown_user,
    delete_message,
    full_media_send,
    get_message_url,
    full_message_send,
    full_message_or_media_send_or_edit,
    get_deeplink,
)
from src.service.notification_service import send_notification
from src.utils.phrase_utils import get_outcome_text
from src.utils.string_utils import get_belly_formatted


def get_game_from_keyboard(inbound_keyboard: Keyboard) -> Game:
    """
    Get the game from the keyboard
    :param inbound_keyboard: The keyboard
    :return: The game
    """

    try:
        game: Game = Game.get_by_id(
            inbound_keyboard.info[ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY]
        )
        return game
    except IndexError:
        raise CommonChatException(phrases.GAME_NOT_FOUND)


async def end_game(
    game: Game,
    game_outcome: GameOutcome,
    context: ContextTypes.DEFAULT_TYPE,
    is_forced_end: bool = False,
    update: Update = None,
    send_outcome_to_user: User = None,
) -> Game:
    """
    End the game, set the status and return the game
    :param game: The game
    :param game_outcome: The outcome
    :param context: The context
    :param is_forced_end: If the game was forced to end
    :param update: The update
    :param send_outcome_to_user: End user to send game outcome notification
    :return: The game
    """

    challenger: User = game.challenger
    opponent: User = game.opponent
    half_wager: int = int(game.wager / 2)
    previous_status: GameStatus = game.get_status()

    bounty_for_challenger = bounty_for_opponent = 0
    pending_bounty_for_challenger = pending_bounty_for_opponent = int(game.wager / 2)
    if game_outcome == GameOutcome.CHALLENGER_WON:
        # Challenger won
        game.status = GameStatus.WON
        bounty_for_challenger = game.wager
    elif game_outcome == GameOutcome.OPPONENT_WON:
        # Opponent won
        game.status = GameStatus.LOST
        bounty_for_opponent = game.wager
    else:
        # No one won
        bounty_for_challenger = half_wager
        bounty_for_opponent = half_wager
        game.status = GameStatus.FORCED_END if is_forced_end else GameStatus.DRAW

    if not previous_status.no_wager_was_collected():
        await add_or_remove_bounty(
            challenger,
            bounty_for_challenger,
            context=context,
            pending_belly_amount=pending_bounty_for_challenger,
            update=update,
            tax_event_type=IncomeTaxEventType.GAME,
            event_id=game.id,
            opponent=opponent,
        )

        if opponent is not None:
            await add_or_remove_bounty(
                opponent,
                bounty_for_opponent,
                context=context,
                pending_belly_amount=pending_bounty_for_opponent,
                update=update,
                tax_event_type=IncomeTaxEventType.GAME,
                event_id=game.id,
                opponent=challenger,
            )

    # Refresh
    game.challenger = challenger
    game.opponent = opponent

    # Save opponent time if relevant
    if game.is_global() and game_outcome is GameOutcome.OPPONENT_WON:
        game.global_opponent_end_date = datetime.now()

    challenger.save()
    if opponent is not None:
        opponent.save()
    game.save()

    if not is_forced_end:
        notification_users: list[User] = []
        if send_outcome_to_user:
            notification_users.append(send_outcome_to_user)

        add_time_and_terminology = False
        # If is global guess based game and someone won, always send notification
        if game.is_guess_based() and game.is_global() and game.has_winner():
            add_time_and_terminology = True

            # Always send to challenger
            notification_users.append(game.challenger)

            # Send to opponent too only if they didn't win, so it's due to timeout
            # If they won, no need for notification since the game specific text will contain it
            if game_outcome is GameOutcome.CHALLENGER_WON:
                notification_users.append(game.opponent)

        for u in notification_users:
            footer_text = ""
            if add_time_and_terminology:
                footer_text = phrases.GAME_OUTCOME_NOTIFICATION_TIME_TERMINOLOGY.format(
                    get_global_time_based_text(game, u),
                    get_guess_game_result_term_text(get_terminology_from_game(game)),
                )
            await send_notification(context, u, GameOutcomeNotification(game, u, footer_text))

        # Edit message in group, if global and started from a group
        if game.is_global() and game.group_chat is not None:
            ot_text = get_text(game, True, game_outcome=game_outcome, is_for_group_global=True)
            context.application.create_task(
                full_media_send(
                    context,
                    caption=ot_text,
                    chat_id=game.group_chat.group.tg_group_id,
                    edit_message_id=game.message_id,
                    add_delete_button=True,
                    edit_only_caption_and_keyboard=True,
                    group_chat=game.group_chat,
                    authorized_users=[game.challenger],
                )
            )

    return game


def get_text(
    game: Game,
    is_finished: bool,
    game_outcome: GameOutcome = None,
    user_turn: User = None,
    terminology: Terminology = None,
    remaining_seconds_to_start: int = None,
    is_played_in_private_chat: bool = False,
    text_to_add_before_footer: str = None,
    is_for_group_global: bool = False,
    challenger_has_finished: bool = False,
    opponent_has_finished: bool = False,
) -> str:
    """
    Get the text
    :param game: The game object
    :param is_finished: Is the game finished
    :param game_outcome: The game outcome
    :param user_turn: The user turn
    :param terminology: The character, in case of Who's Who
    :param remaining_seconds_to_start: The remaining seconds to start
    :param is_played_in_private_chat: Is the game played in private chat
    :param text_to_add_before_footer: The text to add before the footer
    :param is_for_group_global: If the text is for a group and the game is global
    :param challenger_has_finished: If the challenger has finished playing
    :param opponent_has_finished: If the opponent has finished playing
    :return: The text
    """

    added_ot_text = ""
    difficulty_text = ""

    is_turn_based = game.is_turn_based()

    game_type: GameType = game.get_type()
    if game_type.has_difficulty_level():
        difficulty_text = phrases.GAME_DIFFICULTY.format(game.get_difficulty().get_name())

    if text_to_add_before_footer is not None:
        added_ot_text += text_to_add_before_footer

    if game.is_guess_based() and game.is_global() and not is_for_group_global:
        added_ot_text += get_global_time_based_text(game, user_turn)

    if is_finished and game_outcome is not None and game_outcome is not GameOutcome.NONE:
        if not is_turn_based and terminology is not None:
            added_ot_text += get_guess_game_result_term_text(terminology) + "\n\n"

        if game_outcome is GameOutcome.CHALLENGER_WON:
            added_ot_text += phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.challenger))
        elif game_outcome is GameOutcome.OPPONENT_WON:
            added_ot_text += phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.opponent))
        else:
            added_ot_text += phrases.GAME_RESULT_DRAW
    elif game.is_global() and not is_for_group_global:
        if game.is_challenger(user_turn) and not opponent_has_finished:
            added_ot_text += phrases.GAME_GLOBAL_PENDING_CHALLENGER
        elif not challenger_has_finished:
            added_ot_text += phrases.GAME_GLOBAL_PENDING_OPPONENT
    elif not is_for_group_global:
        if is_turn_based:
            added_ot_text += phrases.GAME_TURN.format(mention_markdown_user(user_turn))
        else:
            if remaining_seconds_to_start is not None:
                added_ot_text += phrases.GAME_COUNTDOWN.format(
                    convert_seconds_to_duration(remaining_seconds_to_start)
                )
            elif is_played_in_private_chat:
                added_ot_text += phrases.GAME_STARTED

    # Add auto move warning
    if is_turn_based and (
        (game.is_challenger(user_turn) and not challenger_has_finished)
        or (game.is_opponent(user_turn) and not opponent_has_finished)
    ):
        added_ot_text += get_auto_move_warning(add_turn_notification_time=not game.is_global())

    if game.opponent is None:  # Global
        return phrases.GAME_TEXT_WITHOUT_PLAYERS.format(
            game_type.get_name(),
            game_type.get_description(),
            get_belly_formatted(game.wager),
            difficulty_text,
            added_ot_text,
        )

    return phrases.GAME_TEXT.format(
        game_type.get_name(),
        game_type.get_description(),
        mention_markdown_user(game.challenger),
        mention_markdown_user(game.opponent),
        get_belly_formatted(game.wager),
        difficulty_text,
        added_ot_text,
    )


def get_global_time_based_text(game: Game, user: User) -> str:
    """
    Get the text for a time based game in global chat
    :param game: The game
    :param user: The user
    :return: The text
    """

    if not game.is_global():
        return ""

    text_list = []
    is_challenger = game.is_challenger(user)
    is_opponent = not is_challenger
    is_finished = game.is_finished()
    outcome: GameOutcome = game.get_outcome()
    challenger_has_finished = game.challenger_has_finished()

    if is_challenger:
        self_is_still_playing = not is_finished and not challenger_has_finished
        self_start_time = game.global_challenger_start_date
        self_end_time = game.global_challenger_end_date
    else:
        self_is_still_playing = not is_finished
        self_start_time = game.global_opponent_start_date
        self_end_time = game.global_opponent_end_date

    # Current time, if user is still playing
    if self_is_still_playing:
        text_list.append(
            phrases.GAME_GLOBAL_CURRENT_TIME.format(
                get_elapsed_duration(self_start_time, show_full=True)
            )
        )

    # Completion time
    if (is_finished and not (outcome is GameOutcome.CHALLENGER_WON and is_opponent)) or (
        (not is_finished and challenger_has_finished and is_challenger)
    ):
        text_list.append(
            phrases.GAME_GLOBAL_COMPLETION_TIME.format(
                get_remaining_duration(self_end_time, self_start_time, show_full=True)
            )
        )

    challenger_seconds, opponent_seconds = game.get_players_time_seconds()

    # Opponent time
    if (not is_finished and challenger_has_finished and is_opponent) or (
        (is_finished and not (outcome is GameOutcome.CHALLENGER_WON and is_challenger))
    ):
        other_time = challenger_seconds if is_opponent else challenger_seconds
        text_list.append(
            phrases.GAME_GLOBAL_OPPONENT_TIME.format(
                convert_seconds_to_duration(other_time, show_full=True)
            )
        )

    # Remaining time
    if not is_finished and challenger_has_finished and is_opponent:
        # Should never be negative, but better to be safe than sorry
        remaining_time_seconds = max(challenger_seconds - opponent_seconds, 0)

        text_list.append(
            phrases.GAME_GLOBAL_REMAINING_TIME.format(
                convert_seconds_to_duration(remaining_time_seconds, show_full=True)
            )
        )

    return "\n\n" + "\n".join(text_list)


def get_global_text_challenger_finished(
    game: Game, should_add_already_guessed_text: bool = True
) -> str:
    """
    Get the text for a time based game in global mode, when the challenger has finished playing
    :param game: The game
    :param should_add_already_guessed_text: If it should add "You have already guessed correctly" text prefix
    :return: The text
    """

    if game.has_opponent():
        wait_text = phrases.GAME_GLOBAL_GUESS_WAIT_OPPONENT
    else:
        wait_text = phrases.GAME_GLOBAL_PENDING_CHALLENGER

    if not should_add_already_guessed_text:
        return wait_text

    return phrases.GAME_GLOBAL_GUESS_ALREADY_GUESSED.format(
        get_opponent_and_wager_text(game), wait_text
    )


def get_opponent_and_wager_text(game: Game) -> str:
    """
    Get the opponent and wager text
    :param game: The game
    :return: The text
    """

    if game.opponent is None:
        return ""

    return phrases.GAME_OPPONENT_AND_WAGER.format(
        mention_markdown_user(game.opponent), game.get_wager_formatted()
    )


async def delete_game(
    context: ContextTypes.DEFAULT_TYPE,
    update: Update,
    game: Game,
    should_delete_message: bool = True,
    show_timeout_message: bool = False,
) -> None:
    """
    Delete game
    :param context: The context
    :param update: The update
    :param game: The game
    :param should_delete_message: If the message should be deleted
    :param show_timeout_message: If the message should be edited showing timeout
    :return: None
    """

    if should_delete_message and show_timeout_message:
        raise ValueError("should_delete_message and show_timeout_message cannot be both True")

    if show_timeout_message:
        await full_media_send(
            context=context,
            update=update,
            group_chat=game.group_chat,
            caption=phrases.GAME_TIMEOUT,
            edit_message_id=game.message_id,
            edit_only_caption_and_keyboard=True,
            add_delete_button=True,
        )
    elif should_delete_message:
        # Try to delete message
        if should_delete_message:
            await delete_message(
                context=context, group_chat=game.group_chat, message_id=game.message_id
            )

    # Delete game
    game.delete_instance()


async def validate_game(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
    game: Game = None,
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

    status: GameStatus = game.get_status()

    if status is GameStatus.FORCED_END:
        await full_media_send(
            context,
            caption=phrases.GAME_FORCED_END,
            update=update,
            edit_only_caption_and_keyboard=True,
        )
        return None

    if status.is_finished():
        await full_message_or_media_send_or_edit(
            context,
            text=phrases.GAME_ENDED,
            update=update,
            answer_callback=True,
            show_alert=True,
        )
        return None

    if status in (GameStatus.AWAITING_SELECTION, GameStatus.AWAITING_OPPONENT_CONFIRMATION):
        challenger: User = game.challenger
        # Challenger does not have enough bounty
        if not await validate_amount(
            update, context, challenger, game.wager, Env.GAME_MIN_WAGER.get_int()
        ):
            return None

        # Challenger in cooldown
        if (
            challenger.game_cooldown_end_date
            and challenger.game_cooldown_end_date > datetime.now()
        ):
            ot_text = phrases.GAME_CANNOT_INITIATE.format(
                get_remaining_duration(challenger.game_cooldown_end_date)
            )
            await full_media_send(
                context,
                caption=ot_text,
                update=update,
                add_delete_button=True,
                authorized_users=game.get_players(),
                edit_only_caption_and_keyboard=True,
            )

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


async def end_inactive_games(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    End inactive games (games which last interaction was more than N seconds ago)
    :return: None
    """

    # Game
    inactive_games = Game.select().where(
        # Still in progress
        (Game.status == GameStatus.IN_PROGRESS)
        & (
            # Is not global and start date was more than N minutes ago
            (
                (Game.global_challenger_start_date.is_null())
                & (
                    Game.date
                    < (
                        datetime.now()
                        - timedelta(minutes=Env.GAME_INACTIVE_TIME_SINCE_START_MINUTES.get_int())
                    )
                )
            )
            |
            # Is global and opponent has started and start time was more than N minutes ago
            (
                (Game.global_opponent_start_date.is_null(False))
                & (
                    Game.global_opponent_start_date
                    < (
                        datetime.now()
                        - timedelta(minutes=Env.GAME_INACTIVE_TIME_SINCE_START_MINUTES.get_int())
                    )
                )
            )
            |
            # Last interaction was more than N minutes ago
            (
                Game.last_interaction_date
                < (
                    datetime.now()
                    - timedelta(minutes=Env.GAME_INACTIVE_TIME_SINCE_INTERACTION_MINUTES.get_int())
                )
            )
        )
        &
        # It's not a global game. If it is, then it's not considered inactive if an opponent has not yet accepted it
        # and X hours have not passed since the global game was initiated
        ~(
            (Game.global_challenger_start_date.is_null(False))  # It's a global game
            & (Game.opponent.is_null())  # But no opponent has accepted it
            & (
                Game.global_challenger_start_date
                > (datetime.now() - timedelta(hours=Env.GAME_GLOBAL_INACTIVE_HOURS.get_int()))
            )  # N hours have not passed since the global game was initiated
        )
    )

    for game in inactive_games:
        await end_game(game, GameOutcome.NONE, context, is_forced_end=True)
        logging.info(f"Game {game.id} was ended due to inactivity")


async def notify_game_turn(context: ContextTypes.DEFAULT_TYPE, game: Game, game_turn: GameTurn):
    """
    Notify a user that it's their turn

    :param context: The context
    :param game: The game
    :param game_turn: The game turn
    :return: None
    """

    # No notification required for global games
    if game.is_global():
        return

    if game_turn == GameTurn.CHALLENGER:
        user_turn: User = game.challenger
        opponent: User = game.opponent
    else:
        user_turn: User = game.opponent
        opponent: User = game.challenger

    # Fire and forget
    context.application.create_task(
        enqueue_game_turn_notification(context, user_turn, opponent, game)
    )


async def enqueue_game_turn_notification(
    context: ContextTypes.DEFAULT_TYPE, user: User, opponent: User, game: Game
):
    """
    Enqueue a game turn notification. Waits for N time and if the game board stays unchanged,
    sends the notification

    :param context: The context
    :param user: The user
    :param opponent: The opponent
    :param game: The game
    :return: None
    """

    # Wait for N time
    await asyncio.sleep(Env.GAME_TURN_NOTIFICATION_TIME_SECONDS.get_int())

    updated_game = Game.get_by_id(game.id)

    # Check if the game board is still the same
    if updated_game.board == game.board:
        await send_notification(context, user, GameTurnNotification(game, opponent))


async def enqueue_game_timeout(context: ContextTypes.DEFAULT_TYPE, update: Update, game: Game):
    """
    Enqueue a game timeout. Waits for N time and if the opponent doesn't accept,
    the game is deleted
    :param context: The context
    :param update: The update
    :param game: The game
    :return: None
    """

    # Wait for N time
    await asyncio.sleep(Env.GAME_CONFIRMATION_TIMEOUT.get_int())

    try:
        updated_game = Game.get_by_id(game.id)
    except DoesNotExist:
        return  # Game was cancelled

    # Check if the game is still in the same state
    if GameStatus(updated_game.status) == GameStatus.AWAITING_OPPONENT_CONFIRMATION:
        await delete_game(
            context, update, updated_game, should_delete_message=False, show_timeout_message=True
        )


def get_players(game: Game) -> Tuple[User, User]:
    """
    Get the players of a game

    :param game: The game
    :return: The players
    """

    return game.challenger, game.opponent


async def set_user_private_screen(
    user: User, game: Game = None, should_reset: bool = False
) -> None:
    """
    Update the players' private screen
    :param game: The game
    :param user: The user
    :param should_reset: If True, reset the private screen
    :return: None
    """

    if not should_reset and game is None:
        raise ValueError("If should_reset is False, game must be provided")

    if should_reset:
        private_screen_list = None
        private_screen_in_edit_id = None
    else:
        private_screen_list = Screen.PVT_GAME_GUESS_INPUT
        private_screen_in_edit_id = game.id

    # Using update instead of save to avoid overwriting other fields, namely bounty and
    # pending_bounty
    User.update(
        private_screen_list=private_screen_list,
        private_screen_in_edit_id=private_screen_in_edit_id,
    ).where(User.id == user.id).execute()

    return


def get_guess_game_final_image_path(game: Game) -> str:
    """
    Get the path of the final image of a guess game

    :param game: The game
    :return: The path
    """

    json_dict = json.loads(game.board)

    match game.type:
        case GameType.WHOS_WHO:
            return WhosWho(**json_dict).image_path

        case GameType.SHAMBLES:
            shambles: Shambles = Shambles(**json_dict)
            shambles.set_grid_image(highlight_answer=True)

            return shambles.image_path

        case _:
            raise ValueError(f"Game type {game.type} is not a guess game")


def get_guess_game_result_term_text(terminology: Terminology):
    """
    Get the text of the result term of a guess game

    :param terminology: The terminology
    :return: The text
    """

    term_mention = terminology.get_markdown_mention()
    if isinstance(terminology, Character):
        return phrases.GAME_RESULT_CHARACTER.format(term_mention)

    return phrases.GAME_RESULT_TERM.format(term_mention)


async def guess_game_countdown_to_start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    game: Game,
    remaining_seconds: int,
    run_game_function: Callable,
    player: User,
) -> None:
    """
    Countdown to start
    :param update: The update object
    :param context: The context object
    :param game: The game object
    :param remaining_seconds: The remaining time
    :param run_game_function: The function to run when the countdown is over
    :param player: The player who triggered the countdown
    :return: None
    """

    play_deeplink_button = [[get_guess_game_play_deeplink_button(game)]]

    if remaining_seconds <= 0:
        game.status = GameStatus.IN_PROGRESS
        game.save()

        # Edit group message if the game was started in a group
        # In case of global game, it's edited in global_start_challenger
        if game.group_chat is not None and not game.is_global():
            ot_text = get_text(game, False, is_played_in_private_chat=True)
            await full_media_send(
                context,
                caption=ot_text,
                update=update,
                keyboard=play_deeplink_button,
                edit_only_caption_and_keyboard=True,
                edit_message_id=game.message_id,
            )

        # Run game
        await run_game_function(context, game, player)
        return

    # Update message
    try:
        ot_text = get_text(game, False, remaining_seconds_to_start=remaining_seconds)
        await full_media_send(
            context,
            caption=ot_text,
            update=update,
            keyboard=play_deeplink_button,
            saved_media_name=game.get_saved_media_name(),
            ignore_bad_request_exception=True,
        )
    except RetryAfter:
        pass

    # Update every 10 seconds if remaining time is more than 10 seconds, otherwise
    # update every 5 seconds
    if remaining_seconds > 10:
        await asyncio.sleep(10)
        await guess_game_countdown_to_start(
            update, context, game, remaining_seconds - 10, run_game_function, player
        )
    else:
        await asyncio.sleep(5)
        await guess_game_countdown_to_start(
            update, context, game, remaining_seconds - 5, run_game_function, player
        )


async def get_guess_game_users_to_send_message_to(
    game: Game, send_to_user: User, should_send_to_all_players: bool, schedule_next_send: bool
) -> list[User]:
    """
    Get the users to send the image to
    :param game: The game
    :param game: The game object
    :param send_to_user: The user to send the image to
    :param should_send_to_all_players: If the image should be sent to all players
    :param schedule_next_send: If the next send should be scheduled
    :return:
    """

    if not should_send_to_all_players and schedule_next_send and not game.is_global():
        raise ValueError("Cannot schedule next send if not sending to all players")
    if send_to_user is not None and not should_send_to_all_players:
        users: list[User] = [send_to_user]
    else:
        users: list[User] = [game.challenger]
        if game.opponent is not None:
            users.append(game.opponent)

    return users


async def guess_game_validate_answer(
    update: Update, context: ContextTypes.DEFAULT_TYPE, game: Game, user: User
) -> None:
    """
    Validate the answer
    :param update: The update object
    :param context: The context object
    :param game: The game object
    :param user: The user object
    :return: None
    """

    try:
        answer = update.effective_message.text
    except AttributeError:
        return

    terminology = get_terminology_from_game(game)

    if not terminology.name.lower() == answer.lower():
        return

    # End game
    challenger, opponent = get_players(game)
    outcome: GameOutcome = (
        GameOutcome.CHALLENGER_WON if user == challenger else GameOutcome.OPPONENT_WON
    )
    await end_game(game, outcome, context, update=update)
    user.should_update_model = False  # To avoid re-writing bounty
    loser = challenger if user == opponent else opponent

    # Go to game message in group button
    outbound_keyboard: list[list[Keyboard]] = [
        [
            Keyboard(
                text=phrases.PVT_KEY_GO_TO_MESSAGE,
                url=get_message_url(game.message_id, game.group_chat),
            )
        ]
    ]

    term_text_addition = get_guess_game_result_term_text(terminology)
    image_path: str = get_guess_game_final_image_path(game)

    # Send message to winner
    await set_user_private_screen(user, should_reset=True)
    winner_caption: str = (
        phrases.GUESS_GAME_CORRECT_ANSWER.format(term_text_addition)
        + "\n\n"
        + get_outcome_text(True, game.wager)
    )
    await full_media_send(
        context,
        chat_id=user.tg_user_id,
        caption=winner_caption,
        saved_media=SavedMedia(media_type=SavedMediaType.PHOTO, file_name=image_path),
        ignore_forbidden_exception=True,
        keyboard=outbound_keyboard,
    )

    # Send message to loser
    await set_user_private_screen(loser, should_reset=True)
    loser_caption: str = (
        phrases.GUESS_GAME_OPPONENT_CORRECT_ANSWER.format(term_text_addition)
        + "\n\n"
        + get_outcome_text(True, game.wager)
    )
    await full_media_send(
        context,
        chat_id=loser.tg_user_id,
        caption=loser_caption,
        saved_media=SavedMedia(media_type=SavedMediaType.PHOTO, file_name=image_path),
        ignore_forbidden_exception=True,
        keyboard=outbound_keyboard,
    )

    # Update group message
    ot_text = get_text(game, True, game_outcome=outcome, terminology=terminology)
    group_chat: GroupChat = game.group_chat
    await full_media_send(
        context,
        caption=ot_text,
        group_chat=group_chat,
        edit_message_id=game.message_id,
        edit_only_caption_and_keyboard=True,
    )


def get_terminology_from_game(game: Game) -> Terminology:
    """
    Get the terminology from the game
    :param game: The game
    :return: The terminology
    """

    # Parse the JSON string and create a Terminology object
    json_dict = json.loads(game.board)
    if "terminology" in json_dict:
        term_dict = json_dict.pop("terminology")
        terminology: Terminology = Terminology(**term_dict)
    elif "character" in json_dict:
        char_dict = json_dict.pop("character")
        terminology: Terminology = Character(**char_dict)
    else:
        raise ValueError("No terminology or character in JSON string")

    return terminology


def get_guess_game_play_deeplink_button(game: Game) -> Keyboard:
    """
    Get the play button for the game
    :param game: The game
    :return: The keyboard
    """

    info: dict = {ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: game.id}
    return Keyboard(
        phrases.GRP_KEY_GAME_PLAY, info, screen=Screen.PVT_GAME_GUESS_INPUT, is_deeplink=True
    )


def save_game(
    game: Game, board: str, is_opponent_board: bool = False, hint_was_issued: bool = False
) -> None:
    """
    Save the game
    :param game: The game
    :param board: The board
    :param is_opponent_board: If it's an opponent board
    :param hint_was_issued: If the hint was issued
    :return: None
    """

    if game.is_global() and is_opponent_board:
        game.opponent_board = board
        if hint_was_issued:
            game.last_hint_opponent_date = datetime.now()
    else:
        game.board = board
        if hint_was_issued:
            game.last_hint_date = datetime.now()

    game.last_interaction_date = datetime.now()
    game.save()


async def end_text_based_game(
    context: ContextTypes.DEFAULT_TYPE,
    game: Game,
    outcome: GameOutcome,
    winner: User,
    winner_text: str,
    loser: User,
    loser_text: str,
    group_text: str = None,
) -> None:
    """
    End a text based game
    :param context: The context
    :param game: The game
    :param outcome: The outcome
    :param winner: The winner
    :param winner_text: The winner text
    :param loser: The loser
    :param loser_text: The loser text
    :param group_text: The group text
    """

    terminology: Terminology = get_terminology_from_game(game)
    term_text_addition = get_guess_game_result_term_text(terminology)

    # If winner or loser text doesn't end with 3 new lines (just enough to add 3)
    if not winner_text.endswith("\n\n\n"):
        # Check how many new lines are missing at the end
        missing_new_lines = 3 - winner_text.count("\n", -3)
        winner_text += "\n" * missing_new_lines
        loser_text += "\n" * missing_new_lines

    # Add terminology text
    winner_text += term_text_addition
    loser_text += term_text_addition

    outbound_keyboard: list[list[Keyboard]] = []

    if not game.is_global():
        # Go to game message in group button
        outbound_keyboard = [
            [
                Keyboard(
                    text=phrases.PVT_KEY_GO_TO_MESSAGE,
                    url=get_message_url(game.message_id, game.group_chat),
                )
            ]
        ]

    # Send message to winner
    await set_user_private_screen(winner, should_reset=True)
    context.application.create_task(
        full_message_send(
            context, winner_text, chat_id=winner.tg_user_id, keyboard=outbound_keyboard
        )
    )

    # If global, we can stop here. No message sent to loser since the notification triggered in end_game will handle it,
    # same for group message
    if game.is_global():
        return

    # Send message to loser
    await set_user_private_screen(loser, should_reset=True)
    context.application.create_task(
        full_message_send(
            context, loser_text, chat_id=loser.tg_user_id, keyboard=outbound_keyboard
        )
    )

    # Update group message
    if game.group_chat is not None:
        if group_text is None:
            group_text = get_text(game, True, game_outcome=outcome, terminology=terminology)

        group_chat: GroupChat = game.group_chat
        await full_media_send(
            context,
            caption=group_text,
            group_chat=group_chat,
            edit_message_id=game.message_id,
            edit_only_caption_and_keyboard=True,
        )


async def collect_game_wagers_and_set_in_progress(
    update: Update,
    game: Game,
    challenger: User = None,
    opponent: User = None,
    should_remove_bounty_challenger: bool = True,
    should_save_challenger: bool = True,
    should_remove_bounty_opponent: bool = True,
    should_save_opponent: bool = True,
    should_save_game: bool = True,
    should_set_cooldown_challenger: bool = True,
    should_set_global_cooldown_opponent: bool = False,
) -> None:
    """
    Start the game, removing bounty from challenger and opponent
    :param update: The update object
    :param game: The game object
    :param challenger: The challenger
    :param opponent: The opponent
    :param should_remove_bounty_challenger: If the bounty should be removed from the challenger
    :param should_save_challenger: If the challenger should be saved
    :param should_remove_bounty_opponent: If the bounty should be removed from the opponent
    :param should_save_opponent: If the opponent should be saved
    :param should_save_game: If the game should be saved
    :param should_set_cooldown_challenger: If the game cooldown should be set for the challenger
    :param should_set_global_cooldown_opponent: If the global cooldown should be set for the opponent
    :return: None
    """
    if challenger is None:
        if should_remove_bounty_challenger:
            raise ValueError(
                "Challenger must be provided if should_remove_bounty_challenger is True"
            )

        if should_set_cooldown_challenger:
            raise ValueError(
                "Challenger must be provided if should_set_cooldown_challenger is True"
            )

    if opponent is None:
        if should_remove_bounty_opponent:
            raise ValueError("Opponent must be provided if should_remove_bounty_opponent is True")

        if should_set_global_cooldown_opponent:
            raise ValueError(
                "Opponent must be provided if should_set_global_cooldown_opponent is True"
            )

    if should_remove_bounty_opponent:
        await add_or_remove_bounty(
            opponent,
            game.wager,
            add=False,
            update=update,
            should_affect_pending_bounty=True,
            should_save=should_save_opponent,
        )
    if should_set_global_cooldown_opponent:
        opponent.should_set_global_cooldown_opponent = get_ability_adjusted_datetime(
            opponent,
            DevilFruitAbilityType.GAME_GLOBAL_ACCEPT_COOLDOWN_DURATION,
            Env.GAME_GLOBAL_ACCEPT_COOLDOWN_DURATION.get_int(),
        )

    if should_remove_bounty_challenger:
        await add_or_remove_bounty(
            challenger,
            game.wager,
            add=False,
            should_affect_pending_bounty=True,
            update=update,
            should_save=should_save_challenger,
        )
    if should_set_cooldown_challenger:
        challenger.game_cooldown_end_date = get_ability_adjusted_datetime(
            challenger,
            DevilFruitAbilityType.GAME_COOLDOWN_DURATION,
            Env.GAME_COOLDOWN_DURATION.get_int(),
        )

    # Double wager if opponent is provided
    if opponent is not None:
        game.wager *= 2
        game.opponent = opponent

    game.status = GameStatus.IN_PROGRESS

    if should_save_game:
        game.save()


def get_global_game_item_text_deeplink(game: Game, user: User) -> str:
    """
    Get global game item text with deeplink
    :param game: The game
    :param user: The user
    :return: The text
    """
    self_emoji = Emoji.USER if game.is_challenger(user) else ""

    return phrases.GAME_GLOBAL_ITEM_DEEPLINK.format(
        self_emoji,
        game.get_type().get_name(),
        get_belly_formatted(game.wager),
        get_deeplink(
            info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: game.id},
            screen=Screen.PVT_GAME_GLOBAL_START_OPPONENT,
        ),
    )


def get_global_challenges_section_text(
    user: User, max_items_per_category: int = c.STANDARD_LIST_SIZE
) -> str:
    """
    Get global challenges section text
    :param user: The user
    :param max_items_per_category: Max items per category
    :return: Global challenges section
    """

    global_challenges = Game.get_global_games()
    global_challenges_text = ""

    if len(global_challenges) == 0:
        return ""

    for i, game in enumerate(global_challenges):
        # Limit max visible items
        if i == max_items_per_category:
            url = get_deeplink(screen=Screen.PVT_GAME_GLOBAL_LIST)
            global_challenges_text += phrases.VIEW_ALL_WITH_EMOJI.format(url)
            break

        global_challenges_text += phrases.DAILY_REWARD_GLOBAL_CHALLENGE_ITEM.format(
            get_global_game_item_text_deeplink(game, user)
        )

    return phrases.DAILY_REWARD_GLOBAL_CHALLENGE.format(global_challenges_text)


def get_auto_move_seconds(add_turn_notification_time: bool = False) -> int:
    """
    Get auto move seconds
    :param add_turn_notification_time: If turn notification time should be added
    :return: The seconds
    """

    seconds = Env.GAME_TURN_AUTO_MOVE_TIME_SECONDS.get_int()

    # In case it's played in a group, auto move countdown should start from when the user is notified of their turn
    if add_turn_notification_time:
        seconds += Env.GAME_TURN_NOTIFICATION_TIME_SECONDS.get_int()

    return seconds


def get_auto_move_warning(add_turn_notification_time: bool = False) -> str:
    """
    Get auto move warning
    :param add_turn_notification_time: If turn notification time should be added
    :return: The warning
    """

    return phrases.GAME_AUTO_MOVE_WARNING.format(
        convert_seconds_to_duration(
            get_auto_move_seconds(add_turn_notification_time=add_turn_notification_time)
        )
    )


async def enqueue_auto_move(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    game: Game,
    user: User,
    auto_move_function: Callable,
    message_id: int,
    extra_wait_time: int = 0,
) -> None:
    """
    Enqueue auto move
    :param update: The update
    :param context: The context
    :param game: The game
    :param user: The user
    :param auto_move_function: The auto move function
    :param message_id: Identifier of the message that will be updated in auto move
    :param extra_wait_time: Extra time to wait
    :return: None
    """
    await asyncio.sleep(get_auto_move_seconds(not game.is_global()))

    if extra_wait_time > 0:
        await asyncio.sleep(extra_wait_time)

    updated_game = Game.get_by_id(game.id)

    # Game already ended
    if game.is_finished():
        return

    await auto_move_function(update, context, updated_game, user, message_id, game)


async def edit_other_player_message(
    context: ContextTypes.DEFAULT_TYPE,
    game: Game,
    player: User,
    sent_message_id: int,
    challenger_text: str,
    opponent_text: str,
    outbound_keyboard: list[list[Keyboard]],
):
    """
    Edit the other player message
    :param context: The context object
    :param game: The game object
    :param player: The player object
    :param sent_message_id: The id of the message that was just sent to the player
    :param challenger_text: The challenger text
    :param opponent_text: The opponent text
    :param outbound_keyboard: The outbound keyboard
    :return: None
    """
    if game.is_challenger(player):
        game.challenger_message_id = sent_message_id
        other_player: User = game.opponent
        other_player_message_id = game.opponent_message_id
        other_player_text = opponent_text
    else:
        game.opponent_message_id = sent_message_id
        other_player: User = game.challenger
        other_player_message_id = game.challenger_message_id
        other_player_text = challenger_text

    if other_player is not None:
        await full_media_send(
            context,
            caption=other_player_text,
            keyboard=outbound_keyboard,
            authorized_users=game.get_players(),
            chat_id=other_player.tg_user_id,
            edit_message_id=other_player_message_id,
            ignore_bad_request_exception=True,
            ignore_forbidden_exception=True,
            edit_only_caption_and_keyboard=True,
        )

    game.save()


async def timeout_opponent_guess_game(context: ContextTypes.DEFAULT_TYPE, game: Game) -> bool:
    """
    Check if opponent has timed out for guessing. If so, end game giving challenger the win.
    In case this method returns False, every caller should exit, since it handles everything
    :param context: The context
    :param game: The game
    :return: Whether the opponent has timed out
    """

    if not game.is_global():
        return False

    # Game already ended, no further action needed
    if game.is_finished():
        return True

    if game.global_challenger_end_date is None:  # Challenger has not yet finished
        return False

    if game.global_opponent_start_date is None:  # Opponent has not yet started
        return False

    challenger_seconds, opponent_seconds = game.get_players_time_seconds()
    if challenger_seconds > opponent_seconds:
        return False

    # End game
    await end_game(game, GameOutcome.CHALLENGER_WON, context)

    return True


async def enqueue_timeout_opponent_guess_game(
    context: ContextTypes.DEFAULT_TYPE, game: Game
) -> None:
    """
    Enqueue timeout opponent guess game. If the game is not finished and timeout is not yet enqueued, waits till as much
    time has passed as the challenger took to guess, and if the game is still ongoing, it means the opponent has lost
    :param context: The context
    :param game: The game
    :return: None
    """

    if not game.is_global():
        return

    if game.is_finished():
        return

    # Game without opponent yet
    if not game.has_opponent():
        return

    # Challenger has not yet finished
    if game.global_challenger_end_date is None:
        return

    challenger_seconds, opponent_seconds = game.get_players_time_seconds()
    remaining_seconds = challenger_seconds - opponent_seconds

    if remaining_seconds <= 0:  # Opponent has already taken more time, how did it arrive here??
        await timeout_opponent_guess_game(context, game)
        return

    # Already enqueued a timeout, do not enqueue more
    try:
        get_bot_context_data(
            context,
            ContextDataKey.GAME_OPPONENT_TIMEOUT,
            inner_key=str(game.id),
            tolerate_key_exception=False,
        )
        # Key exists, no error, so timeout already enqueued
        return
    except KeyError:
        set_bot_context_data(
            context, ContextDataKey.GAME_OPPONENT_TIMEOUT, game.id, inner_key=str(game.id)
        )

    # Wait for the remaining time, then try ending if game is not yet finished
    await asyncio.sleep(remaining_seconds)
    updated_game = Game.get_by_id(game.id)

    # Game already ended
    if game.is_finished():
        return

    await timeout_opponent_guess_game(context, updated_game)


async def end_global_guess_game_challenger(context: ContextTypes.DEFAULT_TYPE, game: Game) -> None:
    """
    End the global guess game after a challenger has correctly guessed
    :param context: The context object
    :param game: The game object
    """

    # Save challenger end time
    game.global_challenger_end_date = datetime.now()
    game.save()

    # Try enqueuing opponent timeout
    context.application.create_task(enqueue_timeout_opponent_guess_game(context, game))


async def challenger_has_finished_or_opponent_timeout(
    context: ContextTypes.DEFAULT_TYPE, game: Game, user: User
) -> bool:
    """
    Check if the challenger has finished or the opponent has timed out. If returns true, exit immediately since all
    eventual messages/triggers are done internally
    :param context: The context
    :param game: The game
    :param user: The user
    :return: True if the challenger has finished or the opponent has timed out, False otherwise.
    """
    # Challenger still playing, no need to check timeout
    if not game.challenger_has_finished():
        return False

    # Is challenger, and they have already guessed, so they should wait for the opponent to finish
    if game.is_challenger(user):
        await full_message_send(
            context, get_global_text_challenger_finished(game), chat_id=user.tg_user_id
        )

        # Try checking if opponent already in timeout
        await timeout_opponent_guess_game(context, game)
        return True

    # On opponent input, always try timeout in case the previously started thread to auto timeout has failed
    if await timeout_opponent_guess_game(context, game):
        return True

    return False


async def restart_hint_thread_if_down_all_games(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Restart the hint thread if it's down for all games
    :param context: The context object
    :return: None
    """
    from src.chat.common.screens.screen_game_manage import restart_hint_thread_if_down

    # Get all guess games in progress
    games = Game.select().where(
        (Game.status == GameStatus.IN_PROGRESS) & (Game.type.in_(GameType.get_guess_based_list()))
    )

    for game in games:
        context.application.create_task(restart_hint_thread_if_down(context, game))


def get_generic_boards_for_guess_game(
    game: Game, max_len: int = None, only_letters: bool = False
) -> [GameBoard, GameBoard]:
    """
    Get the boards for a guess game
    :param game: The game
    :param max_len: The maximum length of the terminology to generate
    :param only_letters: If True, only generate letters, if False, generate all characters
    :return: The boards
    """

    match game.get_type():
        case GameType.PUNK_RECORDS:
            board_class = PunkRecords
            terminology_type = Character

        case GameType.SHAMBLES:
            board_class = Shambles
            terminology_type = Terminology

        case GameType.WHOS_WHO:
            board_class = WhosWho
            terminology_type = Character

        case _:
            raise ValueError(f"Unsupported game type: {game.get_type()}")

    # Create if not existing board
    if game.board is None:
        if terminology_type == Character:
            random_terminology: Character = SupabaseRest.get_random_character(
                game.get_difficulty()
            )
        else:
            random_terminology: Terminology = SupabaseRest.get_random_terminology(
                max_len=max_len, only_letters=only_letters
            )

        board = board_class(random_terminology)
        save_game(game, board.get_as_json_string(), hint_was_issued=True)

        if game.is_global():
            save_game(game, board.get_as_json_string(), is_opponent_board=True)

        return board, board

    # Parse the JSON string and create a Terminology object
    json_dict = json.loads(game.board)
    opponent_json_dict = json.loads(game.opponent_board) if game.is_global() else None
    opponent_board = None

    if terminology_type == Character:
        char_dict = json_dict.pop("character")
        char: Character = Character(**char_dict)
        board = board_class(character=char, **json_dict)

        if opponent_json_dict:
            opponent_json_dict.pop("character")
            opponent_board = board_class(character=char, **opponent_json_dict)
    else:
        term_dict = json_dict.pop("terminology")
        term: Terminology = Terminology(**term_dict)
        board = board_class(terminology=term, **json_dict)

        if opponent_json_dict:
            opponent_json_dict.pop("terminology")
            opponent_board = board_class(terminology=term, **opponent_json_dict)

    return board, opponent_board


def get_player_board(game: Game, user: User) -> PunkRecords | Shambles | WhosWho:
    """
    Get the player board
    :param game: The game object
    :param user: The user object
    :return: The board
    """

    challenger_board, opponent_board = get_generic_boards_for_guess_game(game)
    return challenger_board if game.is_challenger(user) or not game.is_global() else opponent_board


async def should_proceed_after_hint_sleep(
    context: ContextTypes.DEFAULT_TYPE, game: Game, user: User
) -> bool:
    """
    Should proceed after hint sleep?
    :param context: The context
    :param game: The game
    :param user: The user
    :return: True if the hint sleep should be proceeded, False otherwise
    """
    if game.is_finished():
        return False

    if game.is_opponent(user) and await timeout_opponent_guess_game(context, game):
        return False

    # Challenger is playing and they have already guessed
    if game.is_challenger(user) and game.challenger_has_finished():
        return False

    return True


def get_winner_loser_text(
    game: Game, specific_winner_text: str, specific_loser_text: str = None
) -> [str, str]:
    """
    Get the winner and loser text
    :param game: The game
    :param specific_winner_text: The specific winner text
    :param specific_loser_text: The specific loser text. If not set, will use the specific_winner_text
    :return: The winner and loser text
    """

    if specific_loser_text is None:
        specific_loser_text = specific_winner_text

    winner_text = (
        phrases.GUESS_GAME_CORRECT_ANSWER.format(specific_winner_text)
        + "\n\n"
        + get_outcome_text(True, game.wager)
    )

    loser_text: str = (
        phrases.GUESS_GAME_OPPONENT_CORRECT_ANSWER.format(specific_loser_text)
        + "\n\n"
        + get_outcome_text(True, game.wager)
    )

    return winner_text, loser_text
