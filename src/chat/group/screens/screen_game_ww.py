import asyncio
import json
from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
import src.service.game_service as game_service
from src.model.Game import Game
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.SavedMedia import SavedMedia
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.SavedMediaType import SavedMediaType
from src.model.enums.Screen import Screen
from src.model.game.GameOutcome import GameOutcome
from src.model.game.GameType import GameType
from src.model.game.whoswho.Character import Character
from src.model.game.whoswho.WhosWho import WhosWho
from src.model.pojo.Keyboard import Keyboard
from src.model.pojo.SupabaseRest import SupabaseRest
from src.service.download_service import download_temp_file
from src.service.game_service import get_participants, end_game, get_text, get_game_name
from src.service.message_service import full_media_send, get_message_url


class GameWWReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    GAME_ID = 'a'


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
        context.application.create_task(countdown_to_start(update, context, game, Env.GAME_START_WAIT_TIME.get_int()))
        return


def get_board(game: Game) -> WhosWho:
    """
    Get the board
    :param game: The game object
    :return: The board
    """

    # Create board
    if game.board is None:
        random_character: Character = SupabaseRest.get_random_character()
        whos_who = WhosWho(random_character, download_temp_file(random_character.anime_image_url, 'jpg'))
        save_game(game, whos_who)
        return whos_who

    # Parse the JSON string and create a Character object
    json_dict = json.loads(game.board)
    char_dict = json_dict.pop("character")
    char: Character = Character(**char_dict)

    # Create a WhosWho object with attribute unpacking
    return WhosWho(character=char, **json_dict)


async def countdown_to_start(update: Update, context: ContextTypes.DEFAULT_TYPE, game: Game, remaining_seconds: int
                             ) -> None:
    """
    Countdown to start
    :param update: The update object
    :param context: The context object
    :param game: The game object
    :param remaining_seconds: The remaining time
    :return: None
    """

    play_deeplink_button = get_play_deeplink_button(game)

    if remaining_seconds <= 0:
        game.status = GameStatus.IN_PROGRESS
        game.save()

        # Edit group message
        ot_text = get_text(game, get_game_name(GameType.WHOS_WHO), False, is_turn_based=False,
                           is_played_in_private_chat=True)
        await full_media_send(context, caption=ot_text, update=update, keyboard=[[play_deeplink_button]],
                              edit_only_caption_and_keyboard=True)

        # Send the blurred image
        await send_blurred_image(context, game)
        return

    # Update message
    ot_text = get_text(game, get_game_name(GameType.WHOS_WHO), False, is_turn_based=False,
                       remaining_seconds_to_start=remaining_seconds)
    await full_media_send(context, caption=ot_text, update=update, keyboard=[[play_deeplink_button]],
                          saved_media_name=SavedMediaName.GAME_WHOS_WHO)

    # Update every 10 seconds if remaining time is more than 10 seconds, otherwise update every second
    if remaining_seconds > 10:
        await asyncio.sleep(10)
        await countdown_to_start(update, context, game, remaining_seconds - 10)
    else:
        await asyncio.sleep(1)
        await countdown_to_start(update, context, game, remaining_seconds - 1)


