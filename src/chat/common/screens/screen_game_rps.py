import json
import random
from datetime import datetime
from enum import StrEnum

from telegram import Update, Message
from telegram.error import BadRequest
from telegram.ext import ContextTypes

import resources.phrases as phrases
import src.service.game_service as game_service
from src.model.Game import Game
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.MessageSource import MessageSource
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.Screen import Screen
from src.model.game.GameOutcome import GameOutcome
from src.model.game.rps.RockPaperScissors import RockPaperScissors
from src.model.game.rps.RockPaperScissorsChoice import RockPaperScissorsChoice as RPSChoice
from src.model.pojo.Keyboard import Keyboard
from src.service.game_service import (
    get_auto_move_warning,
    enqueue_auto_move,
    edit_other_player_message,
    get_global_share_keyboard,
    end_global_game_player,
)
from src.service.message_service import (
    full_message_send,
    mention_markdown_user,
    full_media_send,
    get_message_source,
)
from src.utils.string_utils import get_belly_formatted


class GameRPSReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    GAME_ID = "a"
    CHOICE = "b"


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
    Manage the Rock Paper Scissors game screen
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

    rock_paper_scissors: RockPaperScissors = get_board(game)
    game.last_interaction_date = datetime.now()

    if inbound_keyboard.screen == get_screen(update):
        rps_choice = RPSChoice(inbound_keyboard.info[GameRPSReservedKeys.CHOICE])
        # Save choice
        if user == game.challenger:
            rock_paper_scissors.challenger_choice = rps_choice
        else:
            rock_paper_scissors.opponent_choice = rps_choice

        game.board = rock_paper_scissors.get_as_json_string()
        game.save()

        # Alert showing choice, if not auto-move
        if not is_auto_move:
            await full_message_send(
                context,
                get_choice_text(rps_choice),
                update=update,
                answer_callback=True,
                show_alert=True,
            )

        # Update turn
        rock_paper_scissors.set_turn()

        if game.is_global():
            await end_global_game_player(context, game, is_challenger=game.is_challenger(user))

    # Game is finished
    if rock_paper_scissors.is_finished():
        game_outcome: GameOutcome = rock_paper_scissors.get_outcome()
        await game_service.end_game(
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
            caption=get_text(game, rock_paper_scissors, user),
            update=update,
            keyboard=get_outbound_keyboard(context, game, update, user),
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
                    get_text(game, rock_paper_scissors, game.challenger),
                    get_text(game, rock_paper_scissors, game.opponent),
                    get_outbound_keyboard(context, game, update, user),
                )
            )

        return

    # Send message
    try:
        message: Message = await full_media_send(
            context,
            caption=get_text(game, rock_paper_scissors, user),
            update=update,
            keyboard=get_outbound_keyboard(context, game, update, user),
            authorized_users=game.get_players(),
            saved_media_name=SavedMediaName.GAME_ROCK_PAPER_SCISSORS,
            edit_message_id=edit_message_id,
        )

        # Modify other player message and save current message id
        if game.is_global():
            context.application.create_task(
                edit_other_player_message(
                    context,
                    game,
                    user,
                    message.id,
                    get_text(game, rock_paper_scissors, game.challenger),
                    get_text(game, rock_paper_scissors, game.opponent),
                    get_outbound_keyboard(context, game, update, user),
                )
            )

        # Notify user turn. After message send to avoid double notification in case user changes choice
        await game_service.notify_game_turn(context, game, rock_paper_scissors.game_turn)

        # Auto-move
        if (
            rock_paper_scissors.challenger_choice == RPSChoice.NONE
            or rock_paper_scissors.opponent_choice == RPSChoice.NONE
        ):
            should_auto_move_challenger = False
            should_auto_move_opponent = False

            # Group game, arriving from opponent confirmation, auto move for both
            if not game.is_global():
                if inbound_keyboard.screen != get_screen(update):
                    should_auto_move_challenger = True
                    should_auto_move_opponent = True
            else:
                if (
                    game.is_challenger(user)
                    and rock_paper_scissors.challenger_choice == RPSChoice.NONE
                ):
                    should_auto_move_challenger = True
                elif (
                    game.opponent is not None
                    and not game.is_challenger(user)
                    and rock_paper_scissors.opponent_choice == RPSChoice.NONE
                ):
                    should_auto_move_opponent = True

            if should_auto_move_challenger:
                context.application.create_task(
                    enqueue_auto_move(
                        update, context, game, game.challenger, auto_move, message.id
                    )
                )

            if should_auto_move_opponent:
                extra_wait_time = (
                    0 if not should_auto_move_challenger else 5
                )  # To avoid overlapping message edits
                context.application.create_task(
                    enqueue_auto_move(
                        update,
                        context,
                        game,
                        game.opponent,
                        auto_move,
                        message.id,
                        extra_wait_time=extra_wait_time,
                    )
                )

    except BadRequest:
        # Possible when user changes a choice, so the output message stays the same
        pass


