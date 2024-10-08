import datetime

from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.common.screens.screen_game_manage import dispatch_game
from src.model.Game import Game
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.game_service import (
    get_game_from_keyboard,
    collect_game_wagers_and_set_in_progress,
    get_text,
)
from src.service.message_service import full_message_send, mention_markdown_user, full_media_send
from src.utils.string_utils import get_belly_formatted


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the game input screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    game: Game = get_game_from_keyboard(inbound_keyboard)

    # User is not a player of the game
    if not game.is_player(user):
        await full_message_send(context, phrases.GAME_INPUT_NOT_PLAYER, update=update)
        return

    game_status: GameStatus = GameStatus(game.status)

    # May be in progress, may be ended, dunno don't care, let the manage of the game handle it
    if game_status is not GameStatus.AWAITING_OPPONENT_CONFIRMATION:
        await dispatch_game(update, context, user, inbound_keyboard, game)
        return

    # Collect wagers
    game.global_challenger_start_date = datetime.datetime.now()
    await collect_game_wagers_and_set_in_progress(
        update, game, challenger=user, should_remove_bounty_opponent=False
    )

    # Edit group message to show that it's now a global challenge, best effort
    if game.group_chat is not None:
        ot_text = phrases.GAME_REQUEST_OPEN_HEADER.format(
            mention_markdown_user(game.challenger),
            game.get_type().get_name(),
            get_belly_formatted(game.wager),
            game.get_type().get_description(),
        )
        outbound_keyboard: list[list[Keyboard]] = [
            # Start as global button
            [
                Keyboard(
                    phrases.KEYBOARD_OPTION_ACCEPT,
                    info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: game.id},
                    screen=Screen.PVT_GAME_GLOBAL_START_OPPONENT,
                    is_deeplink=True,
                )
            ],
        ]
        context.application.create_task(
            full_media_send(
                context,
                caption=ot_text,
                chat_id=game.group_chat.group.tg_group_id,
                edit_message_id=game.message_id,
                keyboard=outbound_keyboard,
                add_delete_button=True,
                edit_only_caption_and_keyboard=True,
                group_chat=game.group_chat,
                authorized_users=[game.challenger],
            )
        )
    # If global and guess based started in private, edit that message too
    elif game.is_global() and game.is_guess_based():
        ot_text = get_text(game, False, is_for_group_global=True)
        outbound_keyboard: list[list[Keyboard]] = [
            # Play as global button
            [
                Keyboard(
                    phrases.GRP_KEY_GAME_PLAY,
                    info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: game.id},
                    screen=Screen.PVT_GAME_GLOBAL_START_CHALLENGER,
                    is_deeplink=True,
                )
            ],
        ]

        context.application.create_task(
            full_media_send(
                context,
                caption=ot_text,
                keyboard=outbound_keyboard,
                edit_only_caption_and_keyboard=True,
                update=update,
            )
        )

    await dispatch_game(
        update, context, user, inbound_keyboard, game, should_start_immediately=True
    )
