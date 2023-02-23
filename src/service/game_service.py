import asyncio
import json
from typing import Tuple, Callable

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
from resources import phrases as phrases
from src.model.Game import Game
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.Notification import GameTurnNotification
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.SavedMedia import SavedMedia
from src.model.enums.SavedMediaType import SavedMediaType
from src.model.enums.Screen import Screen
from src.model.error.GroupChatError import GroupChatError, GroupChatException
from src.model.game.GameOutcome import GameOutcome
from src.model.game.GameTurn import GameTurn
from src.model.game.GameType import GameType
from src.model.game.shambles.Shambles import Shambles
from src.model.game.whoswho.WhosWho import WhosWho
from src.model.pojo.Keyboard import Keyboard
from src.model.wiki.Character import Character
from src.model.wiki.Terminology import Terminology
from src.service.bounty_service import get_belly_formatted, add_bounty
from src.service.cron_service import convert_seconds_to_time
from src.service.message_service import mention_markdown_user, delete_message, full_media_send, get_message_url
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


def get_text(game: Game, is_finished: bool, game_outcome: GameOutcome = None, user_turn: User = None,
             is_turn_based: bool = True, terminology: Terminology = None, remaining_seconds_to_start: int = None,
             is_played_in_private_chat: bool = False, text_to_add_before_footer: str = None) -> str:
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
    :return: The text
    """

    added_ot_text = ""

    if text_to_add_before_footer is not None:
        added_ot_text += text_to_add_before_footer

    if is_finished and game_outcome is not None and game_outcome is not GameOutcome.NONE:
        if not is_turn_based and terminology is not None:
            added_ot_text += get_guess_game_result_term_text(terminology) + '\n\n'

        if game_outcome is GameOutcome.CHALLENGER_WON:
            added_ot_text += phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.challenger))
        elif game_outcome is GameOutcome.OPPONENT_WON:
            added_ot_text += phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.opponent))
        else:
            added_ot_text += phrases.GAME_RESULT_DRAW
    else:
        if is_turn_based:
            added_ot_text += phrases.GAME_TURN.format(mention_markdown_user(user_turn))
        else:
            if remaining_seconds_to_start is not None:
                added_ot_text += phrases.GAME_COUNTDOWN.format(convert_seconds_to_time(remaining_seconds_to_start))
            elif is_played_in_private_chat:
                added_ot_text += phrases.GAME_STARTED

    game_type: GameType = GameType(game.type)
    return phrases.GAME_TEXT.format(game_type.get_name(),
                                    game_type.get_description(),
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
        await full_media_send(context=context, group_chat=game.group_chat, caption=phrases.GAME_TIMEOUT,
                              edit_message_id=game.message_id, edit_only_caption_and_keyboard=True)
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
        await full_media_send(context, caption=phrases.GAME_FORCED_END, update=update,
                              edit_only_caption_and_keyboard=True)
        return None

    if GameStatus(game.status).is_finished():
        await full_media_send(context, caption=phrases.GAME_ENDED, update=update, answer_callback=True, show_alert=True,
                              edit_only_caption_and_keyboard=True)
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


def get_players(game: Game) -> Tuple[User, User]:
    """
    Get the players of a game

    :param game: The game
    :return: The players
    """

    return game.challenger, game.opponent


async def set_user_private_screen(user: User, game: Game = None, should_reset: bool = False) -> None:
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
        user.private_screen_list = None
        user.private_screen_in_edit_id = None
    else:
        user.private_screen_list = Screen.PVT_GAME_GUESS_INPUT
        user.private_screen_in_edit_id = game.id

    user.save()
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
            raise ValueError(f"Game type {game.game_type} is not a guess game")


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


async def guess_game_countdown_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE, game: Game,
                                        remaining_seconds: int, run_game_function: Callable,
                                        is_played_in_private_chat: bool = True) -> None:
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

    play_deeplink_button = [[get_guess_game_play_deeplink_button(game)]] if is_played_in_private_chat else None

    if remaining_seconds <= 0:
        game.status = GameStatus.IN_PROGRESS
        game.save()

        # Edit group message if the game is played in private chat
        if is_played_in_private_chat:
            ot_text = get_text(game, False, is_turn_based=False, is_played_in_private_chat=True)
            await full_media_send(context, caption=ot_text, update=update, keyboard=play_deeplink_button,
                                  edit_only_caption_and_keyboard=True)

        # Run game
        await run_game_function(context, game)
        return

    # Update message
    ot_text = get_text(game, False, is_turn_based=False, remaining_seconds_to_start=remaining_seconds)
    await full_media_send(context, caption=ot_text, update=update, keyboard=play_deeplink_button,
                          saved_media_name=game.get_saved_media_name(), ignore_bad_request_exception=True)

    # Update every 10 seconds if remaining time is more than 10 seconds, otherwise update every second
    if remaining_seconds > 10:
        await asyncio.sleep(10)
        await guess_game_countdown_to_start(update, context, game, remaining_seconds - 10, run_game_function,
                                            is_played_in_private_chat=is_played_in_private_chat)
    else:
        await asyncio.sleep(1)
        await guess_game_countdown_to_start(update, context, game, remaining_seconds - 1, run_game_function,
                                            is_played_in_private_chat=is_played_in_private_chat)


async def get_guess_game_users_to_send_image_to(game: Game, send_to_user: User, should_send_to_all_players: bool,
                                                schedule_next_send: bool) -> list[User]:
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
        raise ValueError('Cannot send to user and all players')
    if not should_send_to_all_players and schedule_next_send:
        raise ValueError('Cannot schedule next send if not sending to all players')
    if send_to_user is not None:
        users: list[User] = [send_to_user]
    else:
        challenger: User = game.challenger
        opponent: User = game.opponent
        users: list[User] = [challenger, opponent]

    return users


async def guess_game_validate_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, game: Game, user: User
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

    if not terminology.name.lower() == answer.lower():
        return

    # End game
    challenger, opponent = get_players(game)
    outcome: GameOutcome = GameOutcome.CHALLENGER_WON if user == challenger else GameOutcome.OPPONENT_WON
    await end_game(game, outcome)
    user.should_update_model = False  # To avoid re-writing bounty
    loser = challenger if user == opponent else opponent

    # Go to game message in group button
    outbound_keyboard: list[list[Keyboard]] = [[Keyboard(text=phrases.PVT_KEY_GO_TO_MESSAGE,
                                                         url=get_message_url(game.group_chat, game.message_id))]]

    term_text_addition = get_guess_game_result_term_text(terminology)
    image_path: str = get_guess_game_final_image_path(game)

    # Send message to winner
    await set_user_private_screen(user, should_reset=True)
    winner_caption: str = phrases.GUESS_GAME_CORRECT_ANSWER.format(term_text_addition)
    await full_media_send(context, chat_id=user.tg_user_id, caption=winner_caption,
                          saved_media=SavedMedia(media_type=SavedMediaType.PHOTO, file_name=image_path),
                          ignore_forbidden_exception=True, keyboard=outbound_keyboard)

    # Send message to loser
    await set_user_private_screen(loser, should_reset=True)
    loser_caption: str = phrases.GUESS_GAME_OPPONENT_CORRECT_ANSWER.format(term_text_addition)
    await full_media_send(context, chat_id=loser.tg_user_id, caption=loser_caption,
                          saved_media=SavedMedia(media_type=SavedMediaType.PHOTO, file_name=image_path),
                          ignore_forbidden_exception=True, keyboard=outbound_keyboard)

    # Update group message
    ot_text = get_text(game, True, game_outcome=outcome, is_turn_based=False, terminology=terminology)
    group_chat: GroupChat = game.group_chat
    await full_media_send(context, caption=ot_text, group_chat=group_chat, edit_message_id=game.message_id,
                          edit_only_caption_and_keyboard=True)


def get_guess_game_play_deeplink_button(game: Game) -> Keyboard:
    """
    Get the play button for the game
    :param game: The game
    :return: The keyboard
    """

    info: dict = {ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: game.id}
    return Keyboard(phrases.GRP_KEY_GAME_PLAY, info, screen=Screen.PVT_GAME_GUESS_INPUT,
                    is_deeplink=True)


def save_game(game: Game, board: str) -> None:
    """
    Save the game
    :param game: The game
    :param board: The board
    :return: None
    """

    game.board = board
    game.save()
