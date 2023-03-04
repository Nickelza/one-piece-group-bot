import asyncio
import json
import string
from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
import src.service.game_service as game_service
from src.model.Game import Game
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.GameStatus import GameStatus
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.Screen import Screen
from src.model.game.GameOutcome import GameOutcome
from src.model.game.guessorlife.GuessOrLife import GuessOrLife, PlayerType, PlayerInfo
from src.model.pojo.Keyboard import Keyboard
from src.model.wiki.SupabaseRest import SupabaseRest
from src.model.wiki.Terminology import Terminology
from src.service.game_service import get_text, save_game, get_players, get_game_authorized_tg_user_ids
from src.service.message_service import full_media_send
from src.service.message_service import full_message_send, escape_valid_markdown_chars


class GameGOLReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    LETTER = 'b'
    CHECK = 'c'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, inbound_keyboard: Keyboard,
                 game: Game = None) -> None:
    """
    Manage the Guess or Life game screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The inbound keyboard
    :param game: The game object
    :return: None
    """

    # Get the game from validation, will handle error messages
    game = await game_service.validate_game(update, context, inbound_keyboard, game)
    if game is None:
        return

    guess_or_life: GuessOrLife = get_board(game)

    # From opponent confirmation, start countdown
    if inbound_keyboard.screen == Screen.GRP_GAME_OPPONENT_CONFIRMATION:
        game.status = GameStatus.COUNTDOWN_TO_START
        game.save()
        context.application.create_task(
            game_service.guess_game_countdown_to_start(update, context, game, Env.GAME_START_WAIT_TIME.get_int(),
                                                       run_game, is_played_in_private_chat=False))
        return

    player_type: PlayerType = get_player_type(game, user)
    player_info: PlayerInfo = guess_or_life.get_player_info(player_type)
    is_finished: bool = False

    # Not invoked from opponent confirmation
    if inbound_keyboard.screen == Screen.GRP_GUESS_OR_LIFE_GAME:
        info_text_used_letters = get_info_text_with_used_letters(guess_or_life, player_type)

        # Display current situation
        if GameGOLReservedKeys.CHECK in inbound_keyboard.info:
            await full_message_send(context, info_text_used_letters, update=update, answer_callback=True,
                                    show_alert=True)
            return

        # Letter already used
        if guess_or_life.has_used_letter(player_type, inbound_keyboard.info[GameGOLReservedKeys.LETTER]):
            callback_text = phrases.GUESS_OR_LIFE_GAME_LETTER_ALREADY_USED.format(info_text_used_letters)
            await full_message_send(context, callback_text, update=update, answer_callback=True, show_alert=True)
            return

        # No more lives remaining
        elif player_info.lives == 0:
            callback_text = phrases.GUESS_OR_LIFE_GAME_NO_MORE_LIVES.format(info_text_used_letters)
            await full_message_send(context, callback_text, update=update, answer_callback=True, show_alert=True)
            return

        else:
            # Add letter to used letters
            letter = inbound_keyboard.info[GameGOLReservedKeys.LETTER]
            guess_or_life.add_used_letter(player_type, letter)
            save_game(game, guess_or_life.get_board_json())

            # Refresh info text
            info_text_used_letters = get_info_text_with_used_letters(guess_or_life, player_type)

            # Letter not in word
            if not guess_or_life.is_letter_is_in_word(letter):
                guess_or_life.remove_life(player_type)
                save_game(game, guess_or_life.get_board_json())
                callback_text = phrases.GUESS_OR_LIFE_GAME_WRONG_LETTER.format(info_text_used_letters)
                await full_message_send(context, callback_text, update=update, answer_callback=True, show_alert=True)
            # Game not finished
            elif not guess_or_life.is_finished(player_type):
                callback_text = phrases.GUESS_OR_LIFE_GAME_CORRECT_LETTER.format(
                    guess_or_life.get_word_with_blanks(player_type))
                await full_message_send(context, callback_text, update=update, answer_callback=True)

            else:
                # Game finished
                callback_text = phrases.GUESS_OR_LIFE_GAME_CORRECT_LETTER_WIN.format(
                    guess_or_life.get_word_with_blanks(player_type))
                await full_message_send(context, callback_text, update=update, answer_callback=True, show_alert=True)
                game_outcome: GameOutcome = guess_or_life.get_outcome(player_type)
                await game_service.end_game(game, game_outcome)
                user.should_update_model = False
                is_finished = True

    await refresh_message(context, game, guess_or_life, update=update, is_finished=is_finished, player_type=player_type)


