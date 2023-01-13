from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import src.model.enums.Command as Command
import src.model.enums.Location as Location
from src.chat.group.screens.screen_bounty_gift import manage as manage_screen_bounty_gift
from src.chat.group.screens.screen_change_region import manage as manage_screen_change_region
from src.chat.group.screens.screen_crew_invite import manage as manage_screen_crew_invite
from src.chat.group.screens.screen_crew_join import manage as manage_screen_crew_join
from src.chat.group.screens.screen_doc_q_game import manage as manage_screen_doc_q_game
from src.chat.group.screens.screen_fight import manage as manage_screen_fight
from src.chat.group.screens.screen_game import manage as manage_screen_game
from src.chat.group.screens.screen_game_opponent_confirmation import manage as manage_screen_game_opponent_confirmation
from src.chat.group.screens.screen_game_rps import manage as manage_screen_game_rps
from src.chat.group.screens.screen_game_rr import manage as manage_screen_game_rr
from src.chat.group.screens.screen_game_selection import manage as manage_screen_game_selection
from src.chat.group.screens.screen_prediction_bet import manage as manage_screen_prediction_bet
from src.chat.group.screens.screen_prediction_bet_remove import manage as manage_screen_prediction_bet_remove
from src.chat.group.screens.screen_prediction_bet_status import manage as manage_screen_prediction_bet_status
from src.chat.group.screens.screen_silence import manage as manage_screen_silence
from src.chat.group.screens.screen_silence_end import manage as manage_screen_silence_end
from src.chat.group.screens.screen_speak import manage as manage_screen_speak
from src.chat.group.screens.screen_status import manage as manage_screen_show_status
from src.model.User import User
from src.model.enums.Notification import DeletedMessageArrestNotification, DeletedMessageMuteNotification, \
    DeletedMessageLocationNotification
from src.model.enums.Screen import Screen
from src.model.error.CustomException import GroupMessageValidationException
from src.model.error.GroupChatError import GroupChatError, GroupChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import add_bounty
from src.service.bounty_service import get_message_belly
from src.service.message_service import delete_message
from src.service.notification_service import send_notification
from src.service.user_service import user_is_muted


async def update_user_bounty(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User) -> None:
    """
    Creates a new user or updates an existing user
    :param update: Telegram update
    :param context: Telegram context
    :param user: User object
    :return: Updated user
    """

    await add_bounty(user, get_message_belly(update, user), context=context, update=update,
                     should_update_location=True)


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, command: Command.Command, user: User,
                 keyboard: Keyboard,
                 target_user: User, is_callback: bool) -> None:
    """
    Main function for the group chat manager
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command to execute
    :param user: User object
    :param keyboard: Keyboard
    :param target_user: The target user in case of a reply
    :param is_callback: True if the message is a callback, False otherwise
    :return: None
    """

    # Insert or update user, with message count
    try:
        # Ignore self bot messages or from linked channel
        if update.effective_user.is_bot or update.message.sender_chat.id == Env.OPD_CHANNEL_ID.get_int():
            return
    except AttributeError:
        pass

    if not await validate(update, context, user, is_callback):
        return

    await update_user_bounty(update, context, user)

    await dispatch_screens(update, context, user, keyboard, command, target_user)


