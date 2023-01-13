from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.model.enums.Command import Command
from src.model.enums.PredictionStatus import PredictionStatus
from src.service.message_service import full_message_send
from src.service.prediction_service import refresh, get_prediction_options_user


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, command: Command
                   ) -> tuple[Prediction, PredictionOption, list[PredictionOptionUser]] | tuple[None, None, None]:
    """
    Validate the prediction bet
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param command: The command
    :return: None if validation failed or (prediction, prediction_option) if validation succeeded
    """

    error_tuple = None, None, None

    if len(command.parameters) > 1:
        await full_message_send(context, phrases.PREDICTION_BET_REMOVE_INVALID_FORMAT, update=update,
                                add_delete_button=True)
        return error_tuple

    # Get prediction from message id
    prediction: Prediction = Prediction.get_or_none(Prediction.message_id == update.message.reply_to_message.message_id)
    if prediction is None:
        await full_message_send(context, phrases.PREDICTION_NOT_FOUND_IN_REPLY, update=update, add_delete_button=True)
        return error_tuple

    # Prediction does not accept bets withdrawals
    if not prediction.can_withdraw_bet:
        await full_message_send(context, phrases.PREDICTION_DOES_NOT_ACCEPT_BETS_WITHDRAWAL, update=update,
                                add_delete_button=True)
        return error_tuple

    # Prediction is not open
    if PredictionStatus(prediction.status) is not PredictionStatus.SENT:
        await full_message_send(context, phrases.PREDICTION_CLOSED_FOR_BETS_REMOVAL, update=update,
                                add_delete_button=True)
        return error_tuple

    prediction_options: list[PredictionOption] = prediction.prediction_options
    prediction_options_user: list[PredictionOptionUser] = get_prediction_options_user(prediction, user)

    # User has not bet on this prediction
    if len(prediction_options_user) == 0:
        await full_message_send(context, phrases.PREDICTION_BET_USER_HAS_NOT_BET, update=update, add_delete_button=True)
        return error_tuple

    prediction_option = None
    # Option specified
    if len(command.parameters) == 1:
        # Option is not valid
        prediction_option = [prediction_option for prediction_option in prediction_options if
                             str(prediction_option.number) == command.parameters[0]]
        if len(prediction_option) == 0:
            await full_message_send(context, phrases.PREDICTION_OPTION_NOT_FOUND.format(command.parameters[0]),
                                    update=update,
                                    add_delete_button=True)
            return error_tuple

        prediction_option = prediction_option[0]

        # User did not bet on this option
        if len([prediction_option_user for prediction_option_user in prediction_options_user if
                prediction_option_user.prediction_option == prediction_option]) == 0:
            await full_message_send(context, phrases.PREDICTION_OPTION_NOT_BET_ON, update=update,
                                    add_delete_button=True)
            return error_tuple

    return prediction, prediction_option, prediction_options_user


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
    prediction_options_user: list[PredictionOptionUser] = validation_tuple[2]

    if prediction is None:
        return

    if prediction_option is None:
        # Remove all bets on this prediction
        for prediction_option_user in prediction_options_user:
            delete_prediction_option_user(user, prediction_option_user)

        await full_message_send(context, phrases.PREDICTION_BET_REMOVE_ALL_SUCCESS, update=update,
                                add_delete_button=True)
    else:
        # Remove bet on this prediction option
        prediction_option_user: PredictionOptionUser = [
            prediction_option_user for prediction_option_user in prediction_options_user
            if prediction_option_user.prediction_option == prediction_option][0]
        delete_prediction_option_user(user, prediction_option_user)

        await full_message_send(context, phrases.PREDICTION_BET_REMOVE_SUCCESS, update=update, add_delete_button=True)

    # Update prediction text
    await refresh(context, prediction)


def delete_prediction_option_user(user: User, prediction_option_user: PredictionOptionUser) -> None:
    """
    Delete a prediction option user
    :param user: The user object
    :param prediction_option_user: The prediction option user
    :return: None
    """
    # Return wager
    user.pending_bounty -= prediction_option_user.wager
    user.bounty += prediction_option_user.wager

    # Delete prediction option user
    prediction_option_user.delete_instance()
