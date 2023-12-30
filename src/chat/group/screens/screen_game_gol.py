import asyncio
import json

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.model.Game import Game
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.GameStatus import GameStatus
from src.model.enums.Screen import Screen
from src.model.game.GameOutcome import GameOutcome
from src.model.game.guessorlife.GuessOrLife import GuessOrLife, PlayerType, PlayerInfo
from src.model.pojo.Keyboard import Keyboard
from src.model.wiki.SupabaseRest import SupabaseRest
from src.model.wiki.Terminology import Terminology
from src.service.game_service import (
    save_game,
    get_players,
    guess_game_countdown_to_start,
    get_guess_game_users_to_send_message_to,
    set_user_private_screen,
    validate_game,
    end_game,
    get_text,
    end_text_based_game,
)
from src.service.message_service import full_message_send, escape_valid_markdown_chars


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
    game: Game = None,
) -> None:
    """
    Manage the Guess or Life game screen
    :param update: The update object
    :param context: The context object
    :param inbound_keyboard: The inbound keyboard
    :param game: The game object
    :return: None
    """

    # Get the game from validation, will handle error messages
    game = await validate_game(update, context, inbound_keyboard, game)
    if game is None:
        return

    get_board(game)

    # From opponent confirmation, start countdown
    if inbound_keyboard.screen == Screen.GRP_GAME_OPPONENT_CONFIRMATION:
        game.status = GameStatus.COUNTDOWN_TO_START
        game.save()
        context.application.create_task(
            await guess_game_countdown_to_start(
                update, context, game, Env.GAME_START_WAIT_TIME.get_int(), run_game
            )
        )
        return


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

    ot_text_list = []
    for pt in PlayerType:
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
        if guess_or_life.can_issue_live() and not is_finished and not is_for_new_life:
            ot_text += "\n\n" + phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_LIFE_2.format(
                Env.GUESS_OR_LIFE_NEW_LIFE_WAIT_TIME.get_int()
            )

        return ot_text

    # Updating the group message
    text_before_footer = "\n\n".join(ot_text_list) + "\n\n"
    return get_text(
        game,
        is_finished,
        game_outcome=outcome,
        is_turn_based=False,
        terminology=guess_or_life.terminology,
        text_to_add_before_footer=text_before_footer,
    )


def get_board(game: Game) -> GuessOrLife:
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
        guess_or_life = GuessOrLife(random_terminology)
        save_game(game, guess_or_life.get_board_json())
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
    send_to_user: User = None,
    should_send_to_all_players: bool = True,
    schedule_next_send: bool = True,
) -> None:
    """
    Issue lives to to the players
    :param context: The context
    :param game: The game
    :param send_to_user: The user to send the message to
    :param should_send_to_all_players: If the image should be sent to all players
    :param schedule_next_send: If the next send should be scheduled
    """

    users = await get_guess_game_users_to_send_message_to(
        game, send_to_user, should_send_to_all_players, schedule_next_send
    )

    # Get the board
    guess_or_life = get_board(game)

    # Send the message to the users
    for user in users:
        specific_text = get_specific_text(
            game, guess_or_life, player_type=get_player_type(game, user), is_for_new_life=True
        )
        if guess_or_life.can_issue_live():
            remaining_time_text = (
                phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_LIFE_1
                if should_send_to_all_players
                else phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_LIFE_2
            )
            ot_text = phrases.GUESS_OR_LIFE_GAME_PRIVATE_RECAP.format(
                specific_text,
                remaining_time_text.format(Env.GUESS_OR_LIFE_NEW_LIFE_WAIT_TIME.get_int()),
            )
        else:
            ot_text = specific_text

        context.application.create_task(
            full_message_send(context, ot_text, chat_id=user.tg_user_id)
        )

        # Set private screen for input
        context.application.create_task(set_user_private_screen(user, game))

    if not schedule_next_send:
        return

    await asyncio.sleep(Env.GUESS_OR_LIFE_NEW_LIFE_WAIT_TIME.get_int())

    # Refresh game, resend only if it's still ongoing
    game = Game.get_by_id(game.id)
    if GameStatus(game.status) is not GameStatus.IN_PROGRESS:
        return

    # Issue live
    guess_or_life: GuessOrLife = get_board(game)
    if not guess_or_life.can_issue_live():
        return

    guess_or_life.issue_live()
    save_game(game, guess_or_life.get_board_json())

    await run_game(context, game)


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

    guess_or_life: GuessOrLife = get_board(game)

    # More than one letter sent
    if len(letter) > 1:
        return

    # Not a letter
    if not letter.isalpha():
        return

    # Letter already used
    if guess_or_life.has_used_letter(get_player_type(game, user), letter):
        return

    # No more lives remaining
    if guess_or_life.get_player_info(get_player_type(game, user)).lives == 0:
        return

    # Add letter to used letters and refresh specific text
    guess_or_life.add_used_letter(get_player_type(game, user), letter)
    save_game(game, guess_or_life.get_board_json())
    specific_text = get_specific_text(game, guess_or_life, player_type=get_player_type(game, user))

    # Letter not in word
    if not guess_or_life.is_letter_is_in_word(letter):
        guess_or_life.remove_life(get_player_type(game, user))
        save_game(game, guess_or_life.get_board_json())
        specific_text = get_specific_text(
            game, guess_or_life, player_type=get_player_type(game, user)
        )
        ot_text = phrases.GUESS_OR_LIFE_GAME_PRIVATE_RECAP.format(
            phrases.GUESS_OR_LIFE_GAME_WRONG_LETTER, specific_text
        )
        await full_message_send(context, ot_text, update=update)
        return

    # Correct letter but game not finished
    if not guess_or_life.is_finished(get_player_type(game, user)):
        ot_text = phrases.GUESS_OR_LIFE_GAME_PRIVATE_RECAP.format(
            phrases.GUESS_OR_LIFE_GAME_CORRECT_LETTER, specific_text
        )
        await full_message_send(context, ot_text, update=update)
        return

    # End game
    challenger, opponent = get_players(game)
    outcome: GameOutcome = (
        GameOutcome.CHALLENGER_WON if user == challenger else GameOutcome.OPPONENT_WON
    )
    await end_game(game, outcome, update=update)
    user.should_update_model = False  # To avoid re-writing bounty
    loser = challenger if user == opponent else opponent

    specific_text = get_specific_text(
        game, guess_or_life, player_type=get_player_type(game, user), is_finished=True
    )
    winner_text: str = phrases.GUESS_GAME_CORRECT_ANSWER.format(specific_text)

    specific_text = get_specific_text(
        game, guess_or_life, player_type=get_player_type(game, loser), is_finished=True
    )
    loser_text: str = phrases.GUESS_GAME_OPPONENT_CORRECT_ANSWER.format(specific_text)

    group_text = get_specific_text(
        game, guess_or_life, is_finished=True, outcome=outcome, is_for_group=True
    )
    await end_text_based_game(
        context, game, outcome, user, winner_text, loser, loser_text, group_text
    )
