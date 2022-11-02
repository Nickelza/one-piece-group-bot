from strenum import StrEnum
from telegram import Update, Message
from telegram.ext import CallbackContext

import resources.Environment as Env
import resources.phrases as phrases
from src.model.Game import Game
from src.model.User import User
from src.model.enums.Command import Command
from src.model.enums.GameStatus import GameStatus
from src.model.enums.Screen import Screen
from src.model.error.CustomException import OpponentValidationException
from src.model.error.GroupChatError import GroupChatError, GroupChatException
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_amount_from_command, validate_amount
from src.service.cron_service import cron_datetime_difference
from src.service.message_service import full_message_send, mention_markdown_user, get_message_url


class GameReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    GAME_ID = 'a'
    GAME_TYPE = 'b'
    CANCEL = 'c'


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

    # Command does not have wager amount
    if len(command.parameters) == 0:
        full_message_send(context, phrases.GAME_NO_WAGER_AMOUNT, update=update, add_delete_button=True)
        return False

    # Wager basic validation, error message is sent by validate_wager
    if not validate_amount(update, context, challenger, command.parameters[0], Env.GAME_MIN_WAGER.get_int()):
        return False

    # Challenger cannot initiate a game
    if not challenger.can_initiate_game:
        ot_text = phrases.GAME_CANNOT_INITIATE.format(cron_datetime_difference(Env.CRON_RESET_CAN_INITIATE_GAME.get()))

        outbound_keyboard: list[list[Keyboard]] = [[]]
        pending_games: list[Game] = Game.select().where(Game.challenger == challenger,
                                                        Game.status not in GameStatus.get_finished())
        for game in pending_games:
            outbound_keyboard.append([Keyboard(phrases.GAME_PENDING_KEY,
                                               url=get_message_url(Env.OPD_GROUP_ID.get_int(), game.message_id))])

        full_message_send(context, ot_text, update=update, keyboard=outbound_keyboard, add_delete_button=True)
        return False

    # Opponent validation
    try:
        # Opponent is not in the minimum required location
        if not opponent.location_level >= Env.REQUIRED_LOCATION_LEVEL_GAME.get_int():
            raise OpponentValidationException()

        # Opponent is arrested
        if opponent.is_arrested():
            raise OpponentValidationException()

    except OpponentValidationException as ove:
        if ove.message is not None:
            full_message_send(context, ove.message, update)
        else:
            full_message_send(context, phrases.GAME_CANNOT_CHALLENGE_USER, update=update, add_delete_button=True)
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
        raise GroupChatException(GroupChatError.USER_NOT_IN_DB)

    # Validate the request
    if not validate(update, context, user, opponent, command):
        return

    # Create game
    game: Game = Game()
    game.challenger = user
    game.opponent = opponent
    game.wager = get_amount_from_command(command.parameters[0])
    game.save()

    user.bounty -= game.wager
    user.pending_bounty += game.wager
    user.can_initiate_game = False

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
    button_info: dict = {GameReservedKeys.GAME_ID: game.id, GameReservedKeys.GAME_TYPE: GameType.ROCK_PAPER_SCISSORS}
    btn_rps: Keyboard = Keyboard(phrases.ROCK_PAPER_SCISSORS_GAME_NAME, info=button_info,
                                 screen=Screen.GRP_GAME_SELECTION)
    inline_keyboard.append([btn_rps])

    # Russian Roulette
    button_info = {GameReservedKeys.GAME_ID: game.id, GameReservedKeys.GAME_TYPE: GameType.RUSSIAN_ROULETTE}
    btn_rr: Keyboard = Keyboard(phrases.RUSSIAN_ROULETTE_GAME_NAME, info=button_info,
                                screen=Screen.GRP_GAME_SELECTION)
    inline_keyboard.append([btn_rr])

    # Delete button, can't be replaced by add_delete_button because wagers have to be returned
    inline_keyboard.append([Keyboard(phrases.KEYBOARD_OPTION_CANCEL, info={GameReservedKeys.GAME_ID: game.id,
                                                                           GameReservedKeys.CANCEL: True},
                                     screen=Screen.GRP_GAME_SELECTION)])

    ot_text = phrases.GAME_CHOOSE_GAME.format(mention_markdown_user(opponent))
    message: Message = full_message_send(context, ot_text, update=update, keyboard=inline_keyboard)
    game.message_id = message.message_id
    game.save()
