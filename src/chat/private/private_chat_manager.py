from datetime import datetime

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import src.model.enums.Command as Command
from resources import phrases
from src.chat.private.screens.screen_bounty_loan import manage as manage_screen_bounty_loan
from src.chat.private.screens.screen_bounty_loan_detail import (
    manage as manage_screen_bounty_loan_detail,
)
from src.chat.private.screens.screen_bounty_loan_detail_forgive import (
    manage as manage_screen_bounty_loan_detail_forgive,
)
from src.chat.private.screens.screen_bounty_loan_detail_pay import (
    manage as manage_screen_bounty_loan_detail_pay,
)
from src.chat.private.screens.screen_crew import manage as manage_screen_crew
from src.chat.private.screens.screen_crew_ability import manage as manage_screen_crew_ability
from src.chat.private.screens.screen_crew_ability_activate import (
    manage as manage_screen_crew_ability_activate,
)
from src.chat.private.screens.screen_crew_ability_activate_confirm import (
    manage as manage_screen_crew_ability_activate_confirm,
)
from src.chat.private.screens.screen_crew_create import manage as manage_screen_crew_create_or_edit
from src.chat.private.screens.screen_crew_davy_back_fight import (
    manage as manage_screen_crew_davy_back_fight,
)
from src.chat.private.screens.screen_crew_davy_back_fight_detail import (
    manage as manage_screen_crew_davy_back_fight_detail,
)
from src.chat.private.screens.screen_crew_davy_back_fight_detail_conscript_opponent import (
    manage as manage_screen_crew_davy_back_fight_detail_conscript_opponent,
)
from src.chat.private.screens.screen_crew_davy_back_fight_detail_participants_select import (
    manage as manage_screen_crew_davy_back_fight_detail_participants_select,
)
from src.chat.private.screens.screen_crew_davy_back_fight_detail_participants_view import (
    manage as manage_screen_crew_davy_back_fight_detail_participants_view,
)
from src.chat.private.screens.screen_crew_davy_back_fight_request import (
    manage as manage_screen_crew_davy_back_fight_request,
)
from src.chat.private.screens.screen_crew_davy_back_fight_request_received import (
    manage as manage_screen_crew_davy_back_fight_request_received,
)
from src.chat.private.screens.screen_crew_disband import manage as manage_screen_crew_disband
from src.chat.private.screens.screen_crew_join_request_received import (
    manage as manage_screen_crew_join_request_received,
)
from src.chat.private.screens.screen_crew_leave import manage as manage_screen_crew_leave
from src.chat.private.screens.screen_crew_level import manage as manage_screen_crew_level
from src.chat.private.screens.screen_crew_level_up import manage as manage_screen_crew_level_up
from src.chat.private.screens.screen_crew_member import manage as manage_screen_crew_member
from src.chat.private.screens.screen_crew_member_detail import (
    manage as manage_screen_crew_member_detail,
)
from src.chat.private.screens.screen_crew_member_detail_captain_promote import (
    manage as manage_screen_crew_member_detail_captain_promote,
)
from src.chat.private.screens.screen_crew_member_detail_first_mate_demote import (
    manage as manage_screen_crew_member_detail_first_mate_demote,
)
from src.chat.private.screens.screen_crew_member_detail_first_mate_promote import (
    manage as manage_screen_crew_member_detail_first_mate_promote,
)
from src.chat.private.screens.screen_crew_member_detail_post_bail import (
    manage as manage_screen_crew_member_detail_post_bail,
)
from src.chat.private.screens.screen_crew_member_detail_remove import (
    manage as manage_screen_crew_member_detail_remove,
)
from src.chat.private.screens.screen_crew_modify import manage as manage_screen_crew_edit
from src.chat.private.screens.screen_crew_modify_davy_back_fight_default_participants import (
    manage as manage_screen_crew_modify_davy_back_fight_default_participants,
)
from src.chat.private.screens.screen_crew_powerup import manage as manage_screen_crew_powerup
from src.chat.private.screens.screen_crew_search import manage as manage_screen_crew_search
from src.chat.private.screens.screen_crew_search_detail import (
    manage as manage_screen_crew_search_detail,
)
from src.chat.private.screens.screen_crew_search_detail_join import (
    manage as manage_screen_crew_search_detail_join,
)
from src.chat.private.screens.screen_devil_fruit import manage as manage_screen_devil_fruit
from src.chat.private.screens.screen_devil_fruit_detail import (
    manage as manage_screen_devil_fruit_detail,
)
from src.chat.private.screens.screen_devil_fruit_detail_discard import (
    manage as manage_screen_devil_fruit_detail_discard,
)
from src.chat.private.screens.screen_devil_fruit_detail_eat import (
    manage as manage_screen_devil_fruit_detail_eat,
)
from src.chat.private.screens.screen_devil_fruit_detail_sell import (
    manage as manage_screen_devil_fruit_detail_sell,
)
from src.chat.private.screens.screen_devil_fruit_shop import (
    manage as manage_screen_devil_fruit_shop,
)
from src.chat.private.screens.screen_devil_fruit_shop_detail import (
    manage as manage_screen_devil_fruit_shop_detail,
)
from src.chat.private.screens.screen_devil_fruit_shop_detail_buy import (
    manage as manage_screen_devil_fruit_shop_detail_buy,
)
from src.chat.private.screens.screen_devil_fruit_shop_detail_remove import (
    manage as manage_screen_devil_fruit_shop_detail_remove,
)
from src.chat.private.screens.screen_fight import manage as manage_screen_fight
from src.chat.private.screens.screen_game_guess_input import (
    manage as manage_screen_game_guess_input,
)
from src.chat.private.screens.screen_logs import manage as manage_screen_logs
from src.chat.private.screens.screen_logs_type import manage as manage_screen_logs_type
from src.chat.private.screens.screen_logs_type_detail import (
    manage as manage_screen_logs_type_detail,
)
from src.chat.private.screens.screen_logs_type_stats import manage as manage_screen_logs_type_stats
from src.chat.private.screens.screen_plunder import manage as manage_screen_plunder
from src.chat.private.screens.screen_prediction import manage as manage_screen_prediction
from src.chat.private.screens.screen_prediction_create import (
    manage as manage_screen_prediction_create,
)
from src.chat.private.screens.screen_prediction_detail import (
    manage as manage_screen_prediction_detail,
)
from src.chat.private.screens.screen_prediction_detail_place_bet import (
    manage as manage_screen_prediction_detail_place_bet,
)
from src.chat.private.screens.screen_prediction_detail_place_bet_send_amount import (
    manage as manage_screen_prediction_detail_place_bet_send_amount,
)
from src.chat.private.screens.screen_prediction_detail_remove_bet import (
    manage as manage_screen_prediction_detail_remove_bet,
)
from src.chat.private.screens.screen_prediction_detail_remove_bet_confirm import (
    manage as manage_screen_prediction_detail_remove_bet_confirm,
)
from src.chat.private.screens.screen_prediction_detail_send_to_group_chat import (
    manage as manage_screen_prediction_detail_send_to_group,
)
from src.chat.private.screens.screen_prediction_detail_set_result import (
    manage as manage_screen_prediction_detail_set_result,
)
from src.chat.private.screens.screen_settings import manage as manage_screen_settings
from src.chat.private.screens.screen_settings_notifications import (
    manage as manage_screen_settings_notifications,
)
from src.chat.private.screens.screen_settings_notifications_type import (
    manage as manage_screen_settings_notifications_type,
)
from src.chat.private.screens.screen_settings_notifications_type_edit import (
    manage as manage_screen_settings_notifications_type_edit,
)
from src.chat.private.screens.screen_settings_timezone import (
    manage as manage_screen_settings_timezone,
)
from src.chat.private.screens.screen_start import manage as manage_screen_start
from src.chat.private.screens.screen_status import manage as manage_screen_status
from src.model.SystemUpdate import SystemUpdate
from src.model.SystemUpdateUser import SystemUpdateUser
from src.model.User import User
from src.model.enums.ContextDataKey import ContextDataKey
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen, ALLOW_SEARCH_INPUT, HAS_CONTEXT_FILTER
from src.model.error.CustomException import UnauthorizedToViewItemException
from src.model.error.PrivateChatError import PrivateChatError, PrivateChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import (
    full_message_send,
    get_message_url,
    escape_valid_markdown_chars,
)


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    command: Command.Command,
    user: User,
    inbound_keyboard: Keyboard,
) -> None:
    """
    Main function for the group chat manager
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command to execute
    :param user: User
    :param inbound_keyboard: Keyboard
    :return: None
    """

    try:
        await dispatch_screens(update, context, command, user, inbound_keyboard)
    except UnauthorizedToViewItemException as e:
        await full_message_send(
            context,
            phrases.LOG_ITEM_DETAIL_NO_PERMISSION if e.message is None else e.message,
            update=update,
            previous_screens=[Screen.PVT_START],
        )


