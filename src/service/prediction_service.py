import datetime
from datetime import datetime

from telegram.error import BadRequest, TelegramError
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.GroupChat import GroupChat
from src.model.Prediction import Prediction
from src.model.PredictionGroupChatMessage import PredictionGroupChatMessage
from src.model.PredictionOption import PredictionOption
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.model.enums.ContextDataKey import ContextDataKey
from src.model.enums.Emoji import Emoji
from src.model.enums.Feature import Feature
from src.model.enums.Notification import (
    PredictionResultNotification,
    PredictionBetInvalidNotification,
)
from src.model.enums.PredictionStatus import PredictionStatus, get_prediction_status_name_by_key
from src.model.enums.PredictionType import PredictionType
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.enums.income_tax.IncomeTaxEventType import IncomeTaxEventType
from src.model.error.CustomException import PredictionException
from src.model.pojo.ContextDataValue import ContextDataValue
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import round_belly_up, add_or_remove_bounty
from src.service.date_service import default_datetime_format
from src.service.devil_fruit_service import get_ability_value
from src.service.group_service import (
    broadcast_to_chats_with_feature_enabled_dispatch,
    save_group_chat_error,
)
from src.service.message_service import escape_valid_markdown_chars, full_message_send
from src.service.notification_service import send_notification
from src.utils.context_utils import get_random_user_context_inner_query_key
from src.utils.math_utils import (
    get_percentage_from_value,
    get_value_from_percentage,
    add_percentage_to_value,
)
from src.utils.string_utils import get_belly_formatted


async def send(
    context: ContextTypes.DEFAULT_TYPE, prediction: Prediction, is_resent: bool = False
) -> None:
    """
    Send prediction
    :param context: Telegram context
    :param prediction: Prediction
    :param is_resent: If prediction was already sent
    """

    # Do not change status or message_id if prediction is resent
    if not is_resent:
        if PredictionStatus(prediction.status) is not PredictionStatus.NEW:
            raise PredictionException(phrases.PREDICTION_NOT_IN_NEW_STATUS)

        prediction.status = PredictionStatus.SENT
        prediction.send_date = datetime.now()

    prediction.save()

    text = get_prediction_text(prediction)
    await broadcast_to_chats_with_feature_enabled_dispatch(
        context,
        Feature.PREDICTION,
        text,
        external_item=prediction,
        inline_keyboard=[[get_prediction_deeplink_button(prediction)]],
    )


