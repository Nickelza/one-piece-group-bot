from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.GroupChat import GroupChat
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.model.enums.Command import Command
from src.model.enums.PredictionStatus import PredictionStatus
from src.model.error.CustomException import PredictionException
from src.service.message_service import full_message_send
from src.service.prediction_service import (
    refresh,
    get_prediction_options_user,
    delete_prediction_option_user,
    delete_prediction_option_for_user,
    get_prediction_from_message_id,
)


async def validate(
    update: Update,
    user: User,
    command: Command = None,
    prediction_option: PredictionOption = None,
    group_chat: GroupChat = None,
) -> tuple[Prediction, PredictionOption, list[PredictionOptionUser]]:
    """
    Validate the prediction bet
    :param update: The update object
    :param user: The user object
    :param command: The command. Required if prediction_option is None
    :param prediction_option: The prediction option. Required if command is None
    :param group_chat: The group chat from which to get the prediction if getting from message id
    :return: Raises an exception if the validation fails. Otherwise, returns the prediction, prediction option and
                prediction options the user has bet on
    """

    if prediction_option is None and command is None:
        raise ValueError("Either prediction_option or command must be provided")

    if command is not None:
        if len(command.parameters) > 1:
            raise PredictionException(phrases.PREDICTION_BET_REMOVE_INVALID_FORMAT)

        # Get prediction from message id
        prediction: Prediction = get_prediction_from_message_id(
            group_chat, update.message.reply_to_message.message_id
        )
        if prediction is None:
            raise PredictionException(phrases.PREDICTION_NOT_FOUND_IN_REPLY)
    else:
        prediction: Prediction = prediction_option.prediction

    # Prediction does not accept bets withdrawals
    if not prediction.can_withdraw_bet:
        raise PredictionException(phrases.PREDICTION_DOES_NOT_ACCEPT_BETS_WITHDRAWAL)

    # Prediction is not open
    if PredictionStatus(prediction.status) is not PredictionStatus.SENT:
        raise PredictionException(phrases.PREDICTION_CLOSED_FOR_BETS_REMOVAL)

    prediction_options: list[PredictionOption] = prediction.prediction_options
    prediction_options_user: list[PredictionOptionUser] = get_prediction_options_user(
        prediction, user
    )

    # User has not bet on this prediction
    if len(prediction_options_user) == 0:
        raise PredictionException(phrases.PREDICTION_BET_USER_HAS_NOT_BET)

    if command is not None:
        prediction_option = None
        # Option specified
        if len(command.parameters) == 1:
            # Option is not valid
            prediction_option = [
                prediction_option
                for prediction_option in prediction_options
                if str(prediction_option.number) == command.parameters[0]
            ]
            if len(prediction_option) == 0:
                raise PredictionException(
                    phrases.PREDICTION_OPTION_NOT_FOUND.format(command.parameters[0])
                )

            prediction_option = prediction_option[0]

    if prediction_option is not None:
        # User did not bet on this option
        if (
            len([
                prediction_option_user
                for prediction_option_user in prediction_options_user
                if prediction_option_user.prediction_option == prediction_option
            ])
            == 0
        ):
            raise PredictionException(phrases.PREDICTION_OPTION_NOT_BET_ON)

    return prediction, prediction_option, prediction_options_user


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    command: Command,
    group_chat: GroupChat,
) -> None:
    """
    Manage the change region request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param command: The command
    :param group_chat: The group chat
    :return: None
    """

    try:
        validation_tuple = await validate(update, user, command, group_chat=group_chat)

        # Need single assignment to enable IDE type detection
        prediction: Prediction = validation_tuple[0]
        prediction_option: PredictionOption = validation_tuple[1]
        prediction_options_user: list[PredictionOptionUser] = validation_tuple[2]
    except PredictionException as pe:
        await full_message_send(context, pe.message, update=update, add_delete_button=True)
        return

    if prediction_option is None:
        # Remove all bets on this prediction
        for prediction_option_user in prediction_options_user:
            await delete_prediction_option_user(user, prediction_option_user)

        await full_message_send(
            context,
            phrases.PREDICTION_BET_REMOVE_ALL_SUCCESS,
            update=update,
            add_delete_button=True,
        )
    else:
        # Remove bet on this prediction option
        await delete_prediction_option_for_user(user, prediction_option)

        await full_message_send(
            context, phrases.PREDICTION_BET_REMOVE_SUCCESS, update=update, add_delete_button=True
        )

    # Update prediction text
    await refresh(context, prediction, group_chat=group_chat)