async def dispatch_screens(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, inbound_keyboard: Keyboard,
                           command: Command.Command, target_user: User) -> None:
    """
    Dispatches the different screens
    :param update: Telegram update
    :param context: Telegram context
    :param user: User object
    :param inbound_keyboard: Keyboard to send
    :param command: Command to execute
    :param target_user: The target user in case of a reply
    :return: None
    """

    if command is not Command.ND:
        match command.screen:
            case Screen.GRP_USER_STATUS:  # User status
                await manage_screen_show_status(update, context, command, user)

            case Screen.GRP_DOC_Q_GAME:  # Doc Q Game
                await manage_screen_doc_q_game(update, context, user, keyboard=inbound_keyboard)

            case Screen.GRP_CHANGE_REGION:  # Change region
                await manage_screen_change_region(update, context, user, keyboard=inbound_keyboard, command=command)

            case Screen.GRP_FIGHT:  # Fight
                await manage_screen_fight(update, context, user, keyboard=inbound_keyboard)

            case Screen.GRP_GAME:  # Game
                await manage_screen_game(update, context, user, command)

            case Screen.GRP_GAME_SELECTION:  # Game selection
                await manage_screen_game_selection(update, context, user, inbound_keyboard=inbound_keyboard)

            case Screen.GRP_GAME_OPPONENT_CONFIRMATION:  # Game opponent confirmation
                await manage_screen_game_opponent_confirmation(update, context, user, inbound_keyboard=inbound_keyboard)

            case Screen.GRP_ROCK_PAPER_SCISSORS_GAME:  # Game Rock Paper Scissors
                await manage_screen_game_rps(update, context, user, inbound_keyboard=inbound_keyboard)

            case Screen.GRP_RUSSIAN_ROULETTE_GAME:  # Game Russian Roulette
                await manage_screen_game_rr(update, context, user, inbound_keyboard=inbound_keyboard)

            case Screen.GRP_PREDICTION_BET:  # Prediction bet
                await manage_screen_prediction_bet(update, context, user, command)

            case Screen.GRP_PREDICTION_BET_REMOVE:  # Prediction bet remove
                await manage_screen_prediction_bet_remove(update, context, user, command)

            case Screen.GRP_PREDICTION_BET_STATUS:  # Prediction bet status
                await manage_screen_prediction_bet_status(update, context, user)

            case Screen.GRP_CREW_JOIN:  # Crew join
                await manage_screen_crew_join(update, context, user, inbound_keyboard, target_user)

            case Screen.GRP_CREW_INVITE:  # Crew invite
                await manage_screen_crew_invite(update, context, user, inbound_keyboard, target_user)

            case Screen.GRP_SILENCE:  # Silence
                await manage_screen_silence(update, context, user)

            case Screen.GRP_SILENCE_END:  # Silence end
                await manage_screen_silence_end(update, context, user)

            case Screen.GRP_SPEAK:  # Speak
                await manage_screen_speak(update, context, target_user)

            case Screen.GRP_BOUNTY_GIFT:  # Bounty gift
                await manage_screen_bounty_gift(update, context, user, inbound_keyboard, target_user, command)

            case _:  # Unknown screen
                if update.callback_query is not None:
                    raise GroupChatException(GroupChatError.UNRECOGNIZED_SCREEN)


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, is_callback: bool) -> bool:
    """
    Validates the message, deleting it if it's not valid
    :param update: Telegram update
    :param context: Telegram context
    :param user: User object
    :param is_callback: True if the message is a callback, False otherwise
    :return: True if valid, False otherwise
    """
    # Regular message
    if not is_callback:
        if not await validate_location_level(update, context, user, Location.ND.level):
            return False

    # Stickers
    try:
        if (update.message.sticker is not None
                and not await validate_location_level(update, context, user,
                                                      Env.REQUIRED_LOCATION_LEVEL_SEND_STICKER.get_int())):
            return False
    except AttributeError:
        pass

    # Animations
    try:
        if (update.message.animation is not None
                and not await validate_location_level(update, context, user,
                                                      Env.REQUIRED_LOCATION_LEVEL_SEND_ANIMATION.get_int())):
            return False
    except AttributeError:
        pass

    # Forwarded
    try:
        if (update.message.forward_from is not None
                and not await validate_location_level(update, context, user,
                                                      Env.REQUIRED_LOCATION_LEVEL_FORWARD_MESSAGE.get_int(),
                                                      identifier=str(update.message.forward_from.id),
                                                      allowed_identifiers=Env.WHITELIST_FORWARD_MESSAGE.get_list())):
            return False
    except AttributeError:
        pass

    # Dice emoji
    try:
        if (update.message.dice is not None
                and not await validate_location_level(update, context, user,
                                                      Env.REQUIRED_LOCATION_LEVEL_SEND_DICE_EMOJI.get_int())):
            return False
    except AttributeError:
        pass

    # Inline Bot
    try:
        if (update.message.via_bot is not None
                and not await validate_location_level(update, context, user,
                                                      Env.REQUIRED_LOCATION_LEVEL_USE_INLINE_BOTS.get_int(),
                                                      identifier=str(update.message.via_bot.id),
                                                      allowed_identifiers=Env.WHITELIST_INLINE_BOTS.get_list())):
            return False
    except AttributeError:
        pass

    return True


async def validate_location_level(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, location_level: int,
                                  identifier: str = None, allowed_identifiers: list[str] = None) -> bool:
    """
    Validates the location level of the user
    :param update: Telegram update
    :param context: Telegram context
    :param user: User object
    :param location_level: Location level to validate
    :param identifier: If not None, check if is in the list of allowed identifiers
    :param allowed_identifiers: Identifiers to allow. If not None, identifier must be not None
    :return: True if valid, False otherwise
    """

    if identifier is not None and allowed_identifiers is None:
        raise ValueError('allowed_identifiers must be not None if identifier is not None')

    try:
        if identifier is not None and identifier in allowed_identifiers:
            return True

        if user.is_arrested() and location_level > 1:
            raise GroupMessageValidationException(notification=DeletedMessageArrestNotification())

        if await user_is_muted(user, update):
            raise GroupMessageValidationException(notification=DeletedMessageMuteNotification())

        if user.location_level < location_level:
            raise GroupMessageValidationException(notification=DeletedMessageLocationNotification(user, location_level))

    except GroupMessageValidationException as e:
        await send_notification(context, user, e.notification, should_forward_message=True, update=update)
        await delete_message(update)
        return False

    return True
