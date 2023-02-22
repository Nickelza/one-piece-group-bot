import asyncio
import json

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
import src.service.game_service as game_service
from src.model.Game import Game
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.SavedMedia import SavedMedia
from src.model.enums.SavedMediaType import SavedMediaType
from src.model.enums.Screen import Screen
from src.model.game.shambles.Shambles import Shambles
from src.model.pojo.Keyboard import Keyboard
from src.model.wiki.SupabaseRest import SupabaseRest
from src.model.wiki.Terminology import Terminology
from src.service.game_service import set_user_private_screen, guess_game_countdown_to_start, save_game, \
    get_guess_game_users_to_send_image_to
from src.service.message_service import full_media_send


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, game: Game = None
                 ) -> None:
    """
    Manage the Russian Roulette screen
    :param update: The update object
    :param context: The context object
    :param inbound_keyboard: The inbound keyboard
    :param game: The game object
    :return: None
    """

    # Get the game from validation, will handle error messages
    game = await game_service.validate_game(update, context, inbound_keyboard, game)
    if game is None:
        return

    # Init board
    get_board(game)

    # From opponent confirmation, start countdown
    if inbound_keyboard.screen == Screen.GRP_GAME_OPPONENT_CONFIRMATION:
        game.status = GameStatus.COUNTDOWN_TO_START
        game.save()
        context.application.create_task(
            guess_game_countdown_to_start(update, context, game, Env.GAME_START_WAIT_TIME.get_int(),
                                          run_game_function=run_game))
        return


def get_board(game: Game) -> Shambles:
    """
    Get the board
    :param game: The game object
    :return: The board
    """

    # Create board
    if game.board is None:
        random_terminology: Terminology = SupabaseRest.get_random_terminology(
            max_len=Env.SHAMBLES_GRID_SIZE.get_int(), only_letters=True)
        shambles = Shambles(random_terminology)
        save_game(game, shambles.get_board_json())
        return shambles

    # Parse the JSON string and create a Terminology object
    json_dict = json.loads(game.board)
    term_dict = json_dict.pop("terminology")
    char: Terminology = Terminology(**term_dict)

    # Create a Shambles object with attribute unpacking
    return Shambles(terminology=char, **json_dict)


async def run_game(context: ContextTypes.DEFAULT_TYPE, game: Game, send_to_user: User = None,
                   should_send_to_all_participants: bool = True, schedule_next_send: bool = True) -> None:
    """
    Send the blurred image
    :param context: The context object
    :param game: The game object
    :param send_to_user: The user to send the image to
    :param should_send_to_all_participants: If the image should be sent to all participants
    :param schedule_next_send: If the next send should be scheduled
    :return: None
    """

    users = await get_guess_game_users_to_send_image_to(game, send_to_user, should_send_to_all_participants,
                                                        schedule_next_send)

    # Get the board
    shambles = get_board(game)

    # Send the image
    saved_media: SavedMedia = SavedMedia(media_type=SavedMediaType.PHOTO, file_name=shambles.image_path)
    caption = phrases.GUESS_TERM_GAME_INPUT_CAPTION
    if should_send_to_all_participants:
        if shambles.can_reduce_level():
            caption += phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_IMAGE.format(
                Env.SHAMBLES_NEXT_LEVEL_WAIT_TIME.get_int())
        elif shambles.revealed_letters_count >= 1:
            # Add hint
            hint = shambles.terminology.name[:shambles.revealed_letters_count]
            caption += phrases.GUESS_GAME_INPUT_CAPTION_HINT.format(hint)

        if shambles.get_excludable_letters_count() == 0 and not shambles.have_revealed_all_letters():
            caption += phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_HINT.format(
                Env.SHAMBLES_NEXT_LEVEL_WAIT_TIME.get_int())

    for user in users:
        context.application.create_task(
            full_media_send(context, saved_media=saved_media, chat_id=user.tg_user_id, caption=caption,
                            ignore_forbidden_exception=True))

        # Set private screen for input
        context.application.create_task(set_user_private_screen(user, game))

    if not schedule_next_send:
        return

    await asyncio.sleep(Env.SHAMBLES_NEXT_LEVEL_WAIT_TIME.get_int())

    # Refresh game, resend only if it's still ongoing
    game = Game.get_by_id(game.id)
    if GameStatus(game.status) is not GameStatus.IN_PROGRESS:
        return

    # Reduce level
    shambles = get_board(game)

    # Already at level 1
    if not shambles.can_reduce_level() and shambles.have_revealed_all_letters():
        return

    if shambles.can_reduce_level():
        shambles.reduce_level()
    else:
        shambles.revealed_letters_count += 1

    save_game(game, shambles.get_board_json())

    await run_game(context, game)
