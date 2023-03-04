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
from src.model.game.whoswho.WhosWho import WhosWho
from src.model.pojo.Keyboard import Keyboard
from src.model.wiki.Character import Character
from src.model.wiki.SupabaseRest import SupabaseRest
from src.service.game_service import set_user_private_screen, guess_game_countdown_to_start, save_game
from src.service.message_service import full_media_send


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, game: Game = None
                 ) -> None:
    """
    Manage the Who's Who screen
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
            guess_game_countdown_to_start(update, context, game, Env.GAME_START_WAIT_TIME.get_int(), run_game))
        return


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
        save_game(game, whos_who.get_board_json())
        return whos_who

    # Parse the JSON string and create a Character object
    json_dict = json.loads(game.board)
    char_dict = json_dict.pop("character")
    char: Character = Character(**char_dict)

    # Create a WhosWho object with attribute unpacking
    return WhosWho(character=char, **json_dict)


async def run_game(context: ContextTypes.DEFAULT_TYPE, game: Game, send_to_user: User = None,
                   should_send_to_all_players: bool = True, schedule_next_send: bool = True) -> None:
    """
    Send the blurred image
    :param context: The context object
    :param game: The game object
    :param send_to_user: The user to send the image to
    :param should_send_to_all_players: If the image should be sent to all players
    :param schedule_next_send: If the next send should be scheduled
    :return: None
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

    # Get the board
    whos_who = get_board(game)

    # Send the image
    saved_media: SavedMedia = SavedMedia(media_type=SavedMediaType.PHOTO, file_name=whos_who.latest_blurred_image)
    caption = phrases.GUESS_CHARACTER_GAME_INPUT_CAPTION
    if should_send_to_all_players:
        if whos_who.level > 1:
            caption += phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_IMAGE.format(
                Env.WHOS_WHO_NEXT_LEVEL_WAIT_TIME.get_int())
        elif whos_who.revealed_letters_count >= 1:
            # Add hint
            hint = whos_who.character.name[:whos_who.revealed_letters_count]
            caption += phrases.GUESS_GAME_INPUT_CAPTION_HINT.format(hint)

        if whos_who.level == 1 and not whos_who.have_revealed_all_letters():
            caption += phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_HINT.format(
                Env.WHOS_WHO_NEXT_LEVEL_WAIT_TIME.get_int())

    for user in users:
        context.application.create_task(
            full_media_send(context, saved_media=saved_media, chat_id=user.tg_user_id, caption=caption,
                            ignore_forbidden_exception=True))

        # Set private screen for input
        context.application.create_task(set_user_private_screen(user, game))

    if not schedule_next_send:
        return

    await asyncio.sleep(Env.WHOS_WHO_NEXT_LEVEL_WAIT_TIME.get_int())

    # Refresh game, resend only if it's still ongoing
    game = Game.get_by_id(game.id)
    if GameStatus(game.status) is not GameStatus.IN_PROGRESS:
        return

    # Reduce level
    whos_who = get_board(game)

    # Already at level 1
    if whos_who.level == 1 and whos_who.have_revealed_all_letters():
        return

    if whos_who.level > 1:
        whos_who.reduce_level()
    else:
        whos_who.revealed_letters_count += 1

    save_game(game, whos_who.get_board_json())

    await run_game(context, game)