def get_outbound_keyboard(
    context: ContextTypes.DEFAULT_TYPE, game: Game, update: Update, user: User
) -> list[list[Keyboard]]:
    """
    Get the outbound keyboard
    :param context: The context
    :param game: The game object
    :param update: The update object
    :param user: The user
    :return: The outbound keyboard
    """

    outbound_keyboard: list[list[Keyboard]] = []

    if game.is_finished():
        return outbound_keyboard

    keyboard_line: list[Keyboard] = []
    button_info_rock = {
        GameRPSReservedKeys.GAME_ID: game.id,
        GameRPSReservedKeys.CHOICE: RPSChoice.ROCK,
    }
    keyboard_line.append(Keyboard(Emoji.ROCK, info=button_info_rock, screen=get_screen(update)))
    button_info_paper = {
        GameRPSReservedKeys.GAME_ID: game.id,
        GameRPSReservedKeys.CHOICE: RPSChoice.PAPER,
    }
    keyboard_line.append(Keyboard(Emoji.PAPER, info=button_info_paper, screen=get_screen(update)))
    button_info_scissors = {
        GameRPSReservedKeys.GAME_ID: game.id,
        GameRPSReservedKeys.CHOICE: RPSChoice.SCISSORS,
    }
    keyboard_line.append(
        Keyboard(Emoji.SCISSORS, info=button_info_scissors, screen=get_screen(update))
    )
    outbound_keyboard.append(keyboard_line)

    outbound_keyboard += (
        get_global_share_keyboard(context, game)
        if game.challenger_has_finished() and game.is_challenger(user)
        else []
    )

    return outbound_keyboard


def get_board(game: Game) -> RockPaperScissors:
    """
    Get the board
    :param game: The game object
    :return: The board
    """

    # Create board
    if game.board is None:
        rock_paper_scissors = RockPaperScissors()
        game.board = rock_paper_scissors.get_as_json_string()
        game.save()
        return rock_paper_scissors

    rock_paper_scissors_dict = json.loads(game.board)
    return RockPaperScissors(**rock_paper_scissors_dict)


def get_text(game: Game, rock_paper_scissors: RockPaperScissors, player: User) -> str:
    """
    Get the text
    :param game: The game object
    :param rock_paper_scissors: The rock paper scissors object
    :param player: The player
    :return: The text
    """

    if rock_paper_scissors.is_finished():
        if rock_paper_scissors.get_outcome() == GameOutcome.CHALLENGER_WON:
            added_ot_text = phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.challenger))
        elif rock_paper_scissors.get_outcome() == GameOutcome.OPPONENT_WON:
            added_ot_text = phrases.GAME_RESULT_WIN.format(mention_markdown_user(game.opponent))
        else:
            added_ot_text = phrases.GAME_RESULT_DRAW

        choices_text = phrases.ROCK_PAPER_SCISSORS_CHOICES.format(
            mention_markdown_user(game.challenger),
            get_choice_emoji(rock_paper_scissors.challenger_choice),
            mention_markdown_user(game.opponent),
            get_choice_emoji(rock_paper_scissors.opponent_choice),
        )
        added_ot_text = choices_text + added_ot_text
    else:
        if (
            not game.is_global()
            and rock_paper_scissors.challenger_choice == RPSChoice.NONE
            and rock_paper_scissors.opponent_choice == RPSChoice.NONE
        ) or (
            game.is_global()
            and (
                (
                    game.is_challenger(player)
                    and rock_paper_scissors.challenger_choice == RPSChoice.NONE
                )
                or (
                    game.is_opponent(player)
                    and rock_paper_scissors.opponent_choice == RPSChoice.NONE
                )
            )
        ):
            added_ot_text = phrases.GAME_STATUS_AWAITING_CHOICE + get_auto_move_warning(
                add_turn_notification_time=not game.is_global()
            )
        elif game.is_global():
            is_challenger = player == game.challenger

            # Always show choice, since it will be in private chat
            if is_challenger:
                added_ot_text = phrases.ROCK_PAPER_SCISSORS_CHOICE.format(
                    get_choice_emoji(rock_paper_scissors.challenger_choice)
                )
                added_ot_text += phrases.GAME_GLOBAL_PENDING_CHALLENGER
            else:
                added_ot_text = phrases.ROCK_PAPER_SCISSORS_CHOICE.format(
                    get_choice_emoji(rock_paper_scissors.opponent_choice)
                )
                added_ot_text += phrases.ROCK_PAPER_SCISSORS_PENDING_OPPONENT

        elif rock_paper_scissors.challenger_choice == RPSChoice.NONE:
            added_ot_text = phrases.GAME_STATUS_AWAITING_USER_CHOICE.format(
                mention_markdown_user(game.challenger)
            )
        else:
            added_ot_text = phrases.GAME_STATUS_AWAITING_USER_CHOICE.format(
                mention_markdown_user(game.opponent)
            )

    if game.opponent is None:  # Global, no opponent yet available
        return phrases.GAME_TEXT_WITHOUT_PLAYERS.format(
            phrases.ROCK_PAPER_SCISSORS_GAME_NAME,
            phrases.ROCK_PAPER_SCISSORS_GAME_DESCRIPTION,
            get_belly_formatted(game.wager),
            "",
            added_ot_text,
        )

    return phrases.GAME_TEXT.format(
        phrases.ROCK_PAPER_SCISSORS_GAME_NAME,
        phrases.ROCK_PAPER_SCISSORS_GAME_DESCRIPTION,
        mention_markdown_user(game.challenger),
        mention_markdown_user(game.opponent),
        get_belly_formatted(game.wager),
        "",
        added_ot_text,
    )