def get_prediction_text(
    prediction: Prediction,
    add_bets_command: bool = True,
    user: User = None,
    is_creator_recap: bool = False,
) -> str:
    """
    Get prediction text
    :param prediction: Prediction
    :param add_bets_command: If to add commands on how to place and remove bets
    :param user: User, if called from private chat and prediction max refund should be customized
    by DF ability
    :param is_creator_recap: If the prediction is being sent to the creator as a recap
    :return: Prediction text
    """

    if is_creator_recap:
        add_bets_command = False

    is_creator = prediction.creator is not None and user == prediction.creator
    is_creator_but_not_sent = is_creator and prediction.get_status() is PredictionStatus.NEW
    if not is_creator_recap:
        is_creator_recap = (
            prediction.id is None and prediction.creator is not None and user == prediction.creator
        )

    # Options text
    options_text = ""
    total_wager = 0
    if not (is_creator_recap or is_creator_but_not_sent):
        prediction_options: list[PredictionOption] = prediction.prediction_options
        prediction_options_users: list[PredictionOptionUser] = get_prediction_options_users(
            prediction
        )
        total_wager = sum(
            prediction_option_user.wager for prediction_option_user in prediction_options_users
        )

        for index, prediction_option in enumerate(prediction_options):
            prediction_option_users: list[PredictionOptionUser] = [
                prediction_option_user
                for prediction_option_user in prediction_options_users
                if prediction_option_user.prediction_option.id == prediction_option.id
            ]
            option_wager = sum(
                prediction_option_user.wager for prediction_option_user in prediction_option_users
            )
            options_text += phrases.PREDICTION_TEXT_OPTION_WITH_PERCENTAGE.format(
                prediction_option.number,
                escape_valid_markdown_chars(prediction_option.option),
                get_percentage_from_value(option_wager, total_wager, add_decimal=False),
                (Emoji.CORRECT if prediction_option.is_correct else ""),
            )
    else:  # User prediction, not saved yet
        if prediction.id is None:
            for index, option in enumerate(prediction.options):
                options_text += phrases.PREDICTION_TEXT_OPTION.format(
                    index + 1,
                    escape_valid_markdown_chars(option),
                )
        else:
            prediction_options: list[PredictionOption] = prediction.prediction_options
            for index, prediction_option in enumerate(prediction_options):
                options_text += phrases.PREDICTION_TEXT_OPTION.format(
                    prediction_option.number,
                    escape_valid_markdown_chars(prediction_option.option),
                )
        options_text += "\n" if prediction.end_date is not None else ""
    added_text = ""

    # Closing date if not None
    if not is_creator_recap:
        added_text += (
            phrases.PREDICTION_CLOSING_DATE.format(
                default_datetime_format(prediction.end_date, user)
            )
            if prediction.end_date is not None
            else ""
        )

        # If creator and bets closed, show cut off date with description
        if is_creator and prediction.get_status() is PredictionStatus.BETS_CLOSED:
            added_text += phrases.PREDICTION_CREATE_CUT_OFF_DATE.format(
                default_datetime_format(prediction.cut_off_date, user)
                if prediction.cut_off_date is not None
                else phrases.TEXT_NOT_SET
            )
            added_text += phrases.PREDICTION_CUT_OFF_DATE_HOW_TO_SET
        else:
            added_text += (
                phrases.PREDICTION_CUT_OFF_DATE.format(
                    default_datetime_format(prediction.cut_off_date, user)
                )
                if prediction.cut_off_date is not None
                else ""
            )
    else:
        added_text += phrases.PREDICTION_CREATE_CLOSE_DATE.format(
            default_datetime_format(prediction.end_date, user)
            if prediction.end_date is not None
            else phrases.TEXT_NOT_SET
        )

        added_text += phrases.PREDICTION_CREATE_CUT_OFF_DATE.format(
            default_datetime_format(prediction.cut_off_date, user)
            if prediction.cut_off_date is not None
            else phrases.TEXT_NOT_SET
        )

    optional_text = ""

    # Wagers refunded
    if PredictionType(prediction.type) is not PredictionType.USER:
        if prediction.refund_wager:
            enabled_emoji = Emoji.PREDICTION_FEATURE_ENABLED
            if user is not None:
                max_refund_wager = get_max_wager_refund(prediction=prediction, user=user)
            else:
                max_refund_wager = prediction.max_refund_wager
            max_refund_text = phrases.PREDICTION_WAGERS_REFUNDED_MAX.format(
                get_belly_formatted(max_refund_wager)
            )  # Get from get_value, if user param is not None
        else:
            enabled_emoji = Emoji.PREDICTION_FEATURE_DISABLED
            max_refund_text = ""
        optional_text += phrases.PREDICTION_WAGERS_REFUNDED.format(enabled_emoji, max_refund_text)

    # Multiple bets allowed
    enabled_emoji = (
        Emoji.PREDICTION_FEATURE_ENABLED
        if prediction.allow_multiple_choices
        else Emoji.PREDICTION_FEATURE_DISABLED
    )
    optional_text += phrases.PREDICTION_MULTIPLE_BETS_ALLOWED.format(enabled_emoji)
    if is_creator_recap:
        optional_text += phrases.PREDICTION_MULTIPLE_BETS_ALLOWED_DESCRIPTION

    # Bet withdrawal allowed
    optional_text += "\n" if is_creator_recap else ""
    enabled_emoji = (
        Emoji.PREDICTION_FEATURE_ENABLED
        if prediction.can_withdraw_bet
        else Emoji.PREDICTION_FEATURE_DISABLED
    )
    optional_text += phrases.PREDICTION_CAN_WITHDRAW_BETS.format(enabled_emoji)
    if is_creator_recap:
        optional_text += phrases.PREDICTION_CAN_WITHDRAW_BETS_DESCRIPTION

    # Is public, only for creator
    if is_creator:
        optional_text += "\n" if is_creator_recap else ""
        enabled_emoji = (
            Emoji.PREDICTION_FEATURE_ENABLED
            if prediction.is_public
            else Emoji.PREDICTION_FEATURE_DISABLED
        )
        optional_text += phrases.PREDICTION_IS_PUBLIC.format(enabled_emoji)
        optional_text += phrases.PREDICTION_IS_PUBLIC_DESCRIPTION if is_creator_recap else ""

    # Add command to place and remove bets if prediction is open
    how_to_bet_command_text = ""
    how_to_remove_bet_command_text = ""
    if add_bets_command:
        if PredictionStatus(prediction.status) is PredictionStatus.SENT:
            how_to_bet_command_text = phrases.PREDICTION_BET_HOW_TO_PLACE_BET

            if prediction.can_withdraw_bet:
                how_to_remove_bet_command_text = phrases.PREDICTION_BET_HOW_TO_REMOVE_ALL_BETS

    # Append \n if not empty
    optional_text = "\n" + optional_text if optional_text != "" else ""
    added_text += optional_text

    # User prediction disclaimer
    user_prediction_disclaimer = ""
    if PredictionType(prediction.type) is PredictionType.USER and not is_creator:
        user_prediction_disclaimer = phrases.PREDICTION_USER_DISCLAIMER

    # Prediction text
    if prediction.id is not None and not is_creator_but_not_sent and not is_creator_recap:
        prediction_text = phrases.PREDICTION_TEXT.format(
            escape_valid_markdown_chars(prediction.question),
            options_text,
            get_belly_formatted(total_wager),
            get_prediction_status_name_by_key(PredictionStatus(prediction.status)),
            added_text,
            how_to_bet_command_text,
            how_to_remove_bet_command_text,
            user_prediction_disclaimer,
        )
    else:  # User prediction, not saved yet - recap
        added_text += user_prediction_disclaimer
        prediction_text = phrases.PREDICTION_CREATE_RECAP.format(
            escape_valid_markdown_chars(prediction.question), options_text, added_text
        )

    return prediction_text


