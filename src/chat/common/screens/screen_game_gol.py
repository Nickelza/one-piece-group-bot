import asyncio
import json

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.model.Game import Game
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.game.GameOutcome import GameOutcome
from src.model.game.guessorlife.GuessOrLife import GuessOrLife, PlayerType, PlayerInfo
from src.model.wiki.SupabaseRest import SupabaseRest
from src.model.wiki.Terminology import Terminology
from src.service.game_service import (
    save_game,
    get_players,
    get_guess_game_users_to_send_message_to,
    set_user_private_screen,
    end_game,
    get_text,
    end_text_based_game,
    get_global_time_based_text,
    get_global_text_challenger_finished,
    end_global_guess_game_challenger,
    timeout_opponent_guess_game,
    get_winner_loser_text,
)
from src.service.message_service import full_message_send, escape_valid_markdown_chars


def get_specific_text(
    game: Game,
    guess_or_life: GuessOrLife,
    is_finished: bool = False,
    player_type: PlayerType = None,
    outcome: GameOutcome = None,
    is_for_group: bool = False,
    is_for_new_life: bool = False,
) -> str:
    """
    Get the specific text
    :param game: The game object
    :param guess_or_life: The guess or life object
    :param is_finished: If the game is finished
    :param player_type: The player type
    :param outcome: The outcome if the game is finished
    :param is_for_group: If the text is for the group message update
    :param is_for_new_life: If the text is for a new life
    :return: The specific text
    """

    challenger, opponent = get_players(game)
    player = challenger if player_type is PlayerType.CHALLENGER else opponent
    challenger_has_finished = game.challenger_has_finished()

    ot_text_list = []
    for pt in PlayerType:
        # In case of global, skip text block of other player
        if game.is_global() and pt is not player_type:
            continue

        word_with_blanks = guess_or_life.get_word_with_blanks(
            pt, show_guessed_letters=(is_finished or pt is player_type)
        )
        word_with_blanks = escape_valid_markdown_chars(word_with_blanks)

        addition = ""
        hearts_text = (
            (Emoji.BLUE_HEART * guess_or_life.get_player_info(pt).lives)
            if not is_for_group
            else ""
        )
        user = challenger if pt is PlayerType.CHALLENGER else opponent
        if player_type is not None and (pt is player_type or is_finished):
            # Show used and remaining letters to specific user or all players if game is finished
            addition = phrases.GUESS_OR_LIFE_GAME_REMAINING_USED_LETTERS.format(
                guess_or_life.get_remaining_letters(pt),
                guess_or_life.get_used_letters_formatted(pt),
            )

            # Do not show name if sending to specific user
            if pt is player_type:
                pt_text = phrases.GUESS_OR_LIFE_GAME_WORD_LIVES.format(
                    word_with_blanks, "\n", hearts_text, addition
                )
            else:
                pt_text = phrases.GUESS_OR_LIFE_GAME_NAME_WORD_LIVES.format(
                    user.get_markdown_name(), word_with_blanks, "\n", hearts_text, addition
                )
        else:
            if is_for_group:
                pt_text = phrases.GUESS_OR_LIFE_GAME_NAME_WORD.format(
                    user.get_markdown_name(), word_with_blanks
                )
            else:
                pt_text = phrases.GUESS_OR_LIFE_GAME_NAME_WORD_LIVES.format(
                    user.get_markdown_name(),
                    word_with_blanks,
                    ("\n" if player_type is None else ""),
                    hearts_text,
                    addition,
                )

        ot_text_list.append(pt_text)

    # If opponent, swap the order
    if player_type is PlayerType.OPPONENT:
        ot_text_list.reverse()

    # Sending in private chat
    if not is_for_group:
        ot_text = "\n\n\n".join(ot_text_list)

        if game.is_global():
            ot_text += get_global_time_based_text(game, player)

            if game.is_challenger(player) and challenger_has_finished:
                ot_text += get_global_text_challenger_finished(
                    game, should_add_already_guessed_text=False
                )

        if (
            guess_or_life.can_issue_life()
            and not is_finished
            and not is_for_new_life
            and not (game.is_challenger(player) and challenger_has_finished)
        ):
            ot_text += "\n\n" + phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_LIFE_2.format(
                game.get_seconds_for_every_hint()
            )

        return ot_text

    # Updating the group message
    text_before_footer = "\n\n".join(ot_text_list) + "\n\n"
    return get_text(
        game,
        is_finished,
        game_outcome=outcome,
        terminology=guess_or_life.terminology,
        text_to_add_before_footer=text_before_footer,
    )


