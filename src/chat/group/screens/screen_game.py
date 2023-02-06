from datetime import datetime
from enum import StrEnum

from telegram import Update, Message
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.model.Game import Game
from src.model.Group import Group
from src.model.Topic import Topic
from src.model.User import User
from src.model.enums.Command import Command
from src.model.enums.GameStatus import GameStatus
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.error.CustomException import OpponentValidationException
from src.model.error.GroupChatError import GroupChatError, GroupChatException
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_amount_from_string, validate_amount
from src.service.cron_service import get_remaining_time
from src.service.devil_fruit_service import get_datetime
from src.service.message_service import full_message_send, mention_markdown_user, get_message_url


class GameReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    GAME_ID = 'a'
    GAME_TYPE = 'b'
    CANCEL = 'c'


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE, challenger: User, opponent: User,
                   command: Command) -> bool:
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
        await full_message_send(context, phrases.GAME_NO_WAGER_AMOUNT, update=update, add_delete_button=True)
        return False

    # Wager basic validation, error message is sent by validate_wager
    if not await validate_amount(update, context, challenger, command.parameters[0], Env.GAME_MIN_WAGER.get_int()):
        return False

    # Challenger cannot initiate a game
    if challenger.game_cooldown_end_date and challenger.game_cooldown_end_date > datetime.now():
        ot_text = phrases.GAME_CANNOT_INITIATE.format(get_remaining_time(challenger.game_cooldown_end_date))

        outbound_keyboard: list[list[Keyboard]] = [[]]
        pending_games: list[Game] = Game.select().where((Game.challenger == challenger) &
                                                        (Game.status.not_in(GameStatus.get_finished())))
        for game in pending_games:
            outbound_keyboard.append([Keyboard(phrases.GAME_PENDING_KEY,
                                               url=get_message_url(game.group, game.topic, game.message_id))])

        await full_message_send(context, ot_text, update=update, keyboard=outbound_keyboard, add_delete_button=True)
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
            await full_message_send(context, ove.message, update)
        else:
            await full_message_send(context, phrases.GAME_CANNOT_CHALLENGE_USER, update=update, add_delete_button=True)
        return False

    return True


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, command: Command, group: Group,
                 topic: Topic) -> None:
    """
    Manage the game screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param command: The command
    :param group: The group
    :param topic: The topic
    :return: None
    """
    opponent: User = User.get_or_none(User.tg_user_id == update.message.reply_to_message.from_user.id)

    if opponent is None:
        raise GroupChatException(GroupChatError.USER_NOT_IN_DB)

    # Validate the request
    if not await validate(update, context, user, opponent, command):
        return

    # Create game
    game: Game = Game()
    game.challenger = user
    game.opponent = opponent
    game.wager = get_amount_from_string(command.parameters[0])
    game.group = group
    game.topic = topic
    game.save()

    user.bounty -= game.wager
    user.pending_bounty += game.wager
    user.game_cooldown_end_date = get_datetime(
        user, DevilFruitAbilityType.GAME_COOLDOWN_DURATION, Env.GAME_COOLDOWN_DURATION.get_int())

    # Display available games
    await display_games(game, update, context, opponent)
    return


async def display_games(game: Game, update: Update, context: ContextTypes.DEFAULT_TYPE, opponent: User) -> None:
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
    message: Message = await full_message_send(context, ot_text, update=update, keyboard=inline_keyboard)
    game.message_id = message.message_id
    game.save()
