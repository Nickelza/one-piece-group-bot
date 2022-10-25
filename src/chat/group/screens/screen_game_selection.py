from strenum import StrEnum
from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_belly_formatted
from src.service.game_service import delete_game, validate_game
from src.service.message_service import full_message_send, mention_markdown_user, get_yes_no_keyboard


class GameSelectionReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    GAME_ID = 'a'
    GAME_TYPE = 'b'
    CANCEL = 'c'


def manage(update: Update, context: CallbackContext, user: User, inbound_keyboard: Keyboard) -> None:
    """
    Manage the game screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    # Get the game from validation, will handle error messages
    game = validate_game(update, context, inbound_keyboard)
    if game is None:
        return

    # User clicked on cancel button
    if GameSelectionReservedKeys.CANCEL in inbound_keyboard.info:
        delete_game(update, context, game)
        user.should_update_model = False
        return

    game.type = GameType(inbound_keyboard.info[GameSelectionReservedKeys.GAME_TYPE])
    game.save()

    ot_text = phrases.GAME_REQUEST.format(mention_markdown_user(game.opponent),
                                          mention_markdown_user(game.challenger),
                                          (GameType(game.type)),
                                          get_belly_formatted(game.wager))
    outbound_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(game.opponent,
                                                                   screen=Screen.GRP_GAME_OPPONENT_CONFIRMATION,
                                                                   yes_text=phrases.KEYBOARD_OPTION_ACCEPT,
                                                                   no_text=phrases.KEYBOARD_OPTION_REJECT,
                                                                   primary_key=game.id)]

    button_delete_info = {GameSelectionReservedKeys.GAME_ID: game.id,
                          ReservedKeyboardKeys.AUTHORIZED_USER: [
                              game.challenger.id, game.opponent.id], GameSelectionReservedKeys.CANCEL: True}
    outbound_keyboard.append([Keyboard(phrases.KEYBOARD_OPTION_CANCEL, info=button_delete_info,
                                       screen=Screen.GRP_GAME_OPPONENT_CONFIRMATION)])

    full_message_send(context, ot_text, update=update, keyboard=outbound_keyboard)
