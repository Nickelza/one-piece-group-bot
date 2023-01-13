from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
import src.service.prediction_service as prediction_service
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.model.enums.PredictionStatus import PredictionStatus
from src.service.bounty_service import get_belly_formatted
from src.service.message_service import full_message_send, escape_valid_markdown_chars


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User) -> tuple[Prediction, list[
    PredictionOptionUser]] \
                                                                                      | tuple[None, None]:
    """
    Validate the prediction bet
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :return: None if validation failed or (prediction) if validation succeeded
    """

    error_tuple = None, None

    # Get prediction from message id
    prediction: Prediction = Prediction.get_or_none(Prediction.message_id == update.message.reply_to_message.message_id)
    if prediction is None:
        await full_message_send(context, phrases.PREDICTION_NOT_FOUND_IN_REPLY, update=update, add_delete_button=True)
        return error_tuple

    prediction_options_user: list[PredictionOptionUser] = prediction_service.get_prediction_options_user(prediction,
                                                                                                         user)
    # User has not bet on this prediction
    if len(prediction_options_user) == 0:
        await full_message_send(context, phrases.PREDICTION_BET_USER_HAS_NOT_BET, update=update, add_delete_button=True)
        return error_tuple

    return prediction, prediction_options_user


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User) -> None:
    """
    Manage the change region request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :return: None
    """
    validation_tuple = await validate(update, context, user)

    # Need single assignment to enable IDE type detection
    prediction: Prediction = validation_tuple[0]
    prediction_options_user: list[PredictionOptionUser] = validation_tuple[1]

    if prediction is None:
        return

    total_win_amount = 0
    total_win_count = 0
    total_loss_count = 0
    prediction_status: PredictionStatus = PredictionStatus(prediction.status)
    ot_text = phrases.PREDICTION_STATUS_BETS_HEADER

    for prediction_option_user in prediction_options_user:
        prediction_option: PredictionOption = prediction_option_user.prediction_option

        # Option
        ot_text += phrases.PREDICTION_STATUS_OPTION.format(prediction_option.number,
                                                           escape_valid_markdown_chars(prediction_option.option),
                                                           get_belly_formatted(prediction_option_user.wager))

        # If the prediction results are not set, assume the option is correct
        is_potential = prediction_status is not PredictionStatus.RESULT_SET

        potential_win_amount = prediction_service.get_prediction_option_user_win(prediction_option_user,
                                                                                 is_potential=is_potential)

        potential_win_amount_formatted = get_belly_formatted(potential_win_amount)

        # Result not set, add potential win
        if prediction_status is not PredictionStatus.RESULT_SET:
            ot_text += phrases.PREDICTION_STATUS_POTENTIAL_WIN.format(potential_win_amount_formatted)
        else:
            # Result set, add win or loss amount
            if prediction_option.is_correct:
                ot_text += phrases.PREDICTION_STATUS_RESULT_WIN.format(potential_win_amount_formatted)
                total_win_amount += potential_win_amount
                total_win_count += 1
            else:
                ot_text += phrases.PREDICTION_STATUS_RESULT_LOST
                total_win_amount -= prediction_option_user.wager if not prediction.refund_wager else 0
                total_loss_count += 1

                # Wagers are refunded
                if prediction.refund_wager:
                    ot_text += phrases.PREDICTION_STATUS_RESULT_LOSS_REFUNDED

    # Multiple bet options
    if len(prediction_options_user) > 1:
        # Result set, show net win or loss amount
        if prediction_status is PredictionStatus.RESULT_SET:
            if total_win_amount >= 0:  # Won
                if total_loss_count > 0:  # At least one option was wrong, show net win
                    ot_text += phrases.PREDICTION_STATUS_NET_WIN.format(get_belly_formatted(total_win_amount))
                else:  # All options were correct, show total win
                    ot_text += phrases.PREDICTION_STATUS_TOTAL_WIN.format(get_belly_formatted(total_win_amount))
            else:
                total_loss_amount = abs(total_win_amount)
                if total_win_count > 0:  # At least one option was correct, show net loss
                    ot_text += phrases.PREDICTION_STATUS_NET_LOSS.format(get_belly_formatted(total_loss_amount))
                else:  # All options were wrong, show total loss
                    ot_text += phrases.PREDICTION_STATUS_TOTAL_LOSS.format(get_belly_formatted(total_loss_amount))
        # Open prediction, show command to remove single bet
        elif prediction_status is PredictionStatus.SENT and prediction.can_withdraw_bet:
            ot_text += phrases.PREDICTION_BET_HOW_TO_REMOVE_BET

    # Open prediction, show command to remove all bets
    if prediction_status is PredictionStatus.SENT and prediction.can_withdraw_bet:
        ot_text += phrases.PREDICTION_BET_HOW_TO_REMOVE_ALL_BETS

    await full_message_send(context, ot_text, update=update, add_delete_button=True)
