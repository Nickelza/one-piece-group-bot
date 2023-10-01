import json
from datetime import datetime
from enum import StrEnum
from typing import Tuple

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
import src.service.game_service as game_service
from src.model.Game import Game
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.Screen import Screen
from src.model.game.GameOutcome import GameOutcome
from src.model.game.russianroulette.RussianRoulette import RussianRoulette
from src.model.game.russianroulette.RussianRouletteChamberStatus import RussianRouletteChamberStatus as RRChamberStatus
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send, full_media_send


class GameRRReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    GAME_ID = 'a'
    POSITION = 'b'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, inbound_keyboard: Keyboard,
                 game: Game = None) -> None:
    """
    Manage the Russian Roulette screen
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

    game, russian_roulette = get_board(game)
    game.last_interaction_date = datetime.now()

    # Not invoked from opponent confirmation
    if inbound_keyboard.screen == Screen.GRP_RUSSIAN_ROULETTE_GAME:
        # Not user's turn
        if not russian_roulette.is_user_turn(user, game):
            await full_message_send(context, phrases.GAME_NOT_YOUR_TURN, update=update, answer_callback=True,
                                    show_alert=True)
            return

        x, y = inbound_keyboard.info[GameRRReservedKeys.POSITION]
        # Chamber is already fired
        if russian_roulette.cylinder[x][y] == RRChamberStatus.FIRED:
            await full_message_send(context, phrases.RUSSIAN_ROULETTE_GAME_CHAMBER_ALREADY_FIRED, update=update,
                                    answer_callback=True, show_alert=True)
            return

        russian_roulette.cylinder[x][y] = RRChamberStatus.FIRED

        await full_message_send(context, get_choice_text(russian_roulette.bullet_is_fired()), update=update,
                                answer_callback=True)

    should_notify_of_turn = False
    # Game is finished
    if russian_roulette.is_finished():
        game_outcome: GameOutcome = russian_roulette.get_outcome()
        game = await game_service.end_game(game, game_outcome, update=update)
        user.should_update_model = False

        # Send result
        await full_media_send(context, caption=get_specific_text(game, russian_roulette), update=update,
                              keyboard=get_outbound_keyboard(game, russian_roulette),
                              authorized_users=game_service.get_game_authorized_tg_user_ids(game),
                              edit_only_caption_and_keyboard=True)
    else:
        if inbound_keyboard.screen == Screen.GRP_RUSSIAN_ROULETTE_GAME:
            # Update turn only on regular interaction
            russian_roulette.set_turn()

        # Send message
        await full_media_send(context, caption=get_specific_text(game, russian_roulette), update=update,
                              keyboard=get_outbound_keyboard(game, russian_roulette),
                              authorized_users=game_service.get_game_authorized_tg_user_ids(game),
                              saved_media_name=SavedMediaName.GAME_RUSSIAN_ROULETTE)
        should_notify_of_turn = True

    game.board = russian_roulette.get_board_json()
    game.save()

    if should_notify_of_turn:
        await game_service.notify_game_turn(context, game, russian_roulette.game_turn)


def get_outbound_keyboard(game: Game, russian_roulette: RussianRoulette) -> list[list[Keyboard]]:
    """
    Get the outbound keyboard
    :param game: The game object
    :param russian_roulette: The russian roulette object
    :return: The outbound keyboard
    """

    outbound_keyboard: list[list[Keyboard]] = []

    for row_index, row in enumerate(russian_roulette.cylinder):
        keyboard_line: list[Keyboard] = []
        for chamber_index, chamber in enumerate(row):
            # Is center chamber
            if russian_roulette.is_chamber_center(row_index, chamber_index):
                keyboard_line.append(Keyboard(Emoji.CENTER_CHAMBER))

            else:
                button_info = {GameRRReservedKeys.GAME_ID: game.id,
                               GameRRReservedKeys.POSITION: (row_index, chamber_index)}
                if row_index == russian_roulette.bullet_x and chamber_index == russian_roulette.bullet_y and \
                        Env.RUSSIAN_ROULETTE_SHOW_BULLET_LOCATION.get_bool():
                    emoji = Emoji.FIRED_BULLET_CHAMBER
                elif chamber == RRChamberStatus.NOT_FIRED:
                    emoji = Emoji.NOT_FIRED_CHAMBER
                else:
                    if russian_roulette.bullet_x == row_index and russian_roulette.bullet_y == chamber_index:
                        emoji = Emoji.FIRED_BULLET_CHAMBER
                    else:
                        emoji = Emoji.FIRED_EMPTY_CHAMBER

                keyboard_line.append(Keyboard(emoji, info=button_info, screen=Screen.GRP_RUSSIAN_ROULETTE_GAME))

        outbound_keyboard.append(keyboard_line)

    return outbound_keyboard


def get_board(game: Game) -> Tuple[Game, RussianRoulette]:
    """
    Get the board
    :param game: The game object
    :return: The board
    """

    # Create board
    if game.board is None:
        russian_roulette = RussianRoulette()
        game.board = russian_roulette.get_board_json()
        game.save()
        return game, russian_roulette

    russian_roulette_dict = json.loads(game.board)
    return game, RussianRoulette(**russian_roulette_dict)


def get_choice_text(bullet_shot: bool) -> str:
    """
    Get the choice text
    :param bullet_shot: If the bullet was shot
    :return: The text
    """

    if bullet_shot:
        return phrases.RUSSIAN_ROULETTE_GAME_BULLET_SHOT

    return phrases.RUSSIAN_ROULETTE_GAME_BULLET_NOT_SHOT


def get_specific_text(game: Game, russian_roulette: RussianRoulette) -> str:
    """
    Get the text
    :param game: The game object
    :param russian_roulette: The russian roulette object
    :return: The text
    """

    return game_service.get_text(game, russian_roulette.is_finished(), russian_roulette.get_outcome(),
                                 russian_roulette.get_user_turn(game))
