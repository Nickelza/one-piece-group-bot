from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.Game import Game
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.error.GroupChatError import GroupChatError
from src.model.game.GameOutcome import GameOutcome
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_bounty_formatted
from src.service.message_service import full_message_send, mention_markdown_user


def get_game_from_keyboard(update: Update, context: CallbackContext, inbound_keyboard: Keyboard) -> Game | None:
    """
    Get the game from the keyboard
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The keyboard
    :return: The game
    """

    try:
        game: Game = Game.get_by_id(inbound_keyboard.info['a'])
        return game
    except IndexError:
        full_message_send(context, GroupChatError.GAME_NOT_FOUND.build(), update=update)
        return None


def end_game(game: Game, game_outcome: GameOutcome) -> Game:
    """
    End the game, set the status and return the game
    :param game: The game
    :param game_outcome: The outcome
    :return: The game
    """

    challenger: User = game.challenger
    opponent: User = game.opponent

    if game_outcome == GameOutcome.CHALLENGER_WON:
        game.status = GameStatus.WON.value
        challenger.bounty += game.wager
    elif game_outcome == GameOutcome.OPPONENT_WON:
        game.status = GameStatus.LOST.value
        challenger.bounty += game.wager
    else:
        game.status = GameStatus.DRAW.value
        challenger.bounty += game.wager / 2
        opponent.bounty += game.wager / 2

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


def get_text(game: Game, game_name: str, is_finished: bool, game_outcome: GameOutcome = None, user_turn: User = None
             ) -> str:
    """
    Get the text
    :param game: The game object
    :param game_name: The game name
    :param is_finished: Is the game finished
    :param game_outcome: The game outcome
    :param user_turn: The user turn
    :return: The text
    """

    if is_finished:
        if game_outcome is GameOutcome.CHALLENGER_WON:
            added_ot_text = phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.challenger))
        elif game_outcome is GameOutcome.OPPONENT_WON:
            added_ot_text = phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.opponent))
        else:
            added_ot_text = phrases.GAME_RESULT_DRAW
    else:
        added_ot_text = phrases.GAME_TURN.format(mention_markdown_user(user_turn))

    return phrases.GAME_TEXT.format(game_name,
                                    mention_markdown_user(game.challenger),
                                    mention_markdown_user(game.opponent),
                                    get_bounty_formatted(game.wager),
                                    added_ot_text)
