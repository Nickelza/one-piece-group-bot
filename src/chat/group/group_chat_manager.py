from datetime import datetime
from typing import Tuple

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import src.model.enums.Command as Command
import src.model.enums.Location as Location
from src.chat.common.screen_change_region import manage as manage_screen_change_region
from src.chat.common.screens.screen_daily_reward import manage as manage_screen_daily_reward
from src.chat.common.screens.screen_daily_reward_prize import (
    manage as manage_screen_daily_reward_prize,
)
from src.chat.common.screens.screen_doc_q_game import manage as manage_screen_doc_q_game
from src.chat.common.screens.screen_game import manage as manage_screen_game
from src.chat.common.screens.screen_game_rps import manage as manage_screen_game_rps
from src.chat.common.screens.screen_game_rr import manage as manage_screen_game_rr
from src.chat.common.screens.screen_game_selection import manage as manage_screen_game_selection
from src.chat.common.screens.screen_status import manage as manage_screen_show_status
from src.chat.group.screens.screen_bounty_gift import manage as manage_screen_bounty_gift
from src.chat.group.screens.screen_bounty_loan import manage as manage_screen_bounty_loan
from src.chat.group.screens.screen_crew_invite import manage as manage_screen_crew_invite
from src.chat.group.screens.screen_crew_join import manage as manage_screen_crew_join
from src.chat.group.screens.screen_devil_fruit_sell import manage as manage_screen_devil_fruit_sell
from src.chat.group.screens.screen_fight import manage as manage_screen_fight
from src.chat.group.screens.screen_game_opponent_confirmation import (
    manage as manage_screen_game_opponent_confirmation,
)
from src.chat.group.screens.screen_plunder import manage as manage_screen_plunder
from src.chat.group.screens.screen_prediction_bet import manage as manage_screen_prediction_bet
from src.chat.group.screens.screen_prediction_bet_remove import (
    manage as manage_screen_prediction_bet_remove,
)
from src.chat.group.screens.screen_prediction_bet_status import (
    manage as manage_screen_prediction_bet_status,
)
from src.chat.group.screens.screen_settings import manage as manage_screen_settings
from src.chat.group.screens.screen_settings_auto_delete import (
    manage as manage_screen_settings_auto_delete,
)
from src.chat.group.screens.screen_settings_features import manage as manage_screen_features
from src.chat.group.screens.screen_silence import manage as manage_screen_silence
from src.chat.group.screens.screen_silence_end import manage as manage_screen_silence_end
from src.chat.group.screens.screen_speak import manage as manage_screen_speak
from src.model.Group import Group
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.Feature import Feature
from src.model.enums.Notification import (
    DeletedMessageArrestNotification,
    DeletedMessageMuteNotification,
    DeletedMessageLocationNotification,
)
from src.model.enums.Screen import Screen
from src.model.error.CustomException import GroupMessageValidationException
from src.model.error.GroupChatError import GroupChatError, GroupChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.devil_fruit_service import release_devil_fruit_to_user
from src.service.group_service import is_main_group, feature_is_enabled
from src.service.message_service import delete_message
from src.service.notification_service import send_notification
from src.service.user_service import user_is_muted


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    command: Command.Command,
    user: User,
    keyboard: Keyboard,
    target_user: User,
    is_callback: bool,
    group_chat: GroupChat,
) -> None:
    """
    Main function for the group chat manager
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command to execute
    :param user: User object
    :param keyboard: Keyboard
    :param target_user: The target user in case of a reply
    :param is_callback: True if the message is a callback, False otherwise
    :param group_chat: The group chat
    :return: None
    """

    group: Group = group_chat.group

    # Get added or removed from group_chat
    added_to_group, removed_from_group = get_added_or_removed_from_group_event(update)
    if removed_from_group:
        group.is_active = False
        group.save()
        return

    if added_to_group:
        group.is_active = True
        group.save()
        command = Command.GRP_SETTINGS_FEATURES

    # Insert or update user, with message count
    try:
        # Ignore self bot messages
        if update.effective_user.is_bot and user is None:
            return
    except AttributeError:
        pass

    # Validate messages only in main group_chat
    if is_main_group(group_chat):
        if feature_is_enabled(group_chat, Feature.MESSAGE_FILTER):
            if not await validate(update, context, user, is_callback, group_chat):
                return
        elif feature_is_enabled(group_chat, Feature.SILENCE):
            if not await validate(
                update, context, user, is_callback, group_chat, check_only_muted=True
            ):
                return

    if command is Command.ND:
        return

    await dispatch_screens(
        update, context, user, keyboard, command, target_user, group_chat, added_to_group
    )


