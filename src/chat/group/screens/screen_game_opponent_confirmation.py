from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.chat.group.screens.screen_game_gol import manage as manage_gol
from src.chat.group.screens.screen_game_pr import manage as manage_pr
from src.chat.group.screens.screen_game_rps import manage as manage_rps
from src.chat.group.screens.screen_game_rr import manage as manage_rr
from src.chat.group.screens.screen_game_shambles import manage as manage_shambles
from src.chat.group.screens.screen_game_ww import manage as manage_ww
from src.model.Game import Game
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.error.GroupChatError import GroupChatError, GroupChatException
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import add_or_remove_bounty
from src.service.devil_fruit_service import get_ability_adjusted_datetime
from src.service.game_service import delete_game, validate_game
from src.service.message_service import mention_markdown_user, full_media_send, full_message_send
from src.service.string_service import get_belly_formatted


class GameOpponentConfirmationReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    GAME_ID = "a"
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

    # User clicked on cancel button or opponent rejected
    if (
        GameOpponentConfirmationReservedKeys.CANCEL in inbound_keyboard.info
        or not inbound_keyboard.info[ReservedKeyboardKeys.CONFIRM]
    ):
        should_delete_message = True

        if ReservedKeyboardKeys.CONFIRM in inbound_keyboard.info:  # Opponent rejected
            should_delete_message = False
            ot_text = phrases.GAME_CHALLENGE_REJECTED.format(mention_markdown_user(game.opponent))
            await full_media_send(
                context,
                caption=ot_text,
                update=update,
                add_delete_button=True,
                authorized_users=[game.challenger, game.opponent],
                edit_only_caption_and_keyboard=True,
            )

        await delete_game(context, game, should_delete_message=should_delete_message)
        user.should_update_model = False
        return

    # Opponent does not have enough bounty
    if user.bounty < game.wager:
        if game.opponent is not None:
            await delete_game(context, game, should_delete_message=False)
            await full_media_send(
                context,
                caption=phrases.ACTION_INSUFFICIENT_BOUNTY.format(get_belly_formatted(game.wager)),
                update=update,
                add_delete_button=True,
                edit_only_caption_and_keyboard=True,
            )
            user.should_update_model = False
            return
        else:  # Open to everyone, alert
            await full_message_send(
                context,
                phrases.ACTION_INSUFFICIENT_BOUNTY.format(get_belly_formatted(game.wager)),
                update=update,
                show_alert=True,
            )
            return

    # Challenger clicked on confirm button
    challenger: User = game.challenger
    if user == challenger:
        await full_message_send(
            context, phrases.KEYBOARD_USE_UNAUTHORIZED, update=update, show_alert=True
        )
        return

    # Wrong status
    if game.get_status() is not GameStatus.AWAITING_OPPONENT_CONFIRMATION:
        raise GroupChatException(GroupChatError.ITEM_IN_WRONG_STATUS)

    # Remove bounty from opponent
    await add_or_remove_bounty(
        user,
        game.wager,
        add=False,
        update=update,
        should_affect_pending_bounty=True,
        should_save=True,
    )

    # Remove bounty from challenger and set cooldown
    await add_or_remove_bounty(
        challenger, game.wager, add=False, should_affect_pending_bounty=True, update=update
    )
    challenger.game_cooldown_end_date = get_ability_adjusted_datetime(
        user, DevilFruitAbilityType.GAME_COOLDOWN_DURATION, Env.GAME_COOLDOWN_DURATION.get_int()
    )
    challenger.save()

    game.wager += game.wager
    game.status = GameStatus.IN_PROGRESS
    game.opponent = user
    # Will save game later to avoid doubling wager without actually starting game

    await dispatch_game(update, context, user, inbound_keyboard, game)


async def dispatch_game(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    inbound_keyboard: Keyboard,
    game: Game,
) -> None:
    """
    Dispatch game
    :param update: The update
    :param context: The context
    :param user: The user
    :param inbound_keyboard: The inbound keyboard
    :param game: The game
    :return: None
    """

    game_type: GameType = GameType(game.type)
    match game_type:
        case GameType.ROCK_PAPER_SCISSORS:
            await manage_rps(update, context, user, inbound_keyboard, game)

        case GameType.RUSSIAN_ROULETTE:
            await manage_rr(update, context, user, inbound_keyboard, game)

        case GameType.SHAMBLES:
            await manage_shambles(update, context, inbound_keyboard, game)

        case GameType.WHOS_WHO:
            await manage_ww(update, context, inbound_keyboard, game)

        case GameType.GUESS_OR_LIFE:
            await manage_gol(update, context, inbound_keyboard, game)

        case GameType.PUNK_RECORDS:
            await manage_pr(update, context, inbound_keyboard, game)

        case _:
            raise GroupChatException(GroupChatError.INVALID_GAME)
