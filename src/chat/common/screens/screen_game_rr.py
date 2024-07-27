import json
from datetime import datetime
from enum import StrEnum

from telegram import Update, Message
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
import src.service.game_service as game_service
from src.model.Game import Game
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.MessageSource import MessageSource
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.Screen import Screen
from src.model.game.GameBoard import GameBoard
from src.model.game.GameOutcome import GameOutcome
from src.model.game.GameTurn import GameTurn
from src.model.game.russianroulette.RussianRoulette import RussianRoulette
from src.model.game.russianroulette.RussianRouletteChamberStatus import (
    RussianRouletteChamberStatus as RRChamberStatus,
)
from src.model.pojo.Keyboard import Keyboard
from src.service.game_service import edit_other_player_message, enqueue_auto_move
from src.service.message_service import full_message_send, full_media_send, get_message_source


class GameRRReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    GAME_ID = "a"
    POSITION = "b"  # Tuple


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    inbound_keyboard: Keyboard,
    game: Game = None,
    is_auto_move: bool = False,
    edit_message_id: int = None,
) -> None:
    """
    Manage the Russian Roulette screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The inbound keyboard
    :param game: The game object
    :param is_auto_move: If the interaction is from auto move
    :param edit_message_id: Message to be edited. Useful for when a user does not interact with the private game before
        auto-move is triggered, since the message tied with the update would be the start command
    :return: None
    """

    # Get the game from validation, will handle error messages
    game = await game_service.validate_game(update, context, inbound_keyboard, game)
    if game is None:
        return

    all_boards: list[RussianRoulette] = await get_all_boards(game, user)
    board: RussianRoulette = all_boards[0]
    other_board: RussianRoulette = all_boards[1]
    challenger_board: RussianRoulette = all_boards[2]
    opponent_board: RussianRoulette = all_boards[3]

    game.last_interaction_date = datetime.now()

    # Not invoked from opponent confirmation
    if inbound_keyboard.screen == get_screen(update):
        # Not user's turn
        if not game.is_global() and not board.is_user_turn(user, game):
            await full_message_send(
                context,
                phrases.GAME_NOT_YOUR_TURN,
                update=update,
                answer_callback=True,
                show_alert=True,
            )
            return

        x, y = inbound_keyboard.info[GameRRReservedKeys.POSITION]
        # Chamber is already fired
        if board.cylinder[x][y] == RRChamberStatus.FIRED:
            await full_message_send(
                context,
                phrases.RUSSIAN_ROULETTE_GAME_CHAMBER_ALREADY_FIRED,
                update=update,
                answer_callback=True,
                show_alert=True,
            )
            return

        # Player finished but need to wait for opponent to finish too
        if board.is_finished():
            await full_message_send(
                context,
                phrases.GAME_GLOBAL_WAIT_FOR_OPPONENT,
                update=update,
                answer_callback=True,
                show_alert=True,
            )
            return

        board.cylinder[x][y] = RRChamberStatus.FIRED

        # Alert showing choice result, if not auto-move
        if not is_auto_move:
            await full_message_send(
                context,
                get_choice_text(board.bullet_is_fired()),
                update=update,
                answer_callback=True,
            )

        game.set_board(board, user)

    # Game is finished
    if board.is_finished(other_board=other_board):
        game_outcome: GameOutcome = board.get_outcome(game.is_challenger(user), other_board)
        game = await game_service.end_game(
            game,
            game_outcome,
            context,
            update=update,
            send_outcome_to_user=(
                game.get_other_player(user) if (game.is_global() or is_auto_move) else None
            ),
        )
        user.should_update_model = False

        # Send result
        message: Message = await full_media_send(
            context,
            caption=get_specific_text(game, board, user, other_board),
            update=update,
            keyboard=get_outbound_keyboard(game, board, update),
            authorized_users=game.get_players(),
            edit_only_caption_and_keyboard=True,
            edit_message_id=edit_message_id,
        )

        # Global game, modify opponent message
        if game.is_global():
            context.application.create_task(
                edit_other_player_message(
                    context,
                    game,
                    user,
                    message.id,
                    get_specific_text(game, challenger_board, game.challenger, opponent_board),
                    get_specific_text(game, opponent_board, game.opponent, challenger_board),
                    get_outbound_keyboard(game, other_board, update),
                )
            )

        return

    if inbound_keyboard.screen == get_screen(update) and not game.is_global():
        # Update turn only on regular interaction
        board.set_turn()

    # Send message
    message: Message = await full_media_send(
        context,
        caption=get_specific_text(game, board, user, other_board),
        update=update,
        keyboard=get_outbound_keyboard(game, board, update),
        authorized_users=game.get_players(),
        saved_media_name=SavedMediaName.GAME_RUSSIAN_ROULETTE,
        edit_message_id=edit_message_id,
    )

    # Global game, modify opponent message
    if game.is_global():
        context.application.create_task(
            edit_other_player_message(
                context,
                game,
                user,
                message.id,
                get_specific_text(game, challenger_board, game.challenger, opponent_board),
                get_specific_text(game, opponent_board, game.opponent, challenger_board),
                get_outbound_keyboard(game, other_board, update),
            )
        )

    game.set_board(board, user)
    game.save()

    if not game.is_global():
        await game_service.notify_game_turn(context, game, board.game_turn)

    # Auto-move
    if not board.is_finished():
        # Group game, arriving from opponent confirmation, auto move for both
        context.application.create_task(
            enqueue_auto_move(
                update, context, game, board.get_user_turn(game), auto_move, message.id
            )
        )


