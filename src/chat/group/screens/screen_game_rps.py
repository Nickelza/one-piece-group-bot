import json
from typing import Tuple

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.Game import Game
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.GameStatus import GameStatus
from src.model.enums.Screen import Screen
from src.model.error.GroupChatError import GroupChatError
from src.model.game.GameOutcome import GameOutcome
from src.model.game.GameTurn import GameTurn
from src.model.game.RockPaperScissors import RockPaperScissors
from src.model.game.RockPaperScissorsChoice import RockPaperScissorsChoice as RPSChoice
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_bounty_formatted
from src.service.message_service import full_message_send, mention_markdown_user


def manage(update: Update, context: CallbackContext, user: User, inbound_keyboard: Keyboard, game: Game = None) -> None:
    """
    Manage the game screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The inbound keyboard
    :param game: The game object
    :return: None
    """

    if game is None:
        try:
            game: Game = Game.get_by_id(inbound_keyboard.info['a'])
        except IndexError:
            full_message_send(context, GroupChatError.GAME_NOT_FOUND.build(), update=update)
            return

    # Get board
    game, rock_paper_scissors = get_board(game)
    challenger: User = game.challenger
    opponent: User = game.opponent

    if inbound_keyboard.screen == Screen.GRP_ROCK_PAPER_SCISSORS_GAME:
        rps_choice = RPSChoice(inbound_keyboard.info['b'])
        # Save choice
        if user == game.challenger:
            rock_paper_scissors.challenger_choice = rps_choice.value
        else:
            rock_paper_scissors.opponent_choice = rps_choice.value

        game.board = rock_paper_scissors.get_board_json()
        game.save()

        full_message_send(context, get_choice_text(rps_choice), update=update, answer_callback=True, show_alert=True)

    # Game is finished
    game_turn = GameTurn(rock_paper_scissors.get_turn().value)
    if game_turn is GameTurn.FINISHED:
        if rock_paper_scissors.get_outcome() == GameOutcome.CHALLENGER_WON:
            game.status = GameStatus.WON.value
            challenger.bounty += game.wager
        elif rock_paper_scissors.get_outcome() == GameOutcome.OPPONENT_WON:
            game.status = GameStatus.LOST.value
            challenger.bounty += game.wager
        else:
            game.status = GameStatus.DRAW.value
            challenger.bounty += game.wager / 2
            opponent.bounty += game.wager / 2

        game.save()
        challenger.save()
        opponent.save()

        # Send result
        full_message_send(context, get_text(game, rock_paper_scissors, game_turn), update=update)
        return

    # Create outbound keyboard
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

    # Send message
    try:
        full_message_send(context, get_text(game, rock_paper_scissors, game_turn), update=update,
                          keyboard=outbound_keyboard, authorized_users=[challenger.tg_user_id, opponent.tg_user_id])
    except BadRequest:
        # Possible when user changes a choice, so the output message stays the same
        pass


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


def get_text(game: Game, rock_paper_scissors: RockPaperScissors, game_turn: GameTurn) -> str:
    """
    Get the text
    :param game: The game object
    :param rock_paper_scissors: The rock paper scissors object
    :param game_turn: The game turn
    :return: The text
    """

    if game_turn is GameTurn.FINISHED:
        if rock_paper_scissors.get_outcome() == GameOutcome.CHALLENGER_WON:
            added_ot_text = phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.challenger))
        elif rock_paper_scissors.get_outcome() == GameOutcome.OPPONENT_WON:
            added_ot_text = phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.opponent))
        else:
            added_ot_text = phrases.GAME_RESULT_DRAW
    else:
        if rock_paper_scissors.challenger_choice == RPSChoice.NONE and \
                rock_paper_scissors.opponent_choice == RPSChoice.NONE:
            added_ot_text = phrases.GAME_STATUS_AWAITING_CHOICE
        elif rock_paper_scissors.challenger_choice == RPSChoice.NONE:
            added_ot_text = phrases.GAME_STATUS_AWAITING_USER_CHOICE.format(mention_markdown_user(game.challenger))
        else:
            added_ot_text = phrases.GAME_STATUS_AWAITING_USER_CHOICE.format(mention_markdown_user(game.opponent))

    return phrases.ROCK_PAPER_SCISSORS_GAME_TEXT.format(mention_markdown_user(game.challenger),
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
            return phrases.ROCK_PAPER_SCISSORS_CHOICE.format(phrases.ROCK_PAPER_SCISSORS_CHOICE_ROCK)
        case RPSChoice.PAPER:
            return phrases.ROCK_PAPER_SCISSORS_CHOICE.format(phrases.ROCK_PAPER_SCISSORS_CHOICE_PAPER)
        case RPSChoice.SCISSORS:
            return phrases.ROCK_PAPER_SCISSORS_CHOICE.format(phrases.ROCK_PAPER_SCISSORS_CHOICE_SCISSORS)

        case _:
            raise ValueError(f'Unknown Rock Paper Scissors choice: {rps_choice}')
