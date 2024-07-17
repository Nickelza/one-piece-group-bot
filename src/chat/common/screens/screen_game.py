from datetime import datetime
from enum import StrEnum

from telegram import Update, Message
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.chat.common.screens.screen_daily_reward import get_global_challenges_section_text
from src.model.Game import Game
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.Command import Command
from src.model.enums.GameStatus import GameStatus
from src.model.enums.MessageSource import MessageSource
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.Screen import Screen
from src.model.error.CommonChatError import CommonChatException
from src.model.error.CustomException import OpponentValidationException
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_amount_from_string, validate_amount
from src.service.date_service import get_remaining_duration
from src.service.message_service import (
    full_message_send,
    get_message_url,
    full_media_send,
    get_message_source,
)


class GameReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    GAME_ID = "a"
    GAME_TYPE = "b"
    CANCEL = "c"


async def validate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    challenger: User,
    opponent: User,
    command: Command,
) -> bool:
    """
    Validate the fight request
    :param update: The update object
    :param context: The context object
    :param challenger: The challenger object
    :param opponent: The opponent object
    :param command: The command
    :return: True if the request is valid, False otherwise
    """

    global_challenges_text = get_global_challenges_section_text(challenger)
    # Command does not have wager amount
    if len(command.parameters) == 0:
        await full_message_send(
            context,
            phrases.GAME_NO_WAGER_AMOUNT + global_challenges_text,
            update=update,
            add_delete_button=True,
        )
        return False

    # Wager basic validation, error message is sent by validate_wager
    if not await validate_amount(
        update, context, challenger, command.parameters[0], Env.GAME_MIN_WAGER.get_int()
    ):
        return False

    # Challenger cannot initiate a game
    if challenger.game_cooldown_end_date and challenger.game_cooldown_end_date > datetime.now():
        ot_text = (
            phrases.GAME_CANNOT_INITIATE.format(
                get_remaining_duration(challenger.game_cooldown_end_date)
            )
            + global_challenges_text
        )

        outbound_keyboard: list[list[Keyboard]] = [[]]
        pending_games: list[Game] = Game.select().where(
            (Game.challenger == challenger)
            & (Game.status.not_in(GameStatus.get_finished()))
            & (Game.group_chat.is_null(False))
        )
        for game in pending_games:
            outbound_keyboard.append(
                [
                    Keyboard(
                        phrases.GAME_PENDING_KEY,
                        url=get_message_url(game.message_id, game.group_chat),
                    )
                ]
            )

        await full_message_send(
            context, ot_text, update=update, keyboard=outbound_keyboard, add_delete_button=True
        )
        return False

    # Opponent validation
    if opponent is not None:
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
                await full_message_send(
                    context,
                    phrases.GAME_CANNOT_CHALLENGE_USER,
                    update=update,
                    add_delete_button=True,
                )
            return False

    return True


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    command: Command,
    group_chat: GroupChat = None,
) -> None:
    """
    Manage the game screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param command: The command
    :param group_chat: The group chat
    :return: None
    """
    try:
        opponent: User | None = User.get_or_none(
            User.tg_user_id == update.message.reply_to_message.from_user.id
        )

        if opponent is None:
            raise CommonChatException(phrases.USER_NOT_FOUND)
    except AttributeError:
        opponent = None

    # Validate the request
    if not await validate(update, context, user, opponent, command):
        return

    # Create game
    game: Game = Game()
    game.challenger = user
    game.opponent = opponent
    game.wager = get_amount_from_string(command.parameters[0], user)
    game.group_chat = group_chat
    game.save()

    # Display available games
    await display_games(game, update, context)
    return


async def display_games(game: Game, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Display the available games
    :param game: The game object
    :param update: The update object
    :param context: The context object
    :return: None
    """
    inline_keyboard: list[list[Keyboard]] = [[]]

    # Guess or Life
    button_info: dict = {
        GameReservedKeys.GAME_ID: game.id,
        GameReservedKeys.GAME_TYPE: GameType.GUESS_OR_LIFE,
    }
    btn_gol: Keyboard = Keyboard(
        GameType.GUESS_OR_LIFE.get_name(), info=button_info, screen=get_next_screen(update)
    )
    inline_keyboard.append([btn_gol])

    # Rock Paper Scissors
    button_info: dict = {
        GameReservedKeys.GAME_ID: game.id,
        GameReservedKeys.GAME_TYPE: GameType.ROCK_PAPER_SCISSORS,
    }
    btn_rps: Keyboard = Keyboard(
        GameType.ROCK_PAPER_SCISSORS.get_name(), info=button_info, screen=get_next_screen(update)
    )
    inline_keyboard.append([btn_rps])

    # Punk Records
    button_info: dict = {
        GameReservedKeys.GAME_ID: game.id,
        GameReservedKeys.GAME_TYPE: GameType.PUNK_RECORDS,
    }
    btn_pr: Keyboard = Keyboard(
        GameType.PUNK_RECORDS.get_name(), info=button_info, screen=get_next_screen(update)
    )
    inline_keyboard.append([btn_pr])

    # Russian Roulette
    button_info = {
        GameReservedKeys.GAME_ID: game.id,
        GameReservedKeys.GAME_TYPE: GameType.RUSSIAN_ROULETTE,
    }
    btn_rr: Keyboard = Keyboard(
        GameType.RUSSIAN_ROULETTE.get_name(), info=button_info, screen=get_next_screen(update)
    )
    inline_keyboard.append([btn_rr])

    # Shambles
    button_info = {
        GameReservedKeys.GAME_ID: game.id,
        GameReservedKeys.GAME_TYPE: GameType.SHAMBLES,
    }
    btn_shambles: Keyboard = Keyboard(
        GameType.SHAMBLES.get_name(), info=button_info, screen=get_next_screen(update)
    )
    inline_keyboard.append([btn_shambles])

    # Who's Who
    button_info = {
        GameReservedKeys.GAME_ID: game.id,
        GameReservedKeys.GAME_TYPE: GameType.WHOS_WHO,
    }
    btn_ww: Keyboard = Keyboard(
        GameType.WHOS_WHO.get_name(), info=button_info, screen=get_next_screen(update)
    )
    inline_keyboard.append([btn_ww])

    ot_text = phrases.GAME_CHOOSE_GAME
    message: Message = await full_media_send(
        context,
        saved_media_name=SavedMediaName.GAME,
        caption=ot_text,
        update=update,
        keyboard=inline_keyboard,
        add_delete_button=True,
        authorized_users=[game.challenger],
    )
    game.message_id = message.message_id
    game.save()


def get_next_screen(update: Update) -> Screen:
    """
    Get the screen
    :param update: The update object
    :return: The screen
    """

    if get_message_source(update) is MessageSource.GROUP:
        return Screen.GRP_GAME_SELECTION

    return Screen.PVT_GAME_SELECTION