def get_user_prediction_status_text(
    prediction: Prediction,
    user: User,
    prediction_options_user: list[PredictionOptionUser] = None,
    add_header: bool = True,
    add_bets_command: bool = True,
) -> str:
    """
    Get the prediction status text
    :param prediction: The prediction
    :param user: The user
    :param prediction_options_user: The options the user has bet on
    :param add_header: Whether to add the "Bets" header
    :param add_bets_command: Whether to add the command to remove all bets
    :return: The prediction status text
    """

    if PredictionStatus(prediction.status) is PredictionStatus.NEW:
        return ""

    if prediction_options_user is None:
        prediction_options_user = get_prediction_options_user(prediction, user)

    if len(prediction_options_user) == 0:
        return phrases.PREDICTION_BET_USER_HAS_NOT_BET

    total_win_amount = 0
    total_win_count = 0
    total_loss_count = 0
    prediction_status: PredictionStatus = PredictionStatus(prediction.status)
    ot_text = phrases.PREDICTION_STATUS_BETS_HEADER if add_header else ""

    for prediction_option_user in prediction_options_user:
        prediction_option: PredictionOption = prediction_option_user.prediction_option

        # Option
        ot_text += phrases.PREDICTION_STATUS_OPTION.format(
            prediction_option.number,
            escape_valid_markdown_chars(prediction_option.option),
            get_belly_formatted(prediction_option_user.wager),
        )

        # If the prediction results are not set, assume the option is correct
        is_potential = prediction_status is not PredictionStatus.RESULT_SET

        potential_win_amount = get_prediction_option_user_win(
            prediction_option_user, is_potential=is_potential
        )

        potential_win_amount_formatted = get_belly_formatted(potential_win_amount)

        # Result not set, add potential win
        if prediction_status is not PredictionStatus.RESULT_SET:
            ot_text += phrases.PREDICTION_STATUS_POTENTIAL_WIN.format(
                potential_win_amount_formatted
            )
        else:
            # Result set, add win or loss amount
            if prediction_option.is_correct:
                ot_text += phrases.PREDICTION_STATUS_RESULT_WIN.format(
                    potential_win_amount_formatted
                )
                total_win_amount += potential_win_amount
                total_win_count += 1
            else:
                ot_text += phrases.PREDICTION_STATUS_RESULT_LOST
                total_win_amount -= (
                    prediction_option_user.wager if not prediction.refund_wager else 0
                )
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
                    ot_text += phrases.PREDICTION_STATUS_NET_WIN.format(
                        get_belly_formatted(total_win_amount)
                    )
                else:  # All options were correct, show total win
                    ot_text += phrases.PREDICTION_STATUS_TOTAL_WIN.format(
                        get_belly_formatted(total_win_amount)
                    )
            else:
                total_loss_amount = abs(total_win_amount)
                if total_win_count > 0:  # At least one option was correct, show net loss
                    ot_text += phrases.PREDICTION_STATUS_NET_LOSS.format(
                        get_belly_formatted(total_loss_amount)
                    )
                else:  # All options were wrong, show total loss
                    ot_text += phrases.PREDICTION_STATUS_TOTAL_LOSS.format(
                        get_belly_formatted(total_loss_amount)
                    )
        # Open prediction, show command to remove single bet
        elif (
            add_bets_command
            and prediction_status is PredictionStatus.SENT
            and prediction.can_withdraw_bet
        ):
            ot_text += phrases.PREDICTION_BET_HOW_TO_REMOVE_BET

    # Open prediction, show command to remove all bets
    if (
        add_bets_command
        and prediction_status is PredictionStatus.SENT
        and prediction.can_withdraw_bet
    ):
        ot_text += phrases.PREDICTION_BET_HOW_TO_REMOVE_ALL_BETS

    return ot_text


