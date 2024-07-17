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
from src.model.game.GameOutcome import GameOutcome
from src.model.game.GameTurn import GameTurn
from src.model.game.GameType import GameType
from src.model.game.shambles.Shambles import Shambles
from src.model.game.whoswho.WhosWho import WhosWho
from src.model.pojo.Keyboard import Keyboard
from src.model.wiki.Character import Character
from src.model.wiki.Terminology import Terminology
from src.service.bounty_service import add_or_remove_bounty, validate_amount
from src.service.date_service import convert_seconds_to_duration, get_remaining_duration
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

    challenger.save()
    if opponent is not None:
        opponent.save()
    game.save()

    if not is_forced_end:
        if send_outcome_to_user:
            await send_notification(
                context, send_outcome_to_user, GameOutcomeNotification(game, send_outcome_to_user)
            )

        # Edit message in group, if global
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
    is_turn_based: bool = True,
    terminology: Terminology = None,
    remaining_seconds_to_start: int = None,
    is_played_in_private_chat: bool = False,
    text_to_add_before_footer: str = None,
    is_for_group_global: bool = False,
) -> str:
    """
    Get the text
    :param game: The game object
    :param is_finished: Is the game finished
    :param game_outcome: The game outcome
    :param user_turn: The user turn
    :param is_turn_based: Is the game turn based
    :param terminology: The character, in case of Who's Who
    :param remaining_seconds_to_start: The remaining seconds to start
    :param is_played_in_private_chat: Is the game played in private chat
    :param text_to_add_before_footer: The text to add before the footer
        :param is_for_group_global: If the text is for a group and the game is global
    :return: The text
    """

    added_ot_text = ""
    difficulty_text = ""

    game_type: GameType = game.get_type()
    if game_type.has_difficulty_level():
        difficulty_text = phrases.GAME_DIFFICULTY.format(game.get_difficulty().get_name())

    if text_to_add_before_footer is not None:
        added_ot_text += text_to_add_before_footer

    if is_finished and game_outcome is not None and game_outcome is not GameOutcome.NONE:
        if not is_turn_based and terminology is not None:
            added_ot_text += get_guess_game_result_term_text(terminology) + "\n\n"

        if game_outcome is GameOutcome.CHALLENGER_WON:
            added_ot_text += phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.challenger))
        elif game_outcome is GameOutcome.OPPONENT_WON:
            added_ot_text += phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.opponent))
        else:
            added_ot_text += phrases.GAME_RESULT_DRAW
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

    return phrases.GAME_TEXT.format(
        game_type.get_name(),
        game_type.get_description(),
        mention_markdown_user(game.challenger),
        mention_markdown_user(game.opponent),
        get_belly_formatted(game.wager),
        difficulty_text,
        added_ot_text,
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
    is_played_in_private_chat: bool = True,
) -> None:
    """
    Countdown to start
    :param update: The update object
    :param context: The context object
    :param game: The game object
    :param remaining_seconds: The remaining time
    :param run_game_function: The function to run when the countdown is over
    :param is_played_in_private_chat: If True, the game is played in private chat
    :return: None
    """

    play_deeplink_button = (
        [[get_guess_game_play_deeplink_button(game)]] if is_played_in_private_chat else None
    )

    if remaining_seconds <= 0:
        game.status = GameStatus.IN_PROGRESS
        game.save()

        # Edit group message if the game is played in private chat
        if is_played_in_private_chat:
            ot_text = get_text(game, False, is_turn_based=False, is_played_in_private_chat=True)
            await full_media_send(
                context,
                caption=ot_text,
                update=update,
                keyboard=play_deeplink_button,
                edit_only_caption_and_keyboard=True,
            )

        # Run game
        await run_game_function(context, game)
        return

    # Update message
    try:
        ot_text = get_text(
            game, False, is_turn_based=False, remaining_seconds_to_start=remaining_seconds
        )
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
            update,
            context,
            game,
            remaining_seconds - 10,
            run_game_function,
            is_played_in_private_chat=is_played_in_private_chat,
        )
    else:
        await asyncio.sleep(5)
        await guess_game_countdown_to_start(
            update,
            context,
            game,
            remaining_seconds - 5,
            run_game_function,
            is_played_in_private_chat=is_played_in_private_chat,
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

    if send_to_user is not None and should_send_to_all_players:
        raise ValueError("Cannot send to user and all players")
    if not should_send_to_all_players and schedule_next_send:
        raise ValueError("Cannot schedule next send if not sending to all players")
    if send_to_user is not None:
        users: list[User] = [send_to_user]
    else:
        challenger: User = game.challenger
        opponent: User = game.opponent
        users: list[User] = [challenger, opponent]

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

    terminology = await get_terminology_from_game(game)

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
    winner_caption: str = phrases.GUESS_GAME_CORRECT_ANSWER.format(term_text_addition)
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
    loser_caption: str = phrases.GUESS_GAME_OPPONENT_CORRECT_ANSWER.format(term_text_addition)
    await full_media_send(
        context,
        chat_id=loser.tg_user_id,
        caption=loser_caption,
        saved_media=SavedMedia(media_type=SavedMediaType.PHOTO, file_name=image_path),
        ignore_forbidden_exception=True,
        keyboard=outbound_keyboard,
    )

    # Update group message
    ot_text = get_text(
        game, True, game_outcome=outcome, is_turn_based=False, terminology=terminology
    )
    group_chat: GroupChat = game.group_chat
    await full_media_send(
        context,
        caption=ot_text,
        group_chat=group_chat,
        edit_message_id=game.message_id,
        edit_only_caption_and_keyboard=True,
    )


async def get_terminology_from_game(game: Game) -> Terminology:
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


def save_game(game: Game, board: str) -> None:
    """
    Save the game
    :param game: The game
    :param board: The board
    :return: None
    """

    game.board = board
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

    terminology: Terminology = await get_terminology_from_game(game)
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

    # Go to game message in group button
    outbound_keyboard: list[list[Keyboard]] = [
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

    # Send message to loser
    await set_user_private_screen(loser, should_reset=True)
    context.application.create_task(
        full_message_send(
            context, loser_text, chat_id=loser.tg_user_id, keyboard=outbound_keyboard
        )
    )

    # Update group message
    if group_text is None:
        group_text = get_text(
            game, True, game_outcome=outcome, is_turn_based=False, terminology=terminology
        )

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
    extra_wait_time: int = 0,
) -> None:
    """
    Enqueue auto move
    :param update: The update
    :param context: The context
    :param game: The game
    :param user: The user
    :param auto_move_function: The auto move function
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

    await auto_move_function(update, context, updated_game, user)
