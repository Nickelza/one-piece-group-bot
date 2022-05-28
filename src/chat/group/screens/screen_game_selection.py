from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.Game import Game
from src.model.enums.Screen import Screen
from src.model.error.GroupChatError import GroupChatError
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_bounty_formatted
from src.service.game_service import delete_game
from src.service.message_service import full_message_send, mention_markdown_user, get_yes_no_keyboard


def manage(update: Update, context: CallbackContext, inbound_keyboard: Keyboard) -> None:
    """
    Manage the game screen
    :param update: The update object
    :param context: The context object
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    try:
        game: Game = Game.get_by_id(inbound_keyboard.info['a'])
    except IndexError:
        full_message_send(context, GroupChatError.GAME_NOT_FOUND.build(), update=update)
        return

    # User clicked on cancel button
    if 'x' in inbound_keyboard.info:
        delete_game(update, context, game)
        return

    game.type = GameType(inbound_keyboard.info['b']).value
    game.save()

    ot_text = phrases.GAME_REQUEST.format(mention_markdown_user(game.opponent),
                                          mention_markdown_user(game.challenger),
                                          get_game_name(GameType(game.type)),
                                          get_bounty_formatted(game.wager))
    outbound_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(game.opponent, game.id,
                                                                   phrases.KEYBOARD_OPTION_ACCEPT,
                                                                   phrases.KEYBOARD_OPTION_REJECT,
                                                                   Screen.GRP_GAME_OPPONENT_CONFIRMATION)]

    button_delete_info = {'a': game.id, 'u': [game.challenger.id, game.opponent.id], 'x': 1}
    outbound_keyboard.append([Keyboard(phrases.KEYBOARD_OPTION_CANCEL, info=button_delete_info,
                                       screen=Screen.GRP_GAME_OPPONENT_CONFIRMATION)])

    full_message_send(context, ot_text, update=update, keyboard=outbound_keyboard)


def get_game_name(game_type: GameType) -> str:
    match game_type:
        case GameType.ROCK_PAPER_SCISSORS:
            return phrases.ROCK_PAPER_SCISSORS_GAME_NAME

        case GameType.RUSSIAN_ROULETTE:
            return phrases.RUSSIAN_ROULETTE_GAME_NAME

        case _:
            return phrases.GAME_UNKNOWN_NAME