async def close_bets(context: ContextTypes.DEFAULT_TYPE, prediction: Prediction) -> None:
    """
    Close bets
    :param context: Telegram context
    :param prediction: Prediction
    """
    if PredictionStatus(prediction.status) is not PredictionStatus.SENT:
        raise PredictionException(phrases.PREDICTION_NOT_IN_SENT_STATUS)

    await cut_off_invalid_bets(context, prediction)

    # Update status
    prediction.status = PredictionStatus.BETS_CLOSED
    prediction.end_date = datetime.now()
    prediction.save()

    # Update prediction message
    await refresh(context, prediction)

    # Send message in reply notifying users that bets are closed
    await send_prediction_status_change_message_or_refresh_dispatch(
        context, phrases.PREDICTION_CLOSED_FOR_BETS, prediction
    )


async def cut_off_invalid_bets(context: ContextTypes.DEFAULT_TYPE, prediction: Prediction):
    """
    Cut off invalid bets (bets placed after cut off date), notifying the users
    :param context: Telegram context
    :param prediction: Prediction
    :return: None
    """

    # Dictionary with key: user_id, value: user, prediction option user, total refund
    users_invalid_prediction_options: dict[int, [User, list[PredictionOptionUser], int]] = {}

    # If cut off date is not None, delete all PredictionOptionUsers with date > cut off date and
    # return wager
    if prediction.cut_off_date is not None:
        invalid_prediction_option_users: list[PredictionOptionUser] = get_invalid_bets(prediction)
        for invalid_prediction_option_user in invalid_prediction_option_users:
            user: User = invalid_prediction_option_user.user
            # Return wager and subtract from pending bounty
            await add_or_remove_bounty(
                user, invalid_prediction_option_user.wager, should_affect_pending_bounty=True
            )
            user.save()

            # Add to users_invalid_prediction_options
            if user.id not in users_invalid_prediction_options:
                users_invalid_prediction_options[user.id] = [user, [], 0]

            users_invalid_prediction_options[user.id][1].append(invalid_prediction_option_user)
            users_invalid_prediction_options[user.id][2] += invalid_prediction_option_user.wager

            invalid_prediction_option_user.delete_instance()

    # Send notification to users
    for user_id, value in users_invalid_prediction_options.items():
        user: User = value[0]
        prediction_options_user = value[1]
        total_refund = value[2]

        notification: PredictionBetInvalidNotification = PredictionBetInvalidNotification(
            prediction, prediction_options_user, total_refund
        )

        await send_notification(context, user, notification)


def get_invalid_bets(
    prediction: Prediction, cut_off_date: datetime = None
) -> list[PredictionOptionUser]:
    """
    Get invalid bets (bets placed after cut off date)
    :param prediction: Prediction
    :param cut_off_date: Cut off date
    :return: List of invalid bets
    """

    if cut_off_date is None:
        if prediction.cut_off_date is None:
            raise ValueError("cut_off_date cannot be None if prediction.cut_off_date is None")

        cut_off_date = prediction.cut_off_date

    return PredictionOptionUser.select().where(
        (PredictionOptionUser.prediction == prediction)
        & (PredictionOptionUser.date > cut_off_date)
    )