def get_boards(game: Game) -> [GuessOrLife, GuessOrLife]:
    """
    Get the board
    :param game: The game object
    :return: The board
    """

    # Create board
    if game.board is None:
        random_terminology: Terminology = SupabaseRest.get_random_terminology(
            max_len=Env.GUESS_OR_LIFE_MAX_CHARACTERS.get_int(),
            only_letters=True,
            min_unique_characters=GuessOrLife.get_min_unique_characters_by_difficulty(
                game.get_difficulty()
            ),
            max_unique_characters=GuessOrLife.get_max_unique_characters_by_difficulty(
                game.get_difficulty()
            ),
        )
        board = GuessOrLife(random_terminology)
        save_game(game, board.get_as_json_string(), hint_was_issued=True)

        if game.is_global():
            save_game(game, board.get_as_json_string(), is_opponent_board=True)

        return board, board  # First initialization, both boards are the same

    return get_board_object_from_json(json.loads(game.board)), (
        (get_board_object_from_json(json.loads(game.opponent_board)) if game.is_global() else None)
    )


def get_player_board(game: Game, user: User) -> GuessOrLife:
    """
    Get the player board
    :param game: The game object
    :param user: The user object
    :return: The board
    """

    challenger_board, opponent_board = get_boards(game)
    return challenger_board if game.is_challenger(user) or not game.is_global() else opponent_board


def get_other_board(game: Game, user: User) -> GuessOrLife:
    """
    Get the other board
    :param game: The game object
    :param user: The user object
    :return: The board
    """

    challenger_board, opponent_board = get_boards(game)
    return opponent_board if game.is_challenger(user) else challenger_board


def get_board_object_from_json(json_dict: dict) -> GuessOrLife:
    """
    Get the board
    :param json_dict: The dictionary containing the board
    :return: The board
    """

    term_dict = json_dict.pop("terminology")
    term: Terminology = Terminology(**term_dict)

    # Create challenger and opponent info
    challenger_info_dict = json_dict.pop("challenger_info")
    challenger_info: PlayerInfo = PlayerInfo(**challenger_info_dict)
    opponent_info_dict = json_dict.pop("opponent_info")
    opponent_info: PlayerInfo = PlayerInfo(**opponent_info_dict)

    # Create a Guess or Life object with attribute unpacking
    return GuessOrLife(
        terminology=term, **json_dict, challenger_info=challenger_info, opponent_info=opponent_info
    )


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