async def refresh_message(context, game, guess_or_life, update: Update = None, is_finished: bool = False,
                          player_type: PlayerType = None):
    """
    Refresh the message
    :param context: The context
    :param game: The game object
    :param guess_or_life: The guess or life object
    :param update: The update
    :param is_finished: If the game is finished
    :param player_type: The player type, used to determine the outcome without checking both players board
    :return: None
    """

    ot_text = get_specific_text(game, guess_or_life, is_finished=is_finished, player_type=player_type)

    if not is_finished:
        outbound_keyboard = get_outbound_keyboard(game)
    else:
        outbound_keyboard = None

    await full_media_send(context, saved_media_name=SavedMediaName.GAME_GUESS_OR_LIFE, caption=ot_text,
                          update=update, authorized_users=get_game_authorized_tg_user_ids(game),
                          keyboard=outbound_keyboard, group_chat=game.group_chat, edit_message_id=game.message_id,
                          ignore_bad_request_exception=True)


def get_specific_text(game: Game, guess_or_life: GuessOrLife, is_finished: bool = False, player_type: PlayerType = None,
                      remaining_seconds_to_start: int = None) -> str:
    """
    Get the specific text
    :param game: The game object
    :param guess_or_life: The guess or life object
    :param is_finished: If the game is finished
    :param player_type: The player type
    :param remaining_seconds_to_start: The remaining seconds to start
    :return: The specific text
    """

    challenger, opponent = get_players(game)

    word_with_blanks = guess_or_life.get_word_with_blanks(PlayerType.CHALLENGER, show_guessed_letters=is_finished)
    word_with_blanks = escape_valid_markdown_chars(word_with_blanks)
    challenger_info_text = phrases.GUESS_OR_LIFE_GAME_NAME_WORD_LIVES.format(
        challenger.get_markdown_name(), word_with_blanks,
        Emoji.HEART * guess_or_life.get_player_info(PlayerType.CHALLENGER).lives)

    word_with_blanks = guess_or_life.get_word_with_blanks(PlayerType.OPPONENT, show_guessed_letters=is_finished)
    word_with_blanks = escape_valid_markdown_chars(word_with_blanks)
    opponent_info_text = '\n\n' + phrases.GUESS_OR_LIFE_GAME_NAME_WORD_LIVES.format(
        opponent.get_markdown_name(), word_with_blanks,
        Emoji.HEART * guess_or_life.get_player_info(PlayerType.OPPONENT).lives)

    text_before_footer = challenger_info_text + opponent_info_text

    if is_finished:
        game_outcome: GameOutcome = guess_or_life.get_outcome(player_type)
        text_before_footer += '\n\n'
    else:
        game_outcome: GameOutcome = GameOutcome.NONE

        if guess_or_life.can_issue_live():
            text_before_footer += phrases.GUESS_OR_LIFE_NEW_LIFE_EVERY.format(
                Env.GUESS_OR_LIFE_NEW_LIFE_WAIT_TIME.get_int())

    return get_text(game, is_finished, game_outcome=game_outcome, is_turn_based=False,
                    terminology=guess_or_life.terminology, remaining_seconds_to_start=remaining_seconds_to_start,
                    text_to_add_before_footer=text_before_footer)