async def set_results(context: ContextTypes.DEFAULT_TYPE, prediction: Prediction) -> None:
    """
    Set results
    :param context: Telegram context
    :param prediction: Prediction
    """
    if PredictionStatus(prediction.status) is not PredictionStatus.BETS_CLOSED:
        raise PredictionException(phrases.PREDICTION_NOT_IN_BETS_CLOSED_STATUS)

    prediction_options: list[PredictionOption] = prediction.prediction_options
    prediction_options_correct: list[PredictionOption] = [
        prediction_option
        for prediction_option in prediction_options
        if prediction_option.is_correct
    ]
    prediction_options_users: list[PredictionOptionUser] = get_prediction_options_users(prediction)

    # Dictionary with key: user_id, value: list (user, total_win, list of prediction_options)
    users_total_win: dict[int, list[User, int, list[PredictionOption]]] = {}

    for prediction_option_user in prediction_options_users:
        user: User = prediction_option_user.user

        # If user is not in dictionary, add it
        if user.id not in users_total_win:
            users_total_win[user.id] = [user, 0, []]

        # Add prediction option to list
        prediction_option: PredictionOption = prediction_option_user.prediction_option
        users_total_win[user.id][2].append(prediction_option)

        # Correct prediction
        if prediction_option.is_correct:
            win_amount = get_prediction_option_user_win(
                prediction_option_user, prediction_options_users=prediction_options_users
            )
            # Add to bounty
            await add_or_remove_bounty(
                user,
                win_amount,
                pending_belly_amount=prediction_option_user.wager,
                tax_event_type=IncomeTaxEventType.PREDICTION,
                event_id=prediction.id,
            )

            # Add to total win
            users_total_win[user.id][1] += win_amount
        else:
            # Remove from total win
            users_total_win[user.id][1] -= prediction_option_user.wager

        # Should refund wager or no correct options
        if prediction.refund_wager or len(prediction_options_correct) == 0:
            if len(prediction_options_correct) == 0:
                # No correct options, refund full wager
                refund_amount = prediction_option_user.wager
            else:
                # Cap refund
                refund_amount = min(
                    prediction_option_user.wager,
                    get_max_wager_refund(prediction_option_user=prediction_option_user),
                )

            await add_or_remove_bounty(
                user, refund_amount, pending_belly_amount=prediction_option_user.wager
            )

        user.save()

    # Update status
    prediction.status = PredictionStatus.RESULT_SET
    prediction.result_set_date = datetime.now()
    prediction.save()

    # Refresh prediction
    await refresh(context, prediction)

    # Send message in reply notifying users that results are set
    await send_prediction_status_change_message_or_refresh_dispatch(
        context, phrases.PREDICTION_RESULTS_SET, prediction
    )

    # Send notification to users
    for user_id, value in users_total_win.items():
        user: User = value[0]
        total_win: int = value[1]
        user_prediction_options: list[PredictionOption] = value[2]

        notification: PredictionResultNotification = PredictionResultNotification(
            prediction, user_prediction_options, prediction_options_correct, total_win, user
        )

        await send_notification(context, user, notification)


async def refresh(
    context: ContextTypes.DEFAULT_TYPE, prediction: Prediction, group_chat: GroupChat = None
) -> None:
    """
    Refresh prediction
    :param context: Telegram context
    :param prediction: Prediction
    :param group_chat: Group chat, refresh only for this group chat
    """
    if PredictionStatus(prediction.status) is PredictionStatus.NEW:
        raise PredictionException(phrases.PREDICTION_NOT_SENT)

    await send_prediction_status_change_message_or_refresh_dispatch(
        context, prediction=prediction, should_refresh=True, group_chat=group_chat
    )


def get_prediction_options_user(prediction: Prediction, user: User) -> list[PredictionOptionUser]:
    """
    Get all prediction options for a user
    :param prediction: Prediction
    :param user: User
    :return: List of prediction options user
    """

    result = (
        PredictionOptionUser.select()
        .join(PredictionOption)
        .where(
            (PredictionOptionUser.prediction == prediction) & (PredictionOptionUser.user == user)
        )
        .order_by(PredictionOption.number.asc())
    )

    return result


def get_prediction_options_users(prediction: Prediction) -> list[PredictionOptionUser]:
    """
    Get all prediction options users for a prediction
    :param prediction: Prediction
    :return: List of prediction options users
    """
    return PredictionOptionUser.select().where(PredictionOptionUser.prediction == prediction)


def get_prediction_option_user_win(
    prediction_option_user: PredictionOptionUser,
    prediction_options_users: list[PredictionOptionUser] = None,
    is_potential: bool = False,
) -> int:
    """
    Get prediction option user potential win
    :param prediction_option_user: PredictionOptionUser for which to get potential win
    :param prediction_options_users: List of PredictionOptionUser for the same prediction
    :param is_potential: If True, assume that the prediction option is correct
    :return: Prediction option user potential win
    """

    if prediction_options_users is None:
        prediction_options_users = get_prediction_options_users(prediction_option_user.prediction)

    total_wager = sum(
        prediction_option_user.wager for prediction_option_user in prediction_options_users
    )

    if not is_potential:
        total_correct_wager = sum(
            pou.wager for pou in prediction_options_users if pou.prediction_option.is_correct
        )
    else:
        total_correct_wager = sum(
            pou.wager
            for pou in prediction_options_users
            if pou.prediction_option == prediction_option_user.prediction_option
        )

    # What percent of the total correct wager is this user's wager
    percentage_of_correct_wager = get_percentage_from_value(
        prediction_option_user.wager, total_correct_wager
    )

    # How much is this percentage in the total wager
    value_from_total_wager = round_belly_up(
        get_value_from_percentage(total_wager, percentage_of_correct_wager)
    )

    return value_from_total_wager