async def dispatch_screens(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    inbound_keyboard: Keyboard,
    command: Command.Command,
    target_user: User,
    group_chat: GroupChat,
    added_to_group: bool,
) -> None:
    """
    Dispatches the different screens

    :param update: Telegram update
    :param context: Telegram context
    :param user: User object
    :param inbound_keyboard: Keyboard to send
    :param command: Command to execute
    :param target_user: The target user in case of a reply
    :param group_chat: The group chat
    :param added_to_group: If the Bot was just added to the group chat
    :return: None
    """

    match command.screen:
        case Screen.GRP_USER_STATUS:  # User status
            await manage_screen_show_status(update, context, command, user, group_chat=group_chat)

        case Screen.GRP_DOC_Q_GAME:  # Doc Q Game
            await manage_screen_doc_q_game(update, context, user, inbound_keyboard, group_chat)

        case Screen.GRP_CHANGE_REGION:  # Change region
            await manage_screen_change_region(
                update, context, user, keyboard=inbound_keyboard, command=command
            )

        case Screen.GRP_FIGHT:  # Fight
            await manage_screen_fight(update, context, user, inbound_keyboard, group_chat)

        case Screen.GRP_GAME:  # Game
            await manage_screen_game(update, context, user, command, group_chat)

        case Screen.GRP_GAME_SELECTION:  # Game selection
            await manage_screen_game_selection(
                update, context, user, inbound_keyboard=inbound_keyboard
            )

        case Screen.GRP_GAME_OPPONENT_CONFIRMATION:  # Game opponent confirmation
            await manage_screen_game_opponent_confirmation(
                update, context, user, inbound_keyboard=inbound_keyboard
            )

        case Screen.GRP_ROCK_PAPER_SCISSORS_GAME:  # Game Rock Paper Scissors
            await manage_screen_game_rps(update, context, user, inbound_keyboard=inbound_keyboard)

        case Screen.GRP_RUSSIAN_ROULETTE_GAME:  # Game Russian Roulette
            await manage_screen_game_rr(update, context, user, inbound_keyboard=inbound_keyboard)

        case Screen.GRP_PREDICTION_BET:  # Prediction bet
            await manage_screen_prediction_bet(update, context, user, command, group_chat)

        case Screen.GRP_PREDICTION_BET_REMOVE:  # Prediction bet remove
            await manage_screen_prediction_bet_remove(update, context, user, command, group_chat)

        case Screen.GRP_PREDICTION_BET_STATUS:  # Prediction bet status
            await manage_screen_prediction_bet_status(update, context, user, group_chat)

        case Screen.GRP_CREW_JOIN:  # Crew join
            await manage_screen_crew_join(update, context, user, inbound_keyboard, target_user)

        case Screen.GRP_CREW_INVITE:  # Crew invite
            await manage_screen_crew_invite(update, context, user, inbound_keyboard, target_user)

        case Screen.GRP_SILENCE:  # Silence
            await manage_screen_silence(update, context, group_chat)

        case Screen.GRP_SILENCE_END:  # Silence end
            await manage_screen_silence_end(update, context, group_chat)

        case Screen.GRP_SPEAK:  # Speak
            await manage_screen_speak(update, context, target_user, group_chat)

        case Screen.GRP_BOUNTY_GIFT:  # Bounty gift
            await manage_screen_bounty_gift(
                update, context, user, inbound_keyboard, target_user, command, group_chat
            )

        case Screen.GRP_SETTINGS_FEATURES:  # Features
            await manage_screen_features(
                update, context, inbound_keyboard, group_chat, added_to_group
            )

        case Screen.GRP_DEVIL_FRUIT_SELL:  # Devil fruit sell
            await manage_screen_devil_fruit_sell(
                update, context, user, inbound_keyboard, target_user, command, group_chat
            )

        case Screen.GRP_BOUNTY_LOAN:  # Bounty loan
            await manage_screen_bounty_loan(
                update, context, user, inbound_keyboard, target_user, command, group_chat
            )

        case Screen.GRP_PLUNDER:  # Plunder
            await manage_screen_plunder(update, context, user, inbound_keyboard, group_chat)

        case Screen.GRP_DAILY_REWARD:  # Daily reward
            await manage_screen_daily_reward(update, context, user, group_chat)

        case Screen.GRP_DAILY_REWARD_PRIZE:  # Daily reward prize
            await manage_screen_daily_reward_prize(update, context, inbound_keyboard)

        case Screen.GRP_SETTINGS:  # Settings
            await manage_screen_settings(update, context)

        case Screen.GRP_SETTINGS_AUTO_DELETE:  # Auto delete
            await manage_screen_settings_auto_delete(update, context, inbound_keyboard, group_chat)

        case _:  # Unknown screen
            if update.callback_query is not None:
                raise GroupChatException(GroupChatError.UNRECOGNIZED_SCREEN)

    if inbound_keyboard is not None:
        # Setting here to avoid regular messages to be counted as interaction
        user.last_system_interaction_date = datetime.now()

        group: Group = group_chat.group
        if (
            feature_is_enabled(group_chat, Feature.DEVIL_FRUIT_APPEARANCE)
            and group.tg_group_username is not None
        ):
            await release_devil_fruit_to_user(update, context, user, group_chat)


