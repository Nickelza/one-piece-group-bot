from telegram import Update
from telegram.ext import CallbackContext

import src.model.enums.Command as Command
from src.chat.private.screens.screen_crew import manage as manage_screen_crew
from src.chat.private.screens.screen_crew_create import manage as manage_screen_crew_create_or_edit
from src.chat.private.screens.screen_crew_disband import manage as manage_screen_crew_disband
from src.chat.private.screens.screen_crew_leave import manage as manage_screen_crew_leave
from src.chat.private.screens.screen_crew_member import manage as manage_screen_crew_member
from src.chat.private.screens.screen_crew_member_remove import manage as manage_screen_crew_member_remove
from src.chat.private.screens.screen_settings import manage as manage_screen_settings
from src.chat.private.screens.screen_settings_notifications import manage as manage_screen_settings_notifications
from src.chat.private.screens.screen_settings_notifications_type import manage as \
    manage_screen_settings_notifications_type
from src.chat.private.screens.screen_settings_notifications_type_edit import manage as \
    manage_screen_settings_notifications_type_edit
from src.chat.private.screens.screen_start import manage as manage_screen_start
from src.chat.private.screens.screen_status import manage as manage_screen_status
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.PrivateChatError import PrivateChatError, PrivateChatException
from src.model.pojo.Keyboard import Keyboard


def manage(update: Update, context: CallbackContext, command: Command.Command, user: User,
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

    dispatch_screens(update, context, command, user, inbound_keyboard)


def dispatch_screens(update: Update, context: CallbackContext, command: Command.Command, user: User,
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

            # Text message but not in edit mode and screen is not start, return
            if user.private_screen_in_edit_id is None and screen is not Screen.PVT_START:
                return

        match screen:
            case Screen.PVT_START:  # Start
                manage_screen_start(update, context)

            case Screen.PVT_SETTINGS:  # Settings
                manage_screen_settings(update, context, inbound_keyboard)

            case Screen.PVT_USER_STATUS:  # Status
                manage_screen_status(update, context, command, inbound_keyboard)

            case Screen.PVT_CREW:  # Crew
                manage_screen_crew(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_CREATE_OR_EDIT:  # Crew Create or Edit
                manage_screen_crew_create_or_edit(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_LEAVE:  # Crew Leave
                manage_screen_crew_leave(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_DISBAND:  # Crew Disband
                manage_screen_crew_disband(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_MEMBER:  # Crew Member
                manage_screen_crew_member(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_MEMBER_REMOVE:  # Crew Member Remove
                manage_screen_crew_member_remove(update, context, inbound_keyboard, user)

            case Screen.PVT_SETTINGS_NOTIFICATIONS:  # Notifications
                manage_screen_settings_notifications(update, context, inbound_keyboard)

            case Screen.PVT_SETTINGS_NOTIFICATIONS_TYPE:  # Notifications Type
                manage_screen_settings_notifications_type(update, context, inbound_keyboard)

            case Screen.PVT_SETTINGS_NOTIFICATIONS_TYPE_EDIT:  # Notifications Type Edit
                manage_screen_settings_notifications_type_edit(update, context, inbound_keyboard, user)

            case _:  # Unknown screen
                if update.callback_query is not None:
                    raise PrivateChatException(PrivateChatError.UNRECOGNIZED_SCREEN)