async def send_blurred_image(context: ContextTypes.DEFAULT_TYPE, game: Game, send_to_user: User = None,
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

    if send_to_user is not None and should_send_to_all_participants:
        raise ValueError('Cannot send to user and all participants')

    if not should_send_to_all_participants and schedule_next_send:
        raise ValueError('Cannot schedule next send if not sending to all participants')

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
    caption = phrases.WHOS_WHO_GAME_INPUT_CAPTION
    if should_send_to_all_participants:
        if whos_who.level > 1:
            caption += phrases.WHOS_WHO_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_IMAGE.format(
                Env.WHOS_WHO_NEXT_LEVEL_WAIT_TIME.get_int())
        elif whos_who.revealed_letters_count >= 1:
            # Add hint
            hint = whos_who.character.name[:whos_who.revealed_letters_count]
            caption += phrases.WHOS_WHO_GAME_INPUT_CAPTION_HINT.format(hint)

        if whos_who.level == 1:
            caption += phrases.WHOS_WHO_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_HINT.format(
                Env.WHOS_WHO_NEXT_LEVEL_WAIT_TIME.get_int())

    for user in users:
        context.application.create_task(
            full_media_send(context, saved_media=saved_media, chat_id=user.tg_user_id, caption=caption,
                            ignore_forbidden_exception=True))

        # Set private screen for input
        context.application.create_task(set_user_private_screen(game, user))

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
    if whos_who.level == 1 and whos_who.revealed_letters_count == len(whos_who.character.name):
        return

    if whos_who.level > 1:
        whos_who.reduce_level()
    else:
        whos_who.revealed_letters_count += 1

    save_game(game, whos_who)

    await send_blurred_image(context, game)


async def set_user_private_screen(game: Game, user: User) -> None:
    """
    Update the participants' private screen
    :param game: The game
    :param user: The user
    :return: None
    """

    user.private_screen_list = Screen.PVT_GAME_WW_INPUT
    user.private_screen_in_edit_id = game.id
    user.save()


async def validate_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, game: Game, user: User) -> None:
    """
    Validate the answer
    :param update: The update object
    :param context: The context object
    :param game: The game object
    :param user: The user object
    :return: None
    """

    # Get the board
    whos_who: WhosWho = get_board(game)

    try:
        if not whos_who.is_correct(update.effective_message.text):
            return

        # End game
        challenger, opponent = get_participants(game)
        outcome: GameOutcome = GameOutcome.CHALLENGER_WON if user == challenger else GameOutcome.OPPONENT_WON
        await end_game(game, outcome)
        user.should_update_model = False  # To avoid re-writing bounty
        loser = challenger if user == opponent else opponent

        # Go to game message in group button
        outbound_keyboard: list[list[Keyboard]] = [[Keyboard(text=phrases.PVT_KEY_GO_TO_MESSAGE,
                                                             url=get_message_url(game.group_chat, game.message_id))]]

        # Send message to winner
        winner_caption: str = phrases.WHOS_WHO_GAME_CORRECT_ANSWER.format(whos_who.character.get_markdown_mention())
        await full_media_send(context, chat_id=user.tg_user_id, caption=winner_caption,
                              saved_media=SavedMedia(media_type=SavedMediaType.PHOTO, file_name=whos_who.image_path),
                              ignore_forbidden_exception=True, keyboard=outbound_keyboard)

        # Send message to loser
        loser_caption: str = phrases.WHOS_WHO_GAME_OPPONENT_CORRECT_ANSWER.format(
            whos_who.character.get_markdown_mention())
        await full_media_send(context, chat_id=loser.tg_user_id, caption=loser_caption,
                              saved_media=SavedMedia(media_type=SavedMediaType.PHOTO, file_name=whos_who.image_path),
                              ignore_forbidden_exception=True, keyboard=outbound_keyboard)

        # Update group message
        ot_text = get_text(game, get_game_name(GameType.WHOS_WHO), True, is_turn_based=False,
                           character=whos_who.character, game_outcome=outcome)
        group_chat: GroupChat = game.group_chat
        await full_media_send(context, caption=ot_text, group_chat=group_chat, edit_message_id=game.message_id,
                              edit_only_caption_and_keyboard=True)

    except AttributeError:
        pass


def get_play_deeplink_button(game: Game) -> Keyboard:
    """
    Get the play button for the game
    :param game: The game
    :return: The keyboard
    """

    info: dict = {ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: game.id}
    return Keyboard(phrases.GRP_KEY_GAME_PLAY, info, screen=Screen.PVT_GAME_WW_INPUT,
                    is_deeplink=True)


def save_game(game: Game, whos_who: WhosWho) -> None:
    """
    Save the game
    :param game: The game
    :param whos_who: The board
    :return: None
    """

    game.board = whos_who.get_board_json()
    game.save()
