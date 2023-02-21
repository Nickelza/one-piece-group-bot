from peewee import DoesNotExist
from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.group.screens.screen_game_ww import send_blurred_image, validate_answer
from src.model.Game import Game
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.error.GroupChatError import GroupChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.game_service import get_game_from_keyboard
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

        # User is not a participant of the game
        if not game.is_participant(user):
            await full_message_send(context, phrases.GAME_INPUT_NOT_PARTICIPANT, update=update)
            return

        # Game is finished
        if GameStatus(game.status).is_finished():
            await full_message_send(context, phrases.GAME_INPUT_GAME_FINISHED, update=update)
            return

        # Game in countdown
        if GameStatus(game.status) is GameStatus.COUNTDOWN_TO_START:
            await full_message_send(context, phrases.GAME_INPUT_COUNTDOWN, update=update)
            return

        # Send current blurred
        await send_blurred_image(context, game, send_to_user=user, should_send_to_all_participants=False,
                                 schedule_next_send=False)
        return

    # Regular input
    game: Game = Game.get_by_id(user.private_screen_in_edit_id)
    await validate_answer(update, context, game, user)