async def dispatch_screens(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    command: Command.Command,
    user: User,
    inbound_keyboard: Keyboard,
) -> None:
    """
    Dispatches the different screens
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command to execute
    :param user: User
    :param inbound_keyboard: Keyboard
    :return: None
    """
    from_deeplink = inbound_keyboard is not None and inbound_keyboard.from_deeplink
    screen: Screen = Screen.UNKNOWN
    if command is not Command.ND:
        screen = command.screen
    elif user.private_screen_list is not None:
        screen = user.get_current_private_screen()

    if screen is not Screen.UNKNOWN:

        # Always add start as first screen
        if (
            inbound_keyboard is not None
            and Screen.PVT_START not in inbound_keyboard.previous_screen_list
            and inbound_keyboard.screen is not Screen.PVT_START
        ):
            inbound_keyboard.previous_screen_list.insert(0, Screen.PVT_START)

        # No longer in Edit mode
        if (screen is not user.get_current_private_screen() or inbound_keyboard is not None) and (
            inbound_keyboard is not None
            and ReservedKeyboardKeys.SCREEN_STEP not in inbound_keyboard.info
        ):
            user.private_screen_in_edit_id = None
            user.private_screen_step = None

        # Update the user's screen
        if inbound_keyboard is not None and not from_deeplink:
            user.update_private_screen_list(
                screen, previous_screen_list=inbound_keyboard.previous_screen_list
            )

            # Screen step
            if ReservedKeyboardKeys.SCREEN_STEP in inbound_keyboard.info:
                user.private_screen_step = inbound_keyboard.info[ReservedKeyboardKeys.SCREEN_STEP]

            # Edit mode
            if ReservedKeyboardKeys.IN_EDIT_ID in inbound_keyboard.info:
                # User private step must be set
                if user.private_screen_step is None:
                    raise PrivateChatException(PrivateChatError.PRIVATE_STEP_NOT_SET)

                user.private_screen_in_edit_id = inbound_keyboard.info[
                    ReservedKeyboardKeys.IN_EDIT_ID
                ]

        else:
            # Back to start, IDE non recognizing from_deeplink means inbound_keyboard is not None
            # so have to check
            if inbound_keyboard is not None and from_deeplink:
                user.update_private_screen_list(
                    screen, previous_screen_list=inbound_keyboard.previous_screen_list
                )
            else:
                user.update_private_screen_list(screen)

                if command is Command.ND or command.name == "":
                    # Text message but not in edit mode and screen is not start, return
                    if not user.in_edit_mode() and screen not in ALLOW_SEARCH_INPUT:
                        return

        # Remove context filters if current screen and none of previous manage filters
        if ContextDataKey.FILTER in context.user_data and inbound_keyboard is not None:
            if screen not in HAS_CONTEXT_FILTER and not any(
                sc in inbound_keyboard.previous_screen_list for sc in HAS_CONTEXT_FILTER
            ):
                user.clear_context_filters(context)

        match screen:
            case Screen.PVT_START:  # Start
                await manage_screen_start(update, context)

            case Screen.PVT_SETTINGS:  # Settings
                await manage_screen_settings(update, context, inbound_keyboard)

            case Screen.PVT_USER_STATUS:  # Status
                await manage_screen_status(update, context, command, user, inbound_keyboard)

            case Screen.PVT_CREW:  # Crew
                await manage_screen_crew(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_ABILITY:  # Crew Ability
                await manage_screen_crew_ability(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_ABILITY_ACTIVATE:  # Crew Ability Activate
                await manage_screen_crew_ability_activate(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_ABILITY_ACTIVATE_CONFIRM:  # Crew Ability Activate Confirm
                await manage_screen_crew_ability_activate_confirm(
                    update, context, inbound_keyboard, user
                )

            case Screen.PVT_CREW_CREATE_OR_EDIT:  # Crew Create or Edit
                await manage_screen_crew_create_or_edit(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_POWERUP:  # Crew Powerup
                await manage_screen_crew_powerup(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_LEVEL:  # Crew Level
                await manage_screen_crew_level(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_LEVEL_UP:  # Crew Level Up
                await manage_screen_crew_level_up(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_MODIFY:  # Crew Edit
                await manage_screen_crew_edit(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_LEAVE:  # Crew Leave
                await manage_screen_crew_leave(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_DISBAND:  # Crew Disband
                await manage_screen_crew_disband(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_MEMBER:  # Crew Member
                await manage_screen_crew_member(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_MEMBER_DETAIL:  # Crew Member Detail
                await manage_screen_crew_member_detail(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_MEMBER_DETAIL_REMOVE:  # Crew Member Remove
                await manage_screen_crew_member_detail_remove(
                    update, context, inbound_keyboard, user
                )

            case (
                Screen.PVT_CREW_MEMBER_DETAIL_FIRST_MATE_PROMOTE
            ):  # Crew Member First Mate Promote
                await manage_screen_crew_member_detail_first_mate_promote(
                    update, context, inbound_keyboard, user
                )

            case Screen.PVT_CREW_MEMBER_DETAIL_FIRST_MATE_DEMOTE:  # Crew Member First Mate Demote
                await manage_screen_crew_member_detail_first_mate_demote(
                    update, context, inbound_keyboard, user
                )

            case Screen.PVT_CREW_MEMBER_DETAIL_POST_BAIL:  # Crew Member Post Bail
                await manage_screen_crew_member_detail_post_bail(
                    update, context, inbound_keyboard, user
                )

            case Screen.PVT_CREW_SEARCH:  # Crew Search
                await manage_screen_crew_search(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_SEARCH_DETAIL:  # Crew Search Detail
                await manage_screen_crew_search_detail(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_SEARCH_DETAIL_JOIN:  # Crew Search Detail Join
                await manage_screen_crew_search_detail_join(
                    update, context, inbound_keyboard, user
                )

            case Screen.PVT_CREW_JOIN_REQUEST_RECEIVED:  # Crew Join Request Received
                await manage_screen_crew_join_request_received(
                    update, context, inbound_keyboard, user
                )

            case Screen.PVT_CREW_DAVY_BACK_FIGHT_REQUEST:  # Crew Davy Back Fight Request
                await manage_screen_crew_davy_back_fight_request(
                    update, context, inbound_keyboard, user
                )

            # Crew Davy Back Fight Request Received
            case Screen.PVT_CREW_DAVY_BACK_FIGHT_REQUEST_RECEIVED:
                await manage_screen_crew_davy_back_fight_request_received(
                    update, context, inbound_keyboard, user
                )

            case Screen.PVT_SETTINGS_NOTIFICATIONS:  # Notifications
                await manage_screen_settings_notifications(update, context, inbound_keyboard)

            case Screen.PVT_SETTINGS_NOTIFICATIONS_TYPE:  # Notifications Type
                await manage_screen_settings_notifications_type(update, context, inbound_keyboard)

            case Screen.PVT_SETTINGS_NOTIFICATIONS_TYPE_EDIT:  # Notifications Type Edit
                await manage_screen_settings_notifications_type_edit(
                    update, context, inbound_keyboard, user
                )

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
                await manage_screen_prediction_detail_place_bet(
                    update, context, inbound_keyboard, user
                )

            case (
                Screen.PVT_PREDICTION_DETAIL_PLACE_BET_SEND_AMOUNT
            ):  # Prediction Detail Place Bet Send Amount
                await manage_screen_prediction_detail_place_bet_send_amount(
                    update, context, inbound_keyboard, user
                )

            case Screen.PVT_PREDICTION_DETAIL_REMOVE_BET:  # Prediction Detail Remove Bet
                await manage_screen_prediction_detail_remove_bet(
                    update, context, inbound_keyboard, user
                )

            case (
                Screen.PVT_PREDICTION_DETAIL_REMOVE_BET_CONFIRM
            ):  # Prediction Detail Remove Bet Confirm
                await manage_screen_prediction_detail_remove_bet_confirm(
                    update, context, inbound_keyboard, user
                )

            case Screen.PVT_PREDICTION_DETAIL_SEND_TO_GROUP:  # Prediction Detail Send To Group
                await manage_screen_prediction_detail_send_to_group(
                    update, context, inbound_keyboard, user
                )

            case Screen.PVT_PREDICTION_DETAIL_SET_RESULT:  # Prediction Detail Set Result
                await manage_screen_prediction_detail_set_result(
                    update, context, inbound_keyboard, user
                )

            case Screen.PVT_PREDICTION_CREATE:  # Prediction Create
                await manage_screen_prediction_create(update, context, inbound_keyboard, user)

            case Screen.PVT_DEVIL_FRUIT:  # Devil Fruit
                await manage_screen_devil_fruit(update, context, inbound_keyboard, user)

            case Screen.PVT_DEVIL_FRUIT_DETAIL:  # Devil Fruit Detail
                await manage_screen_devil_fruit_detail(update, context, inbound_keyboard, user)

            case Screen.PVT_DEVIL_FRUIT_DETAIL_EAT:  # Devil Fruit Detail Eat
                await manage_screen_devil_fruit_detail_eat(update, context, inbound_keyboard, user)

            case Screen.PVT_DEVIL_FRUIT_DETAIL_DISCARD:  # Devil Fruit Detail Discard
                await manage_screen_devil_fruit_detail_discard(
                    update, context, inbound_keyboard, user
                )

            case Screen.PVT_DEVIL_FRUIT_DETAIL_SELL:  # Devil Fruit Detail Sell
                await manage_screen_devil_fruit_detail_sell(
                    update, context, inbound_keyboard, user
                )

            case Screen.PVT_GAME_GUESS_INPUT:  # Guess game input
                await manage_screen_game_guess_input(update, context, inbound_keyboard, user)

            case Screen.PVT_LOGS_TYPE_STATS:  # Logs Type Stats
                await manage_screen_logs_type_stats(update, context, inbound_keyboard, user)

            case Screen.PVT_SETTINGS_TIMEZONE:  # Settings Timezone
                await manage_screen_settings_timezone(update, context, inbound_keyboard, user)

            case Screen.PVT_BOUNTY_LOAN:  # Bounty Loan
                await manage_screen_bounty_loan(update, context, inbound_keyboard, user)

            case Screen.PVT_BOUNTY_LOAN_DETAIL:  # Bounty Loan Detail
                await manage_screen_bounty_loan_detail(update, context, inbound_keyboard, user)

            case Screen.PVT_BOUNTY_LOAN_DETAIL_PAY:  # Bounty Loan Detail Pay
                await manage_screen_bounty_loan_detail_pay(update, context, inbound_keyboard, user)

            case Screen.PVT_BOUNTY_LOAN_DETAIL_FORGIVE:  # Bounty Loan Detail Forgive
                await manage_screen_bounty_loan_detail_forgive(
                    update, context, inbound_keyboard, user
                )

            case Screen.PVT_CREW_DAVY_BACK_FIGHT:  # Crew Davy Back Fight
                await manage_screen_crew_davy_back_fight(update, context, inbound_keyboard, user)

            case Screen.PVT_CREW_DAVY_BACK_FIGHT_DETAIL:  # Crew Davy Back Fight Detail
                await manage_screen_crew_davy_back_fight_detail(
                    update, context, inbound_keyboard, user
                )

            # Crew Davy Back Fight Detail Participants Select
            case Screen.PVT_CREW_DAVY_BACK_FIGHT_DETAIL_PARTICIPANTS_SELECT:
                await manage_screen_crew_davy_back_fight_detail_participants_select(
                    update, context, inbound_keyboard, user
                )

            # Crew Davy Back Fight Detail Participants View
            case Screen.PVT_CREW_DAVY_BACK_FIGHT_DETAIL_PARTICIPANTS_VIEW:
                await manage_screen_crew_davy_back_fight_detail_participants_view(
                    update, context, inbound_keyboard, user
                )

            # Crew Davy Back Fight Detail Conscript Opponent
            case Screen.PVT_CREW_DAVY_BACK_FIGHT_DETAIL_CONSCRIPT_OPPONENT:
                await manage_screen_crew_davy_back_fight_detail_conscript_opponent(
                    update, context, inbound_keyboard, user
                )

            # Crew Modify Davy Back Fight Default Participants
            case Screen.PVT_CREW_MODIFY_DAVY_BACK_FIGHT_DEFAULT_PARTICIPANTS:
                await manage_screen_crew_modify_davy_back_fight_default_participants(
                    update, context, inbound_keyboard, user
                )

            # Devil Fruit Shop
            case Screen.PVT_DEVIL_FRUIT_SHOP:
                await manage_screen_devil_fruit_shop(update, context, inbound_keyboard, user)

            # Devil Fruit Shop detail
            case Screen.PVT_DEVIL_FRUIT_SHOP_DETAIL:
                await manage_screen_devil_fruit_shop_detail(
                    update, context, inbound_keyboard, user
                )

            # Devil Fruit Shop detail buy
            case Screen.PVT_DEVIL_FRUIT_SHOP_DETAIL_BUY:
                await manage_screen_devil_fruit_shop_detail_buy(
                    update, context, inbound_keyboard, user
                )

            # Devil Fruit Shop detail remove
            case Screen.PVT_DEVIL_FRUIT_SHOP_DETAIL_REMOVE:
                await manage_screen_devil_fruit_shop_detail_remove(
                    update, context, inbound_keyboard, user
                )

            # Crew Member Detail Captain Promote
            case Screen.PVT_CREW_MEMBER_DETAIL_CAPTAIN_PROMOTE:
                await manage_screen_crew_member_detail_captain_promote(
                    update, context, inbound_keyboard, user
                )

            case Screen.PVT_FIGHT:
                await manage_screen_fight(update, context, user, inbound_keyboard)

            case Screen.PVT_PLUNDER:
                await manage_screen_plunder(update, context, user, inbound_keyboard)

            case _:  # Unknown screen
                if update.callback_query is not None or screen is not None:
                    raise PrivateChatException(PrivateChatError.UNRECOGNIZED_SCREEN)

        user.last_system_interaction_date = datetime.now()
        await send_system_update_message(update, context, user)


async def send_system_update_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user: User
) -> None:
    """
    Sends a system update message to the user
    :param update: Telegram update
    :param context: Telegram context
    :param user: User
    :return: None
    """

    # Get the system update
    system_update: SystemUpdate = SystemUpdate.get_latest_update()

    if system_update is None:
        return

    # Check if the user already received this system update
    system_update_user: SystemUpdateUser = SystemUpdateUser.get_or_none(
        SystemUpdateUser.system_update == system_update, SystemUpdateUser.user == user
    )

    if system_update_user is not None:
        return

    # Don't send update if user joined after the update was made
    if user.join_date > system_update.date:
        return

    ot_text = phrases.SYSTEM_UPDATE.format(
        escape_valid_markdown_chars(system_update.title),
        escape_valid_markdown_chars(system_update.description),
        get_message_url(chat_id=system_update.chat_id, message_id=system_update.message_id),
    )

    # Add view button
    # Notifications
    inline_keyboard: list[list[Keyboard]] = [[
        Keyboard(
            phrases.KEY_VIEW,
            url=get_message_url(
                chat_id=system_update.chat_id, message_id=system_update.message_id
            ),
        )
    ]]

    system_update_user = SystemUpdateUser()
    system_update_user.system_update = system_update
    system_update_user.user = user

    try:
        # In try except because it should never prevent from updating the user model which happens
        # at script end
        await full_message_send(
            context, ot_text, update=update, keyboard=inline_keyboard, new_message=True
        )
    except TelegramError as e:
        system_update_user.error = str(e)

    system_update_user.save()
