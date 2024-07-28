import asyncio
import json

from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Game import Game
from src.model.User import User
from src.model.enums.SavedMedia import SavedMedia
from src.model.enums.SavedMediaType import SavedMediaType
from src.model.game.whoswho.WhosWho import WhosWho
from src.model.wiki.Character import Character
from src.model.wiki.SupabaseRest import SupabaseRest
from src.service.game_service import (
    set_user_private_screen,
    save_game,
    get_player_board,
    get_guess_game_users_to_send_message_to,
    should_proceed_after_hint_sleep,
    get_global_time_based_text,
)
from src.service.message_service import full_media_send


def get_board(game: Game) -> WhosWho:
    """
    Get the board
    :param game: The game object
    :return: The board
    """

    # Create board
    if game.board is None:
        random_character: Character = SupabaseRest.get_random_character(game.get_difficulty())
        whos_who = WhosWho(random_character)
        save_game(game, whos_who.get_as_json_string())
        return whos_who

    # Parse the JSON string and create a Character object
    json_dict = json.loads(game.board)
    char_dict = json_dict.pop("character")
    char: Character = Character(**char_dict)

    # Create a WhosWho object with attribute unpacking
    return WhosWho(character=char, **json_dict)


async def run_game(
    context: ContextTypes.DEFAULT_TYPE,
    game: Game,
    user: User,
    should_send_to_all_players: bool = True,
    schedule_next_send: bool = True,
    hint_wait_seconds: int = None,
) -> None:
    """
    Send the blurred image
    :param context: The context object
    :param game: The game object
    :param user: The user to send the image to
    :param should_send_to_all_players: If the image should be sent to all players
    :param schedule_next_send: If the next send should be scheduled
    :param hint_wait_seconds: How many seconds to wait before issuing next hint. If none, the game default is used
    :return: None
    """

    hint_wait_seconds = (
        hint_wait_seconds if hint_wait_seconds is not None else game.get_seconds_for_every_hint()
    )

    users = await get_guess_game_users_to_send_message_to(
        game,
        user,
        (should_send_to_all_players and not game.is_global()),
        schedule_next_send,
    )

    # Get the board
    board: WhosWho = get_player_board(game, user)

    # Send the image
    saved_media: SavedMedia = SavedMedia(
        media_type=SavedMediaType.PHOTO, file_name=board.latest_blurred_image
    )
    caption = phrases.GUESS_CHARACTER_GAME_INPUT_CAPTION

    if board.revealed_letters_count >= 1:
        # Add hint
        hint = board.character.name[: board.revealed_letters_count]
        caption += phrases.GUESS_GAME_INPUT_CAPTION_HINT.format(hint)

    if game.is_global():
        caption += get_global_time_based_text(game, user)

    if should_send_to_all_players:
        if board.level > 1:
            caption += phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_IMAGE.format(
                hint_wait_seconds
            )

    if should_send_to_all_players and board.level == 1 and not board.have_revealed_all_letters():
        caption += phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_HINT.format(hint_wait_seconds)

    for u in users:
        context.application.create_task(
            full_media_send(
                context,
                saved_media=saved_media,
                chat_id=u.tg_user_id,
                caption=caption,
                ignore_forbidden_exception=True,
            )
        )

        # Set private screen for input
        context.application.create_task(set_user_private_screen(u, game))

    if not schedule_next_send:
        return

    await asyncio.sleep(hint_wait_seconds)

    # Refresh game, resend only if it's still ongoing
    game = Game.get_by_id(game.id)

    if not await should_proceed_after_hint_sleep(context, game, user):
        return

    # Reduce level
    if not reduce_level_if_possible(game, user):
        return

    await run_game(context, game, user)


def reduce_level_if_possible(game: Game, user: User) -> bool:
    """
    Issue a hint if possible, saving the game
    :param game: The game
    :param user: The user
    :return: If a life was issued
    """
    board: WhosWho = get_player_board(game, user)

    if not board.can_reduce_level() and board.have_revealed_all_letters():
        return False

    if board.can_reduce_level():
        board.reduce_level()
    else:
        board.revealed_letters_count += 1

    save_game(
        game,
        board.get_as_json_string(),
        is_opponent_board=game.is_opponent(user),
        hint_was_issued=True,
    )

    return True
