from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.model.enums.Command import Command
from src.model.enums.PredictionStatus import PredictionStatus
from src.service.bounty_service import get_amount_from_command, validate_amount
from src.service.message_service import full_message_send, escape_valid_markdown_chars
from src.service.prediction_service import refresh, get_prediction_options_user


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, command: Command
                   ) -> tuple[Prediction, PredictionOption, int, int] | tuple[None, None, None, None]:
    """
    Validate the prediction bet
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param command: The command
    :return: None if validation failed or (prediction, prediction_option, wager, option number) if validation succeeded
    """

    error_tuple = None, None, None, None

    if len(command.parameters) != 2:
        await full_message_send(context, phrases.PREDICTION_BET_INVALID_FORMAT, update=update, add_delete_button=True)
        return error_tuple

    # Wager basic validation, error message is sent by validate_wager
    if not validate_amount(update, context, user, command.parameters[0], Env.PREDICTION_BET_MIN_WAGER.get_int()):
        return error_tuple

    # Get prediction from message id
    prediction: Prediction = Prediction.get_or_none(Prediction.message_id == update.message.reply_to_message.message_id)
    if prediction is None:
        await full_message_send(context, phrases.PREDICTION_NOT_FOUND_IN_REPLY, update=update, add_delete_button=True)
        return error_tuple

    # Prediction is not open
    if PredictionStatus(prediction.status) is not PredictionStatus.SENT:
        await full_message_send(context, phrases.PREDICTION_CLOSED_FOR_BETS, update=update, add_delete_button=True)
        return error_tuple

    prediction_options: list[PredictionOption] = prediction.prediction_options

    # User has already bet and prediction does not allow multiple bets
    prediction_options_user: list[PredictionOptionUser] = get_prediction_options_user(prediction, user)
    if len(prediction_options_user) > 0 and prediction.allow_multiple_choices is False:
        await full_message_send(context, phrases.PREDICTION_ALREADY_BET, update=update, add_delete_button=True)
        return error_tuple

    # Option is not valid
    prediction_option = [prediction_option for prediction_option in prediction_options if
                         str(prediction_option.number) == command.parameters[1]]
    if len(prediction_option) == 0:
        await full_message_send(context, phrases.PREDICTION_OPTION_NOT_FOUND.format(
            escape_valid_markdown_chars(command.parameters[1])), update=update, add_delete_button=True)
        return error_tuple

    return prediction, prediction_option[0], get_amount_from_command(command.parameters[0]), int(command.parameters[1])


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, command: Command) -> None:
    """
    Manage the change region request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param command: The command
    :return: None
    """
    validation_tuple = await validate(update, context, user, command)

    # Need single assignment to enable IDE type detection
    prediction: Prediction = validation_tuple[0]
    prediction_option: PredictionOption = validation_tuple[1]
    wager: int = validation_tuple[2]
    option_number: int = validation_tuple[3]

    if prediction is None or prediction_option is None or wager is None or option_number is None:
        return

    # Find existing prediction option user if it exists
    prediction_option_user: PredictionOptionUser = PredictionOptionUser.get_or_none(
        (PredictionOptionUser.user == user)
        & (PredictionOptionUser.prediction_option == prediction_option))

    # User has already bet on this option, add the wager to the existing bet
    if prediction_option_user is not None:
        prediction_option_user.wager += wager
    else:
        # Create prediction option user
        prediction_option_user = PredictionOptionUser()
        prediction_option_user.prediction = prediction
        prediction_option_user.prediction_option = prediction_option
        prediction_option_user.user = user
        prediction_option_user.wager = wager

    prediction_option_user.date = datetime.now()
    prediction_option_user.save()

    # Remove wager from user balance
    user.bounty -= wager
    user.pending_bounty += wager

    # Send success message
    await full_message_send(context, phrases.PREDICTION_BET_SUCCESS, update=update, add_delete_button=True)

    # Update prediction text
    await refresh(context, prediction)