def get_choice_text(rps_choice: RPSChoice) -> str:
    """
    Get the choice text
    :param rps_choice: The choice
    :return: The text
    """

    match rps_choice:
        case RPSChoice.ROCK:
            return phrases.ROCK_PAPER_SCISSORS_CHOICE.format(
                phrases.ROCK_PAPER_SCISSORS_CHOICE_ROCK
            )
        case RPSChoice.PAPER:
            return phrases.ROCK_PAPER_SCISSORS_CHOICE.format(
                phrases.ROCK_PAPER_SCISSORS_CHOICE_PAPER
            )
        case RPSChoice.SCISSORS:
            return phrases.ROCK_PAPER_SCISSORS_CHOICE.format(
                phrases.ROCK_PAPER_SCISSORS_CHOICE_SCISSORS
            )

        case _:
            raise ValueError(f"Unknown Rock Paper Scissors choice: {rps_choice}")


def get_choice_emoji(rps_choice: RPSChoice) -> str:
    """
    Get the choice emoji
    :param rps_choice: The choice
    :return: The emoji
    """

    match rps_choice:
        case RPSChoice.ROCK:
            return Emoji.ROCK
        case RPSChoice.PAPER:
            return Emoji.PAPER
        case RPSChoice.SCISSORS:
            return Emoji.SCISSORS

        case _:
            raise ValueError(f"Unknown Rock Paper Scissors choice: {rps_choice}")


def get_screen(update: Update) -> Screen:
    """
    Get the screen
    :param update: The update object
    :return: The screen
    """

    if get_message_source(update) is MessageSource.GROUP:
        return Screen.GRP_ROCK_PAPER_SCISSORS_GAME

    return Screen.PVT_ROCK_PAPER_SCISSORS_GAME


async def auto_move(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    game: Game,
    player: User,
    message_id: int,
    _previous_game: Game,  # Unused
) -> None:
    """
    Auto-move for the given player
    :param update: The update
    :param context: The context object
    :param game: The game object
    :param player: The player object
    :param message_id: Identifier of the message to be edited
    :param _previous_game: Game object state during enqueue
    :return: None
    """

    # Check that user has not already made a move
    board: RockPaperScissors = get_board(game)
    if (
        (game.is_challenger(player) and board.challenger_choice != RPSChoice.NONE)
        or game.is_opponent(player)
        and board.opponent_choice != RPSChoice.NONE
    ):
        return

    other_player_choice: RPSChoice = RPSChoice(
        board.opponent_choice if game.is_challenger(player) else board.challenger_choice
    )

    if other_player_choice == RPSChoice.NONE:  # Other player has not yet chosen, so truly random
        choice: RPSChoice = random.choice(list(RPSChoice))
    else:  # Else, choose the losing move
        choice: RPSChoice = other_player_choice.get_losing_choice()

    # Craft a mock input and call manage
    mock_keyboard: Keyboard = Keyboard(
        "",
        info={
            GameRPSReservedKeys.GAME_ID: game.id,
            GameRPSReservedKeys.CHOICE: choice,
        },
        screen=get_screen(update),
    )

    player = User.get_by_id(player.id)  # Refresh
    await manage(
        update, context, player, mock_keyboard, game, is_auto_move=True, edit_message_id=message_id
    )
