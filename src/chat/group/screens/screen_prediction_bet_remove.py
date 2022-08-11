from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.model.enums.Command import Command
from src.model.enums.PredictionStatus import PredictionStatus
from src.service.message_service import full_message_send
from src.service.prediction_service import refresh, get_prediction_options_user


def validate(update: Update, context: CallbackContext, user: User, command: Command) -> tuple[Prediction,
                                                                                              PredictionOption] | tuple[
                                                                                            None, None]:
    """
    Validate the prediction bet
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param command: The command
    :return: None if validation failed or (prediction, prediction_option) if validation succeeded
    """

    error_tuple = None, None

    if len(command.parameters) > 1:
        full_message_send(context, phrases.PREDICTION_BET_REMOVE_INVALID_FORMAT, update=update, add_delete_button=True)
        return error_tuple

    # Get prediction from message id
    prediction: Prediction = Prediction.get_or_none(Prediction.message_id == update.message.reply_to_message.message_id)
    if prediction is None:
        full_message_send(context, phrases.PREDICTION_NOT_FOUND_IN_REPLY, update=update)
        return error_tuple

    # Prediction does not accept bets withdrawals
    if not prediction.can_withdraw_bet:
        full_message_send(context, phrases.PREDICTION_DOES_NOT_ACCEPT_BETS_WITHDRAWAL, update=update)
        return error_tuple

    # Prediction is not open
    if PredictionStatus(prediction.status) is not PredictionStatus.SENT:
        full_message_send(context, phrases.PREDICTION_CLOSED_FOR_BETS_REMOVAL, update=update)
        return error_tuple

    prediction_options: list[PredictionOption] = prediction.prediction_options
    prediction_options_user: list[PredictionOptionUser] = get_prediction_options_user(prediction, user)

    # User has not bet on this prediction
    if len(prediction_options_user) == 0:
        full_message_send(context, phrases.PREDICTION_BET_USER_HAS_NOT_BET, update=update)
        return error_tuple

    prediction_option = None
    # Option specified
    if len(command.parameters) == 1:
        # Option is not valid
        prediction_option = [prediction_option for prediction_option in prediction_options if
                             str(prediction_option.number) == command.parameters[0]]
        if len(prediction_option) == 0:
            full_message_send(context, phrases.PREDICTION_OPTION_NOT_FOUND.format(command.parameters[0]), update=update)
            return error_tuple

        prediction_option = prediction_option[0]

        # User did not bet on this option
        if len([prediction_option_user for prediction_option_user in prediction_options_user if
                prediction_option_user.prediction_option == prediction_option]) == 0:
            full_message_send(context, phrases.PREDICTION_OPTION_NOT_BET_ON, update=update)
            return error_tuple

    return prediction, prediction_option


def manage(update: Update, context: CallbackContext, user: User, command: Command) -> None:
    """
    Manage the change region request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param command: The command
    :return: None
    """
    validation_tuple = validate(update, context, user, command)

    # Need single assignment to enable IDE type detection
    prediction: Prediction = validation_tuple[0]
    prediction_option: PredictionOption = validation_tuple[1]

    if prediction is None:
        return

    if prediction_option is None:
        # Remove all bets on this prediction
        PredictionOptionUser.delete().where((PredictionOptionUser.prediction == prediction) &
                                            (PredictionOptionUser.user == user)).execute()
        full_message_send(context, phrases.PREDICTION_BET_REMOVE_ALL_SUCCESS, update=update)
    else:
        # Remove bet on this prediction option
        PredictionOptionUser.delete().where((PredictionOptionUser.prediction_option == prediction_option) &
                                            (PredictionOptionUser.user == user)).execute()
        full_message_send(context, phrases.PREDICTION_BET_REMOVE_SUCCESS, update=update)

    # Update prediction text
    refresh(context, prediction)