def get_outbound_keyboard(game: Game) -> list[list[Keyboard]]:
    """
    Get the outbound keyboard
    :param game: The game object
    :return: The outbound keyboard
    """

    outbound_keyboard: list[list[Keyboard]] = []

    # Alphabet
    max_letters_per_row = 7
    alphabet = list(string.ascii_uppercase)

    keyboard_row: list[Keyboard] = []
    for index, letter in enumerate(alphabet):
        info: dict = {ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: game.id,
                      GameGOLReservedKeys.LETTER: letter}
        keyboard_row.append(Keyboard(letter, info=info, screen=Screen.GRP_GUESS_OR_LIFE_GAME))

        if (index + 1) % max_letters_per_row == 0:
            outbound_keyboard.append(keyboard_row)
            keyboard_row = []

    outbound_keyboard.append(keyboard_row)

    # Add check button
    check_btn_info = {ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: game.id, GameGOLReservedKeys.CHECK: True}
    outbound_keyboard.append([Keyboard(
        phrases.GUESS_OR_LIFE_GAME_CHECK, info=check_btn_info, screen=Screen.GRP_GUESS_OR_LIFE_GAME)])

    return outbound_keyboard


def get_board(game: Game) -> GuessOrLife:
    """
    Get the board
    :param game: The game object
    :return: The board
    """

    # Create board
    if game.board is None:
        random_terminology: Terminology = SupabaseRest.get_random_terminology(
            max_len=Env.GUESS_OR_LIFE_MAX_CHARACTERS.get_int(), only_letters=True,
            min_unique_characters=GuessOrLife.get_min_unique_characters_by_difficulty(game.get_difficulty()),
            max_unique_characters=GuessOrLife.get_max_unique_characters_by_difficulty(game.get_difficulty()))
        guess_or_life = GuessOrLife(random_terminology)
        game_service.save_game(game, guess_or_life.get_board_json())
        return guess_or_life

    # Parse the JSON string and create a Terminology object
    json_dict = json.loads(game.board)
    term_dict = json_dict.pop("terminology")
    term: Terminology = Terminology(**term_dict)

    # Create challenger and opponent info
    challenger_info_dict = json_dict.pop("challenger_info")
    challenger_info: PlayerInfo = PlayerInfo(**challenger_info_dict)
    opponent_info_dict = json_dict.pop("opponent_info")
    opponent_info: PlayerInfo = PlayerInfo(**opponent_info_dict)

    # Create a Guess or Life object with attribute unpacking
    return GuessOrLife(terminology=term, **json_dict, challenger_info=challenger_info, opponent_info=opponent_info)


def get_player_type(game: Game, user: User) -> PlayerType:
    """
    Get the player type
    :param game: The game object
    :param user: The user object
    :return: The player type
    """

    challenger, opponent = get_players(game)

    if challenger == user:
        return PlayerType.CHALLENGER

    return PlayerType.OPPONENT


def get_info_text_with_used_letters(guess_or_life: GuessOrLife, player_type: PlayerType,
                                    should_escape: bool = False) -> str:
    """
    Get the info text
    :param guess_or_life: The guess or life object
    :param player_type: The player type
    :param should_escape: If the text should be escaped
    :return: The info text
    """

    text = phrases.GUESS_OR_LIFE_INFO_USED_LETTERS.format(
        guess_or_life.get_word_with_blanks(player_type), guess_or_life.get_used_letters_formatted(player_type))

    if not should_escape:
        return text

    return escape_valid_markdown_chars(text)


async def run_game(context: ContextTypes.DEFAULT_TYPE, game: Game):
    """
    Run the game
    :param context: The context
    :param game: The game
    """

    guess_or_life: GuessOrLife = get_board(game)
    await refresh_message(context, game, guess_or_life)

    context.application.create_task(issue_lives(context, game))


async def issue_lives(context: ContextTypes.DEFAULT_TYPE, game: Game):
    """
    Issue lives to to the players
    :param context: The context
    :param game: The game
    """

    await asyncio.sleep(Env.GUESS_OR_LIFE_NEW_LIFE_WAIT_TIME.get_int())
    game = Game.get_by_id(game.id)  # Refresh the game

    if GameStatus(game.status) is not GameStatus.IN_PROGRESS:
        return

    guess_or_life: GuessOrLife = get_board(game)
    if not guess_or_life.can_issue_live():
        return

    guess_or_life.issue_live()
    save_game(game, guess_or_life.get_board_json())

    await refresh_message(context, game, guess_or_life)

    await issue_lives(context, game)
