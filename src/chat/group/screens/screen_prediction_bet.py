from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.model.GroupChat import GroupChat
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.model.enums.Command import Command
from src.model.enums.PredictionStatus import PredictionStatus
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_amount_from_string, validate_amount
from src.service.message_service import full_message_send, escape_valid_markdown_chars
from src.service.prediction_service import refresh, get_prediction_options_user, save_prediction_option_user, \
    get_prediction_from_message_id


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, command: Command = None,
                   amount: str = None, inbound_keyboard: Keyboard = None, prediction_option: PredictionOption = None,
                   previous_screens: list[Screen] = None, previous_screen_list_keyboard_info: dict = None,
                   group_chat: GroupChat = None
                   ) -> tuple[Prediction, PredictionOption, int, int] | tuple[None, None, None, None]:
    """
    Validate the prediction bet
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param command: The command
    :param amount: The amount
    :param inbound_keyboard: The inbound keyboard
    :param prediction_option: The prediction option
    :param previous_screens: The previous screens, for the back button if in private chat
    :param previous_screen_list_keyboard_info: The previous screen list keyboard info, for the back button if in private
    :param group_chat: The group chat from which to get the prediction if getting from message id
    :return: None if validation failed or (prediction, prediction_option, wager, option number) if validation succeeded
    """

    error_tuple = None, None, None, None
    add_delete_button = command is not None  # Add delete button if coming from group_chat

    if amount is not None or command is not None:
        if command is not None:
            if len(command.parameters) != 2:
                await full_message_send(context, phrases.PREDICTION_BET_INVALID_FORMAT, update=update,
                                        add_delete_button=add_delete_button, inbound_keyboard=inbound_keyboard,
                                        previous_screens=previous_screens,
                                        previous_screen_list_keyboard_info=previous_screen_list_keyboard_info)
                return error_tuple
            amount = command.parameters[0]

        # Wager basic validation, error message is sent by validate_wager
        if not await validate_amount(update, context, user, amount, Env.PREDICTION_BET_MIN_WAGER.get_int(),
                                     add_delete_button=add_delete_button, inbound_keyboard=inbound_keyboard,
                                     previous_screens=previous_screens,
                                     previous_screen_list_keyboard_info=previous_screen_list_keyboard_info):
            return error_tuple

    # Get prediction from message id
    if prediction_option is None:
        prediction: Prediction = get_prediction_from_message_id(group_chat, update.message.reply_to_message.message_id)
        if prediction is None:
            await full_message_send(context, phrases.PREDICTION_NOT_FOUND_IN_REPLY, update=update,
                                    add_delete_button=add_delete_button, inbound_keyboard=inbound_keyboard,
                                    previous_screens=previous_screens,
                                    previous_screen_list_keyboard_info=previous_screen_list_keyboard_info)
            return error_tuple
    else:
        prediction: Prediction = prediction_option.prediction

    # Prediction is not open
    if PredictionStatus(prediction.status) is not PredictionStatus.SENT:
        await full_message_send(context, phrases.PREDICTION_CLOSED_FOR_BETS, update=update,
                                add_delete_button=add_delete_button, inbound_keyboard=inbound_keyboard,
                                previous_screens=previous_screens,
                                previous_screen_list_keyboard_info=previous_screen_list_keyboard_info)
        return error_tuple

    prediction_options: list[PredictionOption] = prediction.prediction_options

    # Option is not valid
    if command is not None:
        prediction_options = [prediction_option for prediction_option in prediction_options if
                              str(prediction_option.number) == command.parameters[1]]
        if len(prediction_options) == 0:
            await full_message_send(context, phrases.PREDICTION_OPTION_NOT_FOUND.format(
                escape_valid_markdown_chars(command.parameters[1])), update=update, add_delete_button=add_delete_button,
                                    inbound_keyboard=inbound_keyboard, previous_screens=previous_screens,
                                    previous_screen_list_keyboard_info=previous_screen_list_keyboard_info)
            return error_tuple

        prediction_option = prediction_options[0]

    # User has already bet and prediction does not allow multiple bets, unless the user is betting on the same option
    prediction_options_user: list[PredictionOptionUser] = get_prediction_options_user(prediction, user)
    if len(prediction_options_user) > 0 and prediction.allow_multiple_choices is False:
        if prediction_option in prediction_options_user:
            await full_message_send(context, phrases.PREDICTION_ALREADY_BET, update=update,
                                    add_delete_button=add_delete_button, inbound_keyboard=inbound_keyboard,
                                    previous_screens=previous_screens,
                                    previous_screen_list_keyboard_info=previous_screen_list_keyboard_info)
            return error_tuple

    # Prediction does not allow bets withdrawal and user has already bet on this option. This is to avoid a loophole
    # where a user could bet on an option, then add more wager to the same option, updating the wager datetime
    # and triggering his bet to be removed if after the cutoff datetime
    if not prediction.can_withdraw_bet:
        if any(prediction_option_user.prediction_option == prediction_option for prediction_option_user in
               prediction_options_user):
            await full_message_send(context, phrases.PREDICTION_ALREADY_BET_ON_OPTION, update=update,
                                    add_delete_button=add_delete_button, inbound_keyboard=inbound_keyboard,
                                    previous_screens=previous_screens,
                                    previous_screen_list_keyboard_info=previous_screen_list_keyboard_info)
            return error_tuple

    amount_parsed = get_amount_from_string(amount) if amount is not None else 0  # Using 0 to pass validation in PC

    return prediction, prediction_option, amount_parsed, prediction_option.number


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, command: Command,
                 group_chat: GroupChat) -> None:
    """
    Manage the change region request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param command: The command
    :param group_chat: The group chat
    :return: None
    """
    validation_tuple = await validate(update, context, user, command, group_chat=group_chat)

    # Need single assignment to enable IDE type detection
    prediction: Prediction = validation_tuple[0]
    prediction_option: PredictionOption = validation_tuple[1]
    wager: int = validation_tuple[2]
    option_number: int = validation_tuple[3]

    if prediction is None or prediction_option is None or wager is None or option_number is None:
        return

    save_prediction_option_user(prediction_option, user, wager)

    # Send success message
    ot_text = phrases.PREDICTION_BET_SUCCESS + phrases.PREDICTION_BET_HOW_TO_VIEW_BET_STATUS
    await full_message_send(context, ot_text, update=update, add_delete_button=True)

    # Update prediction text
    await refresh(context, prediction, group_chat=group_chat)