async def send_scheduled_predictions(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send scheduled predictions
    :param context: Telegram context
    """

    # Select not sent predictions with send date in the past
    predictions: list[Prediction] = Prediction.select().where(
        (Prediction.send_date.is_null(False))
        & (Prediction.send_date <= datetime.now())
        & (Prediction.status == PredictionStatus.NEW)
    )

    for prediction in predictions:
        await send(context, prediction)


async def close_scheduled_predictions(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Close scheduled predictions
    :param context: Telegram context
    """

    # Select sent predictions with end date in the past
    predictions: list[Prediction] = Prediction.select().where(
        (Prediction.end_date.is_null(False))
        & (Prediction.end_date <= datetime.now())
        & (Prediction.status == PredictionStatus.SENT)
    )

    for prediction in predictions:
        await close_bets(context, prediction)


async def remove_all_bets_from_active_predictions(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Remove all bets from active predictions due to bounty reset
    :param context: Telegram context
    """

    # Select active predictions
    active_statuses = [PredictionStatus.SENT, PredictionStatus.BETS_CLOSED]
    predictions: list[Prediction] = Prediction.select().where(
        Prediction.status.in_(active_statuses)
    )

    for prediction in predictions:
        PredictionOptionUser.delete().where(
            PredictionOptionUser.prediction == prediction
        ).execute()
        await send_prediction_status_change_message_or_refresh_dispatch(
            context, phrases.PREDICTION_ALL_BETS_REMOVED_FOR_BOUNTY_RESET, prediction
        )


def user_has_bet_on_prediction(prediction: Prediction, user: User) -> bool:
    """
    Check if user bet on prediction
    :param prediction: Prediction
    :param user: User
    :return: True if user bet on prediction
    """

    return len(get_prediction_options_user(prediction, user)) > 0


def get_user_prediction_status_emoji(prediction: Prediction, user: User) -> Emoji:
    """
    Get user prediction status emoji for a user
    :param prediction: Prediction
    :param user: User
    :return: User prediction status emoji
    """

    prediction_status = PredictionStatus(prediction.status)
    if user_has_bet_on_prediction(prediction, user):
        if prediction_status is PredictionStatus.SENT:
            return Emoji.PREDICTION_OPEN
        elif prediction_status is PredictionStatus.BETS_CLOSED:
            return Emoji.PREDICTION_CLOSED
        else:  # Result is set
            net_win = get_prediction_net_win(prediction, user)
            if net_win > 0:
                return Emoji.LOG_POSITIVE
            else:
                return Emoji.LOG_NEGATIVE
    elif prediction_status is PredictionStatus.NEW:
        return Emoji.PREDICTION_NEW
    else:  # If user didn't bet on prediction, and it's not open, it means they are the creator
        return Emoji.NULL


def get_prediction_net_win(prediction: Prediction, user: User) -> int:
    """
    Get net win for a user, without considering refunds, only for predictions with result set
    :param prediction: Prediction
    :param user: User
    :return: Net win
    """

    prediction_options_user: list[PredictionOptionUser] = get_prediction_options_user(
        prediction, user
    )

    if PredictionStatus(prediction.status) is not PredictionStatus.RESULT_SET:
        raise ValueError(
            f"Prediction {prediction.id} results are not set, so net win can't be calculated"
        )

    net_win = 0
    for pou in prediction_options_user:
        prediction_option: PredictionOption = pou.prediction_option
        if prediction_option.is_correct:
            net_win += get_prediction_option_user_win(pou)
        else:
            net_win -= pou.wager

    return net_win


async def save_prediction_option_user(
    prediction_option: PredictionOption,
    user: User,
    wager: int,
    prediction_group_chat_message: PredictionGroupChatMessage = None,
) -> PredictionOptionUser:
    """
    Save the prediction option user
    :param prediction_option: The prediction option
    :param user: The user
    :param wager: The wager
    :param prediction_group_chat_message: The prediction group chat message
    :return: The prediction option user
    """
    # Find existing prediction option user if it exists
    prediction_option_user: PredictionOptionUser = PredictionOptionUser.get_or_none(
        (PredictionOptionUser.user == user)
        & (PredictionOptionUser.prediction_option == prediction_option)
    )
    # User has already bet on this option, add the wager to the existing bet
    if prediction_option_user is not None:
        prediction_option_user.wager += wager
    else:
        # Create prediction option user
        prediction_option_user = PredictionOptionUser()
        prediction_option_user.prediction = prediction_option.prediction
        prediction_option_user.prediction_option = prediction_option
        prediction_option_user.user = user
        prediction_option_user.wager = wager
        max_refund_wager_boost = get_ability_value(
            user, DevilFruitAbilityType.PREDICTION_WAGER_REFUND, 0, add_to_value=True
        )
        prediction_option_user.max_refund_wager_boost = (
            max_refund_wager_boost if max_refund_wager_boost > 0 else None
        )

    prediction_option_user.prediction_group_chat_message = (
        prediction_group_chat_message if prediction_group_chat_message is not None else None
    )
    prediction_option_user.date = datetime.now()
    prediction_option_user.save()

    # Remove wager from user balance
    await add_or_remove_bounty(user, wager, add=False, should_affect_pending_bounty=True)

    return prediction_option_user


async def delete_prediction_option_user(
    user: User, prediction_option_user: PredictionOptionUser
) -> None:
    """
    Delete a prediction option user
    :param user: The user object
    :param prediction_option_user: The prediction option user
    :return: None
    """
    # Return wager
    await add_or_remove_bounty(
        user, prediction_option_user.wager, should_affect_pending_bounty=True
    )

    # Delete prediction option user
    prediction_option_user.delete_instance()


async def delete_prediction_option_for_user(
    user: User, prediction_option: PredictionOption
) -> None:
    """
    Delete a prediction option for a user
    :param user: The user object
    :param prediction_option: The prediction option
    :return: None
    """
    prediction_option_user: PredictionOptionUser = PredictionOptionUser.get_or_none(
        (PredictionOptionUser.user == user)
        & (PredictionOptionUser.prediction_option == prediction_option)
    )

    if prediction_option_user is not None:  # Should always be true
        await delete_prediction_option_user(user, prediction_option_user)


def get_max_wager_refund(
    prediction_option_user: PredictionOptionUser = None,
    prediction: Prediction = None,
    user: User = None,
) -> int:
    """
    Get the maximum wager refund for a prediction option user, considering the Devil Fruit ability
    boost
    :param prediction_option_user: The prediction option user
    :param prediction: The prediction
    :param user: The user
    :return: The maximum wager refund
    """

    # If prediction option user is not provided, prediction and user must be provided
    if prediction_option_user is None and (prediction is None or user is None):
        if prediction is None or user is None:
            raise ValueError("Prediction option user or prediction and user must be provided")

        prediction_option_user: PredictionOptionUser = PredictionOptionUser.get_or_none(
            (PredictionOptionUser.user == user) & (PredictionOptionUser.prediction == prediction)
        )

    if prediction_option_user is None:  # user has not yet placed a bet
        return int(
            get_ability_value(
                user, DevilFruitAbilityType.PREDICTION_WAGER_REFUND, prediction.max_refund_wager
            )
        )

    if prediction is None:
        prediction: Prediction = prediction_option_user.prediction

    max_refund_boosted = int(
        add_percentage_to_value(
            prediction.max_refund_wager, prediction_option_user.max_refund_wager_boost
        )
    )
    return max(prediction.max_refund_wager, max_refund_boosted)


def get_prediction_from_message_id(group_chat: GroupChat, message_id: int) -> Prediction | None:
    """
    Gets the prediction from the message id
    :param group_chat: The group chat
    :param message_id: The message id
    :return: The prediction
    """

    prediction_group_chat_message: PredictionGroupChatMessage = (
        PredictionGroupChatMessage.get_or_none(
            (PredictionGroupChatMessage.group_chat == group_chat)
            & (PredictionGroupChatMessage.message_id == message_id)
        )
    )

    if prediction_group_chat_message is None:
        return None

    return prediction_group_chat_message.prediction


async def send_prediction_status_change_message_or_refresh_dispatch(
    context: ContextTypes.DEFAULT_TYPE,
    text: str = None,
    prediction: Prediction = None,
    should_refresh: bool = False,
    group_chat: GroupChat = None,
):
    """
    Dispatch a prediction status change message
    :param context: The context
    :param prediction: The prediction
    :param text: The text
    :param should_refresh: Whether to should_refresh the message instead of sending a new one
    :param group_chat: The group chat for which to refresh the message
    :return: None
    """

    if prediction is not None:
        predictions: list[Prediction] = [prediction]
    elif should_refresh:
        predictions: list[Prediction] = list(
            Prediction.select().where(Prediction.status == PredictionStatus.SENT)
        )
    else:
        raise ValueError("Either prediction or should_refresh must be provided")

    for prediction in predictions:
        if should_refresh:
            text = get_prediction_text(prediction)

        context.application.create_task(
            send_prediction_status_change_message_or_refresh(
                context, prediction, text, should_refresh, group_chat
            )
        )


async def send_prediction_status_change_message_or_refresh(
    context: ContextTypes.DEFAULT_TYPE,
    prediction: Prediction,
    text: str,
    should_refresh: bool = False,
    group_chat: GroupChat = None,
):
    """
    Send a prediction status change message to all group chats in which the prediction was sent or
    refresh the message
    :param context: The context
    :param prediction: The prediction
    :param text: The text
    :param should_refresh: Whether to should_refresh the message instead of sending a new one
    :param group_chat: The group chat for which to refresh the message
    :return: None
    """

    group_chat_filter = True
    if group_chat is not None:
        group_chat_filter = PredictionGroupChatMessage.group_chat == group_chat

    messages: list[PredictionGroupChatMessage] = PredictionGroupChatMessage.select().where(
        (PredictionGroupChatMessage.prediction == prediction) & group_chat_filter
    )

    for message in messages:
        group_chat: GroupChat = message.group_chat
        try:
            if should_refresh:  # Edit original message
                await full_message_send(
                    context,
                    text,
                    group_chat=group_chat,
                    edit_message_id=message.message_id,
                    keyboard=[[get_prediction_deeplink_button(prediction)]],
                )
            else:  # Send new message in reply
                await full_message_send(
                    context,
                    text,
                    group_chat=group_chat,
                    reply_to_message_id=message.message_id,
                    allow_sending_without_reply=False,
                )
        except (TelegramError, BadRequest) as e:
            # New text same as old one, ignore
            if not (
                should_refresh
                and isinstance(e, BadRequest)
                and "Message is not modified" in str(e)
            ):
                save_group_chat_error(group_chat, str(e))


def get_prediction_deeplink_button(prediction: Prediction) -> Keyboard:
    """
    Get the prediction deeplink button
    :param prediction: The prediction
    :return: The keyboard
    """

    from src.chat.private.screens.screen_prediction_detail import PredictionDetailReservedKeys

    info: dict = {PredictionDetailReservedKeys.PREDICTION_ID: prediction.id}

    status: PredictionStatus = PredictionStatus(prediction.status)
    keyboard_text = (
        phrases.GRP_KEY_PREDICTION_BET_IN_PRIVATE_CHAT
        if status is PredictionStatus.SENT
        else phrases.GRP_KEY_PREDICTION_VIEW_IN_PRIVATE_CHAT
    )
    return Keyboard(
        keyboard_text,
        info,
        screen=Screen.PVT_PREDICTION_DETAIL,
        previous_screen_list=[Screen.PVT_PREDICTION],
        is_deeplink=True,
    )


async def delete_prediction(prediction: Prediction):
    """
    Delete a prediction
    :param prediction: The prediction
    :return: None
    """

    # Delete all prediction option users and return wagers
    prediction_option_users: list[PredictionOptionUser] = get_prediction_options_users(prediction)
    for prediction_option_user in prediction_option_users:
        user: User = prediction_option_user.user
        await delete_prediction_option_user(user, prediction_option_user)

    # Delete prediction
    prediction.delete_instance()


def get_share_text(context: ContextTypes.DEFAULT_TYPE, user: User, prediction: Prediction) -> str:
    """
    Get the share button url
    :param context: The context
    :param user: The user
    :param prediction: The prediction
    :return: The share button url
    """

    # Save get_text to context
    inner_key = get_random_user_context_inner_query_key(context)
    keyboard: Keyboard = (
        get_prediction_deeplink_button(prediction)
        if prediction.get_status() is PredictionStatus.SENT
        else None
    )

    context_data_value: ContextDataValue = ContextDataValue(
        phrases.PREDICTION_INLINE_RESULT_SHARE,
        get_prediction_text,
        args=(prediction, False),
        description=prediction.question,
        keyboard=[[keyboard]],
    )
    user.set_context_data(
        context, ContextDataKey.INLINE_QUERY, context_data_value, inner_key=inner_key
    )

    return inner_key


def prediction_is_sent_to_group_chat(prediction: Prediction, group_chat: GroupChat) -> bool:
    """
    Check if a prediction is sent to a group
    :param prediction: The prediction
    :param group_chat: The group chat
    :return: True if the prediction is sent to the group
    """

    return (
        PredictionGroupChatMessage.get_or_none(
            (PredictionGroupChatMessage.prediction == prediction)
            & (PredictionGroupChatMessage.group_chat == group_chat)
        )
        is not None
    )
