import json
from typing import Tuple

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext

import resources.phrases as phrases
import src.service.game_service as game_service
from src.model.Game import Game
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.GameStatus import GameStatus
from src.model.enums.Screen import Screen
from src.model.game.GameOutcome import GameOutcome
from src.model.game.rps.RockPaperScissors import RockPaperScissors
from src.model.game.rps.RockPaperScissorsChoice import RockPaperScissorsChoice as RPSChoice
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_bounty_formatted
from src.service.message_service import full_message_send, mention_markdown_user


def manage(update: Update, context: CallbackContext, user: User, inbound_keyboard: Keyboard, game: Game = None) -> None:
    """
    Manage the Rock Paper Scissors game screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The inbound keyboard
    :param game: The game object
    :return: None
    """

    # Get the game
    if game is None:
        game = game_service.get_game_from_keyboard(update, context, inbound_keyboard)

    if game.status != GameStatus.IN_PROGRESS.value:
        full_message_send(context, phrases.GAME_ENDED, update=update, answer_callback=True, show_alert=True)
        return

    # get_game_from_keyboard will send error message if game is not found
    if game is not None:
        game, rock_paper_scissors = get_board(game)

        if inbound_keyboard.screen == Screen.GRP_ROCK_PAPER_SCISSORS_GAME:
            rps_choice = RPSChoice(inbound_keyboard.info['b'])
            # Save choice
            if user == game.challenger:
                rock_paper_scissors.challenger_choice = rps_choice.value
            else:
                rock_paper_scissors.opponent_choice = rps_choice.value

            game.board = rock_paper_scissors.get_board_json()
            game.save()

            full_message_send(context, get_choice_text(rps_choice), update=update, answer_callback=True,
                              show_alert=True)

        # Game is finished
        if rock_paper_scissors.is_finished():
            game_outcome: GameOutcome = rock_paper_scissors.get_outcome()
            game = game_service.end_game(game, game_outcome)

            # Send result
            full_message_send(context, get_text(game, rock_paper_scissors), update=update,
                              keyboard=get_outbound_keyboard(game),
                              authorized_users=game_service.get_game_authorized_tg_user_ids(game))
            return

        # Send message
        try:
            full_message_send(context, get_text(game, rock_paper_scissors), update=update,
                              keyboard=get_outbound_keyboard(game),
                              authorized_users=game_service.get_game_authorized_tg_user_ids(game))
        except BadRequest:
            # Possible when user changes a choice, so the output message stays the same
            pass


def get_outbound_keyboard(game) -> list[list[Keyboard]]:
    """
    Get the outbound keyboard
    :param game: The game object
    :return: The outbound keyboard
    """

    outbound_keyboard: list[list[Keyboard]] = []

    keyboard_line: list[Keyboard] = []
    button_info_rock = {'a': game.id, 'b': RPSChoice.ROCK}
    keyboard_line.append(Keyboard(Emoji.ROCK.value, info=button_info_rock, screen=Screen.GRP_ROCK_PAPER_SCISSORS_GAME))
    button_info_paper = {'a': game.id, 'b': RPSChoice.PAPER}
    keyboard_line.append(Keyboard(Emoji.PAPER.value, info=button_info_paper,
                                  screen=Screen.GRP_ROCK_PAPER_SCISSORS_GAME))
    button_info_scissors = {'a': game.id, 'b': RPSChoice.SCISSORS}
    keyboard_line.append(Keyboard(Emoji.SCISSORS.value, info=button_info_scissors,
                                  screen=Screen.GRP_ROCK_PAPER_SCISSORS_GAME))
    outbound_keyboard.append(keyboard_line)

    return outbound_keyboard


def get_board(game: Game) -> Tuple[Game, RockPaperScissors]:
    """
    Get the board
    :param game: The game object
    :return: The board
    """

    # Create board
    if game.board is None:
        rock_paper_scissors = RockPaperScissors()
        game.board = rock_paper_scissors.get_board_json()
        game.save()
        return game, rock_paper_scissors

    rock_paper_scissors_dict = json.loads(game.board)
    return game, RockPaperScissors(**rock_paper_scissors_dict)


def get_text(game: Game, rock_paper_scissors: RockPaperScissors) -> str:
    """
    Get the text
    :param game: The game object
    :param rock_paper_scissors: The rock paper scissors object
    :return: The text
    """

    if rock_paper_scissors.is_finished():
        if rock_paper_scissors.get_outcome() == GameOutcome.CHALLENGER_WON:
            added_ot_text = phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.challenger))
        elif rock_paper_scissors.get_outcome() == GameOutcome.OPPONENT_WON:
            added_ot_text = phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.opponent))
        else:
            added_ot_text = phrases.GAME_RESULT_DRAW

        choices_text = phrases.ROCK_PAPER_SCISSORS_CHOICES.format(mention_markdown_user(game.challenger),
                                                                  get_choice_emoji(
                                                                      rock_paper_scissors.challenger_choice),
                                                                  mention_markdown_user(game.opponent),
                                                                  get_choice_emoji(rock_paper_scissors.opponent_choice))
        added_ot_text = choices_text + added_ot_text
    else:
        if rock_paper_scissors.challenger_choice == RPSChoice.NONE and \
                rock_paper_scissors.opponent_choice == RPSChoice.NONE:
            added_ot_text = phrases.GAME_STATUS_AWAITING_CHOICE
        elif rock_paper_scissors.challenger_choice == RPSChoice.NONE:
            added_ot_text = phrases.GAME_STATUS_AWAITING_USER_CHOICE.format(mention_markdown_user(game.challenger))
        else:
            added_ot_text = phrases.GAME_STATUS_AWAITING_USER_CHOICE.format(mention_markdown_user(game.opponent))

    return phrases.GAME_TEXT.format(phrases.ROCK_PAPER_SCISSORS_GAME_NAME,
                                    mention_markdown_user(game.challenger),
                                    mention_markdown_user(game.opponent),
                                    get_bounty_formatted(game.wager),
                                    added_ot_text)


def get_choice_text(rps_choice: RPSChoice) -> str:
    """
    Get the choice text
    :param rps_choice: The choice
    :return: The text
    """

    match rps_choice:
        case RPSChoice.ROCK:
            return phrases.ROCK_PAPER_SCISSORS_CHOICE_ALERT.format(phrases.ROCK_PAPER_SCISSORS_CHOICE_ROCK)
        case RPSChoice.PAPER:
            return phrases.ROCK_PAPER_SCISSORS_CHOICE_ALERT.format(phrases.ROCK_PAPER_SCISSORS_CHOICE_PAPER)
        case RPSChoice.SCISSORS:
            return phrases.ROCK_PAPER_SCISSORS_CHOICE_ALERT.format(phrases.ROCK_PAPER_SCISSORS_CHOICE_SCISSORS)

        case _:
            raise ValueError(f'Unknown Rock Paper Scissors choice: {rps_choice}')


def get_choice_emoji(rps_choice: RPSChoice) -> str:
    """
    Get the choice emoji
    :param rps_choice: The choice
    :return: The emoji
    """

    match rps_choice:
        case RPSChoice.ROCK:
            return Emoji.ROCK.value
        case RPSChoice.PAPER:
            return Emoji.PAPER.value
        case RPSChoice.SCISSORS:
            return Emoji.SCISSORS.value

        case _:
            raise ValueError(f'Unknown Rock Paper Scissors choice: {rps_choice}')