async def validate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    is_callback: bool,
    group_chat: GroupChat,
    check_only_muted: bool = False,
) -> bool:
    """
    Validates the message, deleting it if it's not valid
    :param update: Telegram update
    :param context: Telegram context
    :param user: User object
    :param is_callback: True if the message is a callback, False otherwise
    :param group_chat: The group chat
    :param check_only_muted: True if it should validate only if the user is muted, False otherwise
    :return: True if valid, False otherwise
    """
    # Regular message
    if not is_callback:
        if not await validate_location_level(update, context, user, Location.ND.level, group_chat):
            return False

        if check_only_muted:
            return True

    # Stickers
    try:
        if update.message.sticker is not None and not await validate_location_level(
            update, context, user, Env.REQUIRED_LOCATION_LEVEL_SEND_STICKER.get_int(), group_chat
        ):
            return False
    except AttributeError:
        pass

    # Animations
    try:
        if update.message.animation is not None and not await validate_location_level(
            update, context, user, Env.REQUIRED_LOCATION_LEVEL_SEND_ANIMATION.get_int(), group_chat
        ):
            return False
    except AttributeError:
        pass

    # Forwarded
    try:
        if update.message.forward_from is not None and not await validate_location_level(  # FIXME
            update,
            context,
            user,
            Env.REQUIRED_LOCATION_LEVEL_FORWARD_MESSAGE.get_int(),
            group_chat,
            identifier=str(update.message.forward_from.id),
            allowed_identifiers=Env.WHITELIST_FORWARD_MESSAGE.get_list(),
        ):
            return False
    except AttributeError:
        pass

    # Dice emoji
    try:
        if update.message.dice is not None and not await validate_location_level(
            update,
            context,
            user,
            Env.REQUIRED_LOCATION_LEVEL_SEND_DICE_EMOJI.get_int(),
            group_chat,
        ):
            return False
    except AttributeError:
        pass

    # Inline Bot
    try:
        if update.message.via_bot is not None and not await validate_location_level(
            update,
            context,
            user,
            Env.REQUIRED_LOCATION_LEVEL_USE_INLINE_BOTS.get_int(),
            group_chat,
            identifier=str(update.message.via_bot.id),
            allowed_identifiers=Env.WHITELIST_INLINE_BOTS.get_list(),
        ):
            return False
    except AttributeError:
        pass

    return True


async def validate_location_level(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    location_level: int,
    group_chat: GroupChat,
    identifier: str = None,
    allowed_identifiers: list[str] = None,
) -> bool:
    """
    Validates the location level of the user
    :param update: Telegram update
    :param context: Telegram context
    :param user: User object
    :param location_level: Location level to validate
    :param group_chat: The group chat
    :param identifier: If not None, check if is in the list of allowed identifiers
    :param allowed_identifiers: Identifiers to allow. If not None, identifier must be not None
    :return: True if valid, False otherwise
    """

    if identifier is not None and allowed_identifiers is None:
        raise ValueError("allowed_identifiers must be not None if identifier is not None")

    try:
        if identifier is not None and identifier in allowed_identifiers:
            return True

        if user.is_arrested() and location_level > 1:
            raise GroupMessageValidationException(notification=DeletedMessageArrestNotification())

        if user_is_muted(user, group_chat):
            raise GroupMessageValidationException(notification=DeletedMessageMuteNotification())

        if user.location_level < location_level:
            raise GroupMessageValidationException(
                notification=DeletedMessageLocationNotification(user, location_level)
            )

    except GroupMessageValidationException as e:
        await send_notification(
            context, user, e.notification, should_forward_message=True, update=update
        )
        await delete_message(update)
        return False

    return True


def get_added_or_removed_from_group_event(update) -> Tuple[bool, bool]:
    """
    Gets the added or removed from group_chat event

    :param update: Telegram update
    :return: Tuple of added and removed
    """

    added_to_chat = False
    removed_from_chat = False

    try:
        if update.message.left_chat_member.id == Env.BOT_ID.get_int():
            removed_from_chat = True
    except AttributeError:
        pass

    try:
        if update.message.new_chat_members[0].id == Env.BOT_ID.get_int():
            added_to_chat = True
    except (AttributeError, IndexError):
        pass

    return added_to_chat, removed_from_chat