async def run_game(
    context: ContextTypes.DEFAULT_TYPE,
    game: Game,
    user: User,
    should_send_to_all_players: bool = True,
    schedule_next_send: bool = True,
    hint_wait_seconds: int = None,
) -> None:
    """
    Issue lives to the players
    :param context: The context
    :param game: The game
    :param user: The user to send the message to
    :param should_send_to_all_players: If the image should be sent to all players
    :param schedule_next_send: If the next send should be scheduled
    :param hint_wait_seconds: How many seconds to wait before issuing next hint. If none, the game default is used
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
    board = get_player_board(game, user)

    # Send the message to the users
    for u in users:
        specific_text = get_specific_text(
            game, board, player_type=get_player_type(game, u), is_for_new_life=True
        )
        if board.can_issue_life():
            remaining_time_text = (
                phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_LIFE_1
                if should_send_to_all_players
                else phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_LIFE_2
            )
            ot_text = phrases.GUESS_OR_LIFE_GAME_PRIVATE_RECAP.format(
                specific_text,
                remaining_time_text.format(hint_wait_seconds),
            )
        else:
            ot_text = specific_text

        context.application.create_task(full_message_send(context, ot_text, chat_id=u.tg_user_id))

        # Set private screen for input
        context.application.create_task(set_user_private_screen(u, game))

    if not schedule_next_send:
        return

    await asyncio.sleep(hint_wait_seconds)

    # Refresh game, resend only if it's still ongoing
    game: Game = Game.get_by_id(game.id)
    if game.is_finished():
        return

    if game.is_opponent(user) and await timeout_opponent_guess_game(context, game):
        return

    board: GuessOrLife = get_player_board(game, user)

    # Challenger is playing and they have already guessed
    if game.is_challenger(user) and board.player_has_guessed(PlayerType.CHALLENGER):
        return

    # Issue life
    if not issue_life_if_possible(game, user):
        return

    await run_game(context, game, user)


async def validate_answer(
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
        letter = update.effective_message.text
    except AttributeError:
        return

    board: GuessOrLife = get_player_board(game, user)

    # More than one letter sent
    if len(letter) > 1:
        return

    # Not a letter
    if not letter.isalpha():
        return

    player_type: PlayerType = get_player_type(game, user)
    # Letter already used
    if board.has_used_letter(player_type, letter):
        return

    # No more lives remaining
    if board.get_player_info(player_type).lives == 0:
        return

    # Add letter to used letters and refresh specific text
    board.add_used_letter(player_type, letter)
    save_game(game, board.get_as_json_string(), is_opponent_board=game.is_opponent(user))
    specific_text = get_specific_text(game, board, player_type=player_type)

    # Letter not in word
    if not board.is_letter_is_in_word(letter):
        board.remove_life(player_type)
        save_game(game, board.get_as_json_string(), is_opponent_board=game.is_opponent(user))
        specific_text = get_specific_text(game, board, player_type=player_type)
        ot_text = phrases.GUESS_OR_LIFE_GAME_PRIVATE_RECAP.format(
            phrases.GUESS_OR_LIFE_GAME_WRONG_LETTER, specific_text
        )
        await full_message_send(context, ot_text, update=update)
        return

    # Correct letter but game not finished
    if not board.is_finished(player_type, get_other_board(game, user)):
        # If challenger and they've guessed, show completion time and awaiting opponent to finish
        if player_type is PlayerType.CHALLENGER and board.player_has_guessed(player_type):
            # Set challenger and time and try enqueueing opponent timeout
            await end_global_guess_game_challenger(context, game)

            specific_text = get_specific_text(game, board, player_type=player_type)
            ot_text = phrases.GUESS_GAME_CORRECT_ANSWER.format(specific_text)
            await full_message_send(context, ot_text, update=update)

            return

        ot_text = phrases.GUESS_OR_LIFE_GAME_PRIVATE_RECAP.format(
            phrases.GUESS_OR_LIFE_GAME_CORRECT_LETTER, specific_text
        )
        await full_message_send(context, ot_text, update=update)
        return

    # End game
    challenger, opponent = get_players(game)
    outcome: GameOutcome = board.get_outcome(player_type)

    await end_game(game, outcome, context, update=update)
    user.should_update_model = False  # To avoid re-writing bounty
    loser = challenger if user == opponent else opponent

    specific_winner_text = get_specific_text(
        game, board, is_finished=True, player_type=player_type
    )
    specific_loser_text = get_specific_text(
        game, board, is_finished=True, player_type=get_player_type(game, loser)
    )
    winner_text, loser_text = get_winner_loser_text(
        game, specific_winner_text, specific_loser_text=specific_loser_text
    )

    group_text = get_specific_text(
        game, board, is_finished=True, outcome=outcome, is_for_group=True
    )
    await end_text_based_game(
        context, game, outcome, user, winner_text, loser, loser_text, group_text
    )


def issue_life_if_possible(game: Game, user: User) -> bool:
    """
    Issue a life if possible, saving the game
    :param game: The game
    :param user: The user
    :return: If a life was issued
    """
    board: GuessOrLife = get_player_board(game, user)

    if not board.can_issue_life():
        return False

    board.issue_life()
    save_game(
        game,
        board.get_as_json_string(),
        is_opponent_board=game.is_opponent(user),
        hint_was_issued=True,
    )

    return True