async def get_all_boards(game: Game, user: User) -> [GameBoard, GameBoard, GameBoard, GameBoard]:
    """
    Get all boards
    :param game: The game object
    :param user: The user object
    :return: Current board, other board, challenger board, opponent board
    """
    if not game.is_global():
        board = get_board_challenger(game)
        other_board = None
    else:
        board = (
            get_board_challenger(game) if game.is_challenger(user) else get_board_opponent(game)
        )
        other_board = (
            get_board_opponent(game) if game.is_challenger(user) else get_board_challenger(game)
        )
    if game.is_challenger(user):
        challenger_board = board
        opponent_board = other_board
    else:
        challenger_board = other_board
        opponent_board = board

    return (
        board,
        other_board,
        challenger_board,
        opponent_board,
    )


def get_outbound_keyboard(
    game: Game, russian_roulette: RussianRoulette, update: Update
) -> list[list[Keyboard]]:
    """
    Get the outbound keyboard
    :param game: The game object
    :param russian_roulette: The russian roulette object
    :param update: The update
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
                button_info = {
                    GameRRReservedKeys.GAME_ID: game.id,
                    GameRRReservedKeys.POSITION: (row_index, chamber_index),
                }
                if (
                    row_index == russian_roulette.bullet_x
                    and chamber_index == russian_roulette.bullet_y
                    and Env.RUSSIAN_ROULETTE_SHOW_BULLET_LOCATION.get_bool()
                ):
                    emoji = Emoji.FIRED_BULLET_CHAMBER
                elif chamber == RRChamberStatus.NOT_FIRED:
                    emoji = Emoji.NOT_FIRED_CHAMBER
                else:
                    if (
                        russian_roulette.bullet_x == row_index
                        and russian_roulette.bullet_y == chamber_index
                    ):
                        emoji = Emoji.FIRED_BULLET_CHAMBER
                    else:
                        emoji = Emoji.FIRED_EMPTY_CHAMBER

                keyboard_line.append(Keyboard(emoji, info=button_info, screen=get_screen(update)))

        outbound_keyboard.append(keyboard_line)

    return outbound_keyboard


def get_board_challenger(game: Game) -> RussianRoulette:
    """
    Get the challenger board
    :param game: The game object
    :return: The board
    """

    # Create board
    if game.board is None:
        russian_roulette = RussianRoulette()
        game.board = russian_roulette.get_as_json_string()
        game.save()
        return russian_roulette

    russian_roulette_dict = json.loads(game.board)
    return RussianRoulette(**russian_roulette_dict)


def get_board_opponent(game: Game) -> RussianRoulette:
    """
    Get the opponent board
    :param game: The game object
    :return: The board
    """

    # Create board
    if game.opponent_board is None:
        russian_roulette = RussianRoulette(game_turn=GameTurn.OPPONENT)
        game.opponent_board = russian_roulette.get_as_json_string()
        game.save()
        return russian_roulette

    russian_roulette_dict = json.loads(game.opponent_board)
    return RussianRoulette(**russian_roulette_dict)


def get_choice_text(bullet_shot: bool) -> str:
    """
    Get the choice text
    :param bullet_shot: If the bullet was shot
    :return: The text
    """

    if bullet_shot:
        return phrases.RUSSIAN_ROULETTE_GAME_BULLET_SHOT

    return phrases.RUSSIAN_ROULETTE_GAME_BULLET_NOT_SHOT


def get_specific_text(
    game: Game, board: RussianRoulette, user: User, other_board: RussianRoulette
) -> str:
    """
    Get the text
    :param game: The game object
    :param board: The russian roulette board
    :param user: The user
    :param other_board: The other board
    :return: The text
    """

    is_challenger = game.is_challenger(user)
    is_opponent = game.is_opponent(user)

    extra_text = ""
    if game.is_global():  # Add points text
        extra_text += phrases.GAME_POINTS.format(
            phrases.TEXT_YOUR, board.get_fired_correct_count(), (board.rows * board.columns) - 2
        )
        if game.is_finished() or board.is_finished():
            extra_text += phrases.GAME_POINTS_FINISHED

        # Opponent points
        if game.opponent is not None:
            extra_text += "\n" + phrases.GAME_POINTS.format(
                game.get_other_player(user).get_markdown_mention(),
                other_board.get_fired_correct_count(),
                (board.rows * board.columns) - 2,
            )
            if game.is_finished() or other_board.is_finished():
                extra_text += phrases.GAME_POINTS_FINISHED

            if game.is_finished():
                extra_text += "\n\n"

    challenger_has_finished = (is_challenger and board.is_finished()) or (
        is_opponent and other_board is not None and other_board.is_finished()
    )
    opponent_has_finished = (is_opponent and board.is_finished()) or (
        is_challenger and other_board is not None and other_board.is_finished()
    )

    return game_service.get_text(
        game,
        game.is_finished() or board.is_finished(),
        board.get_outcome(game.is_challenger(user), other_board=other_board),
        board.get_user_turn(game) if not game.is_global() else user,
        text_to_add_before_footer=extra_text,
        challenger_has_finished=challenger_has_finished,
        opponent_has_finished=opponent_has_finished,
    )


def get_screen(update: Update) -> Screen:
    """
    Get the screen
    :param update: The update object
    :return: The screen
    """

    if get_message_source(update) is MessageSource.GROUP:
        return Screen.GRP_RUSSIAN_ROULETTE_GAME

    return Screen.PVT_RUSSIAN_ROULETTE_GAME


async def auto_move(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    game: Game,
    player: User,
    message_id: int,
    previous_game: Game,
) -> None:
    """
    Auto-move for the given player
    :param update: The update
    :param context: The context object
    :param game: The game object
    :param player: The player object
    :param message_id: Identifier of the message to be edited
    :param previous_game: Game object state during enqueue
    :return: None
    """

    if not game.is_global() or game.is_challenger(player):
        board: RussianRoulette = get_board_challenger(game)
        previous_board = get_board_challenger(previous_game)
    else:
        board: RussianRoulette = get_board_opponent(game)
        previous_board = get_board_opponent(previous_game)

    # If the boards state has changed, no need to auto move
    if board.get_as_json_string() != previous_board.get_as_json_string():
        return

    # Craft a mock input and call manage, with the coordinates of the bullet
    mock_keyboard: Keyboard = Keyboard(
        "",
        info={
            GameRRReservedKeys.GAME_ID: game.id,
            GameRRReservedKeys.POSITION: (board.bullet_x, board.bullet_y),
        },
        screen=get_screen(update),
    )

    player = User.get_by_id(player.id)  # Refresh
    await manage(
        update, context, player, mock_keyboard, game, is_auto_move=True, edit_message_id=message_id
    )
