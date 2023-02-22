from peewee import DoesNotExist
from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.group.screens.screen_game_shambles import run_game as run_game_shambles
from src.chat.group.screens.screen_game_ww import run_game as run_game_ww
from src.model.Game import Game
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.error.GroupChatError import GroupChatException
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.game_service import get_game_from_keyboard, guess_game_validate_answer
from src.service.message_service import full_message_send


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the game input screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    if inbound_keyboard is not None:  # From deep link
        try:
            game: Game = get_game_from_keyboard(inbound_keyboard)
        except GroupChatException:
            raise DoesNotExist
    else:  # From private chat
        game: Game = Game.get_by_id(user.private_screen_in_edit_id)

    # User is not a player of the game
    if not game.is_player(user):
        await full_message_send(context, phrases.GAME_INPUT_NOT_PLAYER, update=update)
        return

    # Game is finished
    if GameStatus(game.status).is_finished():
        await full_message_send(context, phrases.GAME_INPUT_GAME_FINISHED, update=update)
        return

    # Game in countdown
    if GameStatus(game.status) is GameStatus.COUNTDOWN_TO_START:
        await full_message_send(context, phrases.GAME_INPUT_COUNTDOWN, update=update)
        return

    if inbound_keyboard is not None:  # From deep link
        match GameType(game.type):
            case GameType.SHAMBLES:
                await run_game_shambles(context, game, send_to_user=user, should_send_to_all_players=False,
                                        schedule_next_send=False)
            case GameType.WHOS_WHO:
                await run_game_ww(context, game, send_to_user=user, should_send_to_all_players=False,
                                  schedule_next_send=False)

            case _:
                raise ValueError(f"Game type {game.type} not supported")

        return

    # Regular input
    await guess_game_validate_answer(update, context, game, user)
