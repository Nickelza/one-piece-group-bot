from telegram import Update
from telegram.ext import ContextTypes

import src.model.enums.Command as Command
from src.chat.private.screens.screen_crew import manage as manage_screen_crew
from src.chat.private.screens.screen_crew_create import manage as manage_screen_crew_create_or_edit
from src.chat.private.screens.screen_crew_disband import manage as manage_screen_crew_disband
from src.chat.private.screens.screen_crew_leave import manage as manage_screen_crew_leave
from src.chat.private.screens.screen_crew_member import manage as manage_screen_crew_member
from src.chat.private.screens.screen_crew_member_remove import manage as manage_screen_crew_member_remove
from src.chat.private.screens.screen_logs import manage as manage_screen_logs
from src.chat.private.screens.screen_logs_type import manage as manage_screen_logs_type
from src.chat.private.screens.screen_logs_type_detail import manage as manage_screen_logs_type_detail
from src.chat.private.screens.screen_prediction import manage as manage_screen_prediction
from src.chat.private.screens.screen_prediction_detail import manage as manage_screen_prediction_detail
from src.chat.private.screens.screen_prediction_detail_place_bet import \
    manage as manage_screen_prediction_detail_place_bet
from src.chat.private.screens.screen_prediction_detail_place_bet_send_amount import \
    manage as manage_screen_prediction_detail_place_bet_send_amount
from src.chat.private.screens.screen_settings import manage as manage_screen_settings
from src.chat.private.screens.screen_settings_notifications import manage as manage_screen_settings_notifications
from src.chat.private.screens.screen_settings_notifications_type import \
    manage as manage_screen_settings_notifications_type
from src.chat.private.screens.screen_settings_notifications_type_edit import \
    manage as manage_screen_settings_notifications_type_edit
from src.chat.private.screens.screen_start import manage as manage_screen_start
from src.chat.private.screens.screen_status import manage as manage_screen_status
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.PrivateChatError import PrivateChatError, PrivateChatException
from src.model.pojo.Keyboard import Keyboard


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, command: Command.Command, user: User,
                 inbound_keyboard: Keyboard) -> None:
    """
    Main function for the group chat manager
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command to execute
    :param user: User
    :param inbound_keyboard: Keyboard
    :return: None
    """

    await dispatch_screens(update, context, command, user, inbound_keyboard)


async def dispatch_screens(update: Update, context: ContextTypes.DEFAULT_TYPE, command: Command.Command, user: User,
                           inbound_keyboard: Keyboard) -> None:
    """
    Dispatches the different screens
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command to execute
    :param user: User
    :param inbound_keyboard: Keyboard
    :return: None
    """

    screen: Screen = Screen.UNKNOWN
    if command is not Command.ND:
        screen = command.screen
    elif user.private_screen_list is not None:
        screen = user.get_current_private_screen()

    if screen is not Screen.UNKNOWN:

        # No longer in Edit mode
        if screen is not user.get_current_private_screen() or inbound_keyboard is not None:
            user.private_screen_in_edit_id = None
            user.private_screen_step = None

        # Update the user's screen
        if inbound_keyboard is not None:
            user.update_private_screen_list(screen, previous_screen_list=inbound_keyboard.previous_screen_list)

            # Screen step
            if ReservedKeyboardKeys.SCREEN_STEP in inbound_keyboard.info:
                user.private_screen_step = inbound_keyboard.info[ReservedKeyboardKeys.SCREEN_STEP]

            # Edit mode
            if ReservedKeyboardKeys.IN_EDIT_ID in inbound_keyboard.info:
                # User private step must be set
                if user.private_screen_step is None:
                    raise PrivateChatException(PrivateChatError.PRIVATE_STEP_NOT_SET)

                user.private_screen_in_edit_id = inbound_keyboard.info[ReservedKeyboardKeys.IN_EDIT_ID]

        else:
            user.update_private_screen_list(screen)

            if command is Command.ND or command.name == "":
                # Text message but not in edit mode and screen is not start, return
                if not user.in_edit_mode():
                    return

        match screen:
            case Screen.PVT_START:  # Start
                await manage_screen_start(update, context)

            case Screen.PVT_SETTINGS:  # Settings
                await manage_screen_settings(update, context, inbound_keyboard)

            case Screen.PVT_USER_STATUS:  # Status
                await manage_screen_status(update, context, command, user, inbound_keyboard)

            case Screen.PVT_CREW:  # Crew
                await manage_screen_crew(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_CREATE_OR_EDIT:  # Crew Create or Edit
                await manage_screen_crew_create_or_edit(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_LEAVE:  # Crew Leave
                await manage_screen_crew_leave(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_DISBAND:  # Crew Disband
                await manage_screen_crew_disband(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_MEMBER:  # Crew Member
                await manage_screen_crew_member(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_MEMBER_REMOVE:  # Crew Member Remove
                await manage_screen_crew_member_remove(update, context, inbound_keyboard, user)

            case Screen.PVT_SETTINGS_NOTIFICATIONS:  # Notifications
                await manage_screen_settings_notifications(update, context, inbound_keyboard)

            case Screen.PVT_SETTINGS_NOTIFICATIONS_TYPE:  # Notifications Type
                await manage_screen_settings_notifications_type(update, context, inbound_keyboard)

            case Screen.PVT_SETTINGS_NOTIFICATIONS_TYPE_EDIT:  # Notifications Type Edit
                await manage_screen_settings_notifications_type_edit(update, context, inbound_keyboard, user)

            case Screen.PVT_LOGS:  # Logs
                await manage_screen_logs(update, context, inbound_keyboard, user)

            case Screen.PVT_LOGS_TYPE:  # Logs Type
                await manage_screen_logs_type(update, context, inbound_keyboard, user)

            case Screen.PVT_LOGS_TYPE_DETAIL:  # Logs Type Detail
                await manage_screen_logs_type_detail(update, context, inbound_keyboard, user)

            case Screen.PVT_PREDICTION:  # Prediction
                await manage_screen_prediction(update, context, inbound_keyboard, user)

            case Screen.PVT_PREDICTION_DETAIL:  # Prediction Detail
                await manage_screen_prediction_detail(update, context, inbound_keyboard, user)

            case Screen.PVT_PREDICTION_DETAIL_PLACE_BET:  # Prediction Detail Place Bet
                await manage_screen_prediction_detail_place_bet(update, context, inbound_keyboard, user)

            case Screen.PVT_PREDICTION_DETAIL_PLACE_BET_SEND_AMOUNT:  # Prediction Detail Place Bet Send Amount
                await manage_screen_prediction_detail_place_bet_send_amount(update, context, inbound_keyboard, user)

            case _:  # Unknown screen
                if update.callback_query is not None:
                    raise PrivateChatException(PrivateChatError.UNRECOGNIZED_SCREEN)
