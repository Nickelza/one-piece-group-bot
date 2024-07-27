from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.chat.private.screens.screen_game_global_start_challenger import (
    manage as manage_global_game,
)
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.game_service import delete_game, validate_game, enqueue_game_timeout
from src.service.message_service import mention_markdown_user, get_yes_no_keyboard, full_media_send
from src.utils.string_utils import get_belly_formatted


class GameSelectionReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    GAME_ID = "a"
    GAME_TYPE = "b"
    CANCEL = "c"


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, inbound_keyboard: Keyboard
) -> None:
    """
    Manage the game screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    # Get the game from validation, will handle error messages
    game = await validate_game(update, context, inbound_keyboard)
    if game is None:
        return

    # User clicked on cancel button
    if GameSelectionReservedKeys.CANCEL in inbound_keyboard.info:
        await delete_game(context, update, game)
        user.should_update_model = False
        return

    game.type = GameType(inbound_keyboard.info[GameSelectionReservedKeys.GAME_TYPE])
    game.status = GameStatus.AWAITING_OPPONENT_CONFIRMATION
    game.save()

    challenger: User = game.challenger
    opponent: User = game.opponent

    # In private chat, immediately start game
    if game.group_chat is None:
        await manage_global_game(update, context, inbound_keyboard, user)
        return

    if opponent is not None:
        # Direct request to opponent
        ot_text = phrases.GAME_REQUEST.format(
            mention_markdown_user(opponent),
            mention_markdown_user(challenger),
            game.get_type().get_name(),
            get_belly_formatted(game.wager),
            game.get_type().get_description(),
        )
        outbound_keyboard: list[list[Keyboard]] = [
            get_yes_no_keyboard(
                opponent,
                screen=Screen.GRP_GAME_OPPONENT_CONFIRMATION,
                yes_text=phrases.KEYBOARD_OPTION_ACCEPT,
                no_text=phrases.KEYBOARD_OPTION_REJECT,
                primary_key=game.id,
            )
        ]
    else:  # Open to all
        ot_text = phrases.GAME_REQUEST_OPEN.format(
            mention_markdown_user(challenger),
            game.get_type().get_name(),
            get_belly_formatted(game.wager),
            game.get_type().get_description(),
        )
        outbound_keyboard: list[list[Keyboard]] = [
            # Start as global button
            [
                Keyboard(
                    phrases.GRP_KEY_GAME_START_GLOBAL,
                    info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: game.id},
                    screen=Screen.PVT_GAME_GLOBAL_START_CHALLENGER,
                    is_deeplink=True,
                )
            ],
            # Accept button for opponent
            get_yes_no_keyboard(
                screen=Screen.GRP_GAME_OPPONENT_CONFIRMATION,
                yes_text=phrases.KEYBOARD_OPTION_ACCEPT,
                primary_key=game.id,
                exclude_no_button=True,
            ),
        ]

    button_delete_info = {
        GameSelectionReservedKeys.GAME_ID: game.id,
        ReservedKeyboardKeys.AUTHORIZED_USERS: [challenger.id],
        GameSelectionReservedKeys.CANCEL: True,
    }
    outbound_keyboard.append(
        [
            Keyboard(
                phrases.KEYBOARD_OPTION_CANCEL,
                info=button_delete_info,
                screen=Screen.GRP_GAME_OPPONENT_CONFIRMATION,
            )
        ]
    )

    await full_media_send(
        context,
        caption=ot_text,
        update=update,
        keyboard=outbound_keyboard,
        saved_media_name=game.get_saved_media_name(),
    )

    # Enqueue the game for timeout
    context.application.create_task(enqueue_game_timeout(context, update, game))
