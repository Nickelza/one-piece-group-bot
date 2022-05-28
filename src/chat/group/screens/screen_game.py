from telegram import Update, Message
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.Game import Game
from src.model.User import User
from src.model.enums.Command import Command
from src.model.enums.Location import is_new_world_by_level
from src.model.enums.Screen import Screen
from src.model.error.GroupChatError import GroupChatError
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send, mention_markdown_user


def validate(update: Update, context: CallbackContext, challenger: User, opponent: User, command: Command) -> bool:
    """
    Validate the fight request
    :param update: The update object
    :param context: The context object
    :param challenger: The challenger object
    :param opponent: The opponent object
    :param command: The command
    :return: True if the request is valid, False otherwise
    """

    # Command has wager amount
    if len(command.parameters) > 0:
        try:
            wager_amount: int = get_wager_amount(command.parameters[0])

            # Challenger does not have enough bounty
            if challenger.bounty < wager_amount:
                full_message_send(context, phrases.GAME_INSUFFICIENT_BOUNTY, update=update, add_delete_button=True)
                return False

        except ValueError:
            full_message_send(context, phrases.GAME_INVALID_WAGER_AMOUNT, update=update, add_delete_button=True)
            return False
    else:
        full_message_send(context, phrases.GAME_NO_WAGER_AMOUNT, update=update, add_delete_button=True)
        return False

    # Opponent is not in New World
    if not is_new_world_by_level(opponent.location_level):
        full_message_send(context, phrases.GAME_CANNOT_CHALLENGE_USER, update, add_delete_button=True)
        return False

    return True


def manage(update: Update, context: CallbackContext, user: User, command: Command) -> None:
    """
    Manage the game screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param command: The command
    :return: None
    """
    opponent: User = User.get_or_none(User.tg_user_id == update.message.reply_to_message.from_user.id)

    if opponent is None:
        full_message_send(context, GroupChatError.USER_NOT_IN_DB.build(), update=update)
        return

    # Validate the request
    if not validate(update, context, user, opponent, command):
        return

    # Create game
    game: Game = Game()
    game.challenger = user
    game.opponent = opponent
    game.wager = get_wager_amount(command.parameters[0])
    game.save()

    user.bounty -= game.wager
    user.pending_bounty += game.wager
    user.save()

    # Display available games
    display_games(game, update, context, opponent)
    return


def display_games(game: Game, update: Update, context: CallbackContext, opponent: User) -> None:
    """
    Display the available games
    :param game: The game object
    :param update: The update object
    :param context: The context object
    :param opponent: The opponent object
    :return: None
    """
    inline_keyboard: list[list[Keyboard]] = [[]]

    # Rock Paper Scissors
    button_info: dict = {'a': game.id, 'b': GameType.ROCK_PAPER_SCISSORS.value}
    btn_rps: Keyboard = Keyboard(phrases.ROCK_PAPER_SCISSORS_GAME_NAME, info=button_info,
                                 screen=Screen.GRP_GAME_SELECTION)
    inline_keyboard.append([btn_rps])

    # Russian Roulette
    button_info = {'a': game.id, 'b': GameType.RUSSIAN_ROULETTE.value}
    btn_rr: Keyboard = Keyboard(phrases.RUSSIAN_ROULETTE_GAME_NAME, info=button_info,
                                screen=Screen.GRP_GAME_SELECTION)
    inline_keyboard.append([btn_rr])

    ot_text = phrases.GAME_CHOOSE_GAME.format(mention_markdown_user(opponent))
    message: Message = full_message_send(context, ot_text, update=update, keyboard=inline_keyboard,
                                         add_delete_button=True)
    game.message_id = message.message_id
    game.save()


def get_wager_amount(amount_str: str) -> int:
    """
    Get the wager amount
    :param amount_str: The wager amount
    :return: The wager amount
    """
    amount_str = amount_str.strip().replace(',', '').replace('.', '')
    return int(amount_str)
