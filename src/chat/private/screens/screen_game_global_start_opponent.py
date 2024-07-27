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
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.date_service import datetime_is_after, get_remaining_duration
from src.service.game_service import (
    get_game_from_keyboard,
    collect_game_wagers_and_set_in_progress,
    get_text,
)
from src.service.message_service import (
    full_message_send,
    get_yes_no_keyboard,
    full_media_send,
)


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

    game_status: GameStatus = GameStatus(game.status)
    game_type: GameType = GameType(game.type)

    # Challenger trying to accept this own challenge, simply redirect
    if game.is_challenger(user):
        await dispatch_game(update, context, user, inbound_keyboard, game)
        return

    # Challenge has an opponent
    if game.opponent is not None:
        # Accepted by another player
        if not game.is_player(user):
            await full_message_send(context, phrases.GAME_GLOBAL_ALREADY_ACCEPTED, update=update)
            return

        await dispatch_game(update, context, user, inbound_keyboard, game)
        return

    if game_status is not GameStatus.IN_PROGRESS:
        await full_message_send(context, phrases.ITEM_IN_WRONG_STATUS, update=update)
        return

    if user.game_accept_global_cooldown_end_date and datetime_is_after(
        user.game_accept_global_cooldown_end_date
    ):
        ot_text = phrases.GAME_GLOBAL_COOLDOWN.format(
            get_remaining_duration(user.game_accept_global_cooldown_end_date)
        )
        await full_message_send(context, ot_text, update=update)
        return

    # Not yet confirmed
    if not inbound_keyboard.has_key(ReservedKeyboardKeys.CONFIRM):
        outbound_keyboard: list[list[Keyboard]] = [
            # Accept button for opponent
            get_yes_no_keyboard(
                screen=Screen.PVT_GAME_GLOBAL_START_OPPONENT,
                yes_text=phrases.KEYBOARD_OPTION_ACCEPT,
                primary_key=game.id,
                no_is_delete_button=True,
            )
        ]
        ot_text = phrases.GAME_GLOBAL_OPPONENT_CONFIRMATION_REQUEST.format(
            game_type.get_description(),
            game.challenger.get_markdown_name(),
            game.get_wager_formatted(),
        )
        await full_media_send(
            context,
            caption=ot_text,
            update=update,
            keyboard=outbound_keyboard,
            saved_media_name=game.get_saved_media_name(),
        )
        return

    # Confirmed (if "No" was pressed, the message would be deleted), collect opponent wager
    game.global_opponent_start_date = datetime.datetime.now()
    await collect_game_wagers_and_set_in_progress(
        update,
        game,
        opponent=user,
        should_remove_bounty_challenger=False,
        should_set_cooldown_challenger=False,
        should_set_global_cooldown_opponent=True,
    )

    # Show challenge accepted alert
    await full_message_send(
        context,
        text=phrases.GAME_GLOBAL_CHALLENGE_ACCEPTED_ALERT,
        update=update,
        answer_callback=True,
    )

    ot_text = get_text(game, False, is_for_group_global=True)
    outbound_keyboard: list[list[Keyboard]] = [
        # Play as global button
        [
            Keyboard(
                phrases.GRP_KEY_GAME_PLAY,
                info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: game.id},
                screen=Screen.PVT_GAME_GLOBAL_START_OPPONENT,
                is_deeplink=True,
            )
        ],
    ]

    # Update group message if present
    if game.group_chat is not None:
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

    # If is guess game, then also edit the message that was accepted in private chat
    if game.is_guess_based():
        context.application.create_task(
            full_media_send(
                context,
                caption=ot_text,
                keyboard=outbound_keyboard,
                edit_only_caption_and_keyboard=True,
                update=update,
            )
        )

    # Opponent just started, first hint issued now
    game.last_hint_opponent_date = datetime.datetime.now()
    game.save()

    await dispatch_game(
        update, context, user, inbound_keyboard, game, should_start_immediately=True
    )
