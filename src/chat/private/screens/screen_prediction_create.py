from datetime import datetime
from enum import IntEnum, StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.chat.private.screens.screen_prediction_detail import PredictionDetailReservedKeys
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.PredictionOptionUser import PredictionOptionUser
from src.model.User import User
from src.model.enums.ContextDataKey import ContextDataKey
from src.model.enums.Emoji import Emoji
from src.model.enums.PredictionStatus import PredictionStatus
from src.model.enums.PredictionType import PredictionType
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.CommonChatError import CommonChatException
from src.model.error.CustomException import (
    PredictionException,
    StepValidationException,
    DateValidationException,
)
from src.model.error.PrivateChatError import PrivateChatError, PrivateChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.date_service import (
    datetime_is_before,
    get_remaining_duration,
    get_user_timezone_and_offset_text,
    get_datetime_from_natural_language,
    default_datetime_format,
    get_datetime_in_future_hours,
)
from src.service.message_service import (
    full_message_send,
    get_create_or_edit_status,
    get_deeplink,
    get_yes_no_keyboard,
)
from src.service.prediction_service import (
    get_prediction_text,
    get_invalid_bets,
    cut_off_invalid_bets,
)


class Step(IntEnum):
    REQUEST_POLL = 0
    REQUEST_SETTINGS = 1
    REQUEST_CLOSE_DATE = 2
    REQUEST_POLL_CHANGE = 3
    REQUEST_CUT_OFF_DATE = 4
    END = 5


class PredictionCreateReservedKeys(StrEnum):
    PREDICTION_ID = "a"
    ALLOW_MULTIPLE_CHOICES = "b"
    ALLOW_BET_WITHDRAWAL = "c"
    IS_PUBLIC = "d"
    REMOVE_CLOSE_DATE = "e"
    IN_EDIT = "f"


# Disable inspection for prediction object might be referenced before assignment
# noinspection PyUnboundLocalVariable
async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard | None,
    user: User | None,
    is_refresh: bool = False,
) -> None:
    """
    Manage the prediction create screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :param is_refresh: If the screen is being refreshed
    :return: None
    """

    should_ignore_input, should_create_item, should_validate_input = get_create_or_edit_status(
        user, inbound_keyboard
    )
    inline_keyboard: list[list[Keyboard]] = [[]]

    if not should_ignore_input:
        # Validate that the user can create a prediction
        if not await validate(update, context, inbound_keyboard, user):
            return

        if user.private_screen_step is None:
            user.private_screen_step = Step.REQUEST_POLL

        prediction: Prediction | None = None
        try:
            prediction: Prediction = user.get_context_data(
                context, ContextDataKey.CREATED_PREDICTION
            )
        except CommonChatException:
            if (
                inbound_keyboard is not None
                and PredictionCreateReservedKeys.PREDICTION_ID in inbound_keyboard.info
            ):
                prediction: Prediction = Prediction.get_by_id(
                    inbound_keyboard.info[PredictionCreateReservedKeys.PREDICTION_ID]
                )
                user.private_screen_in_edit_id = prediction.id
                is_refresh = True
            elif user.private_screen_in_edit_id is not None:
                prediction: Prediction = Prediction.get_by_id(user.private_screen_in_edit_id)
                is_refresh = True

        if prediction is not None:
            user.set_context_data(context, ContextDataKey.CREATED_PREDICTION, prediction)
        else:
            if Step(user.private_screen_step) not in [Step.REQUEST_POLL, Step.REQUEST_SETTINGS]:
                raise ValueError(
                    "Prediction can be None only in step REQUEST_POLL or REQUEST_SETTINGS"
                )

        # Step in inbound keyboard, refresh
        if (
            inbound_keyboard is not None
            and ReservedKeyboardKeys.SCREEN_STEP in inbound_keyboard.info
        ):
            is_refresh = True

        go_to_next_step = True
        next_step = None

        try:
            match Step(user.private_screen_step):
                case Step.REQUEST_POLL:  # Request prediction poll
                    if (
                        prediction is not None and prediction.id is not None
                    ):  # From edit, go back to prediction detail
                        return await go_to_prediction_detail(
                            context, inbound_keyboard, prediction, update, user
                        )

                    ot_text = phrases.PREDICTION_CREATE_REQUEST_POLL

                case Step.REQUEST_SETTINGS:  # Validate prediction poll and request end date
                    go_to_next_step = False
                    if (
                        prediction is not None
                        and prediction.id is not None
                        and not prediction.should_save
                    ):
                        # Refresh from DB
                        prediction = Prediction.get_by_id(prediction.id)
                        user.set_context_data(
                            context, ContextDataKey.CREATED_PREDICTION, prediction
                        )

                    if inbound_keyboard is None and not is_refresh:
                        try:
                            # Only if prediction is new
                            if (
                                prediction is not None
                                and prediction.get_status() is not PredictionStatus.NEW
                            ):
                                raise StepValidationException(
                                    phrases.PREDICTION_CAN_EDIT_POLL_ONLY_IF_NEW
                                )
                            poll = update.message.poll
                            # Less than 2 options
                            if len(poll.options) < 2:
                                raise StepValidationException(
                                    phrases.PREDICTION_CREATE_INVALID_POLL
                                )

                            # Create prediction
                            prediction: Prediction = (
                                Prediction() if prediction is None else prediction
                            )
                            prediction.question = poll.question
                            prediction.options = [option.text for option in poll.options]

                            if prediction.id is None:
                                prediction.creator = user
                                prediction.allow_multiple_choices = poll.allows_multiple_answers
                                prediction.is_public = True
                                prediction.type = PredictionType.USER
                            else:
                                await save_prediction_options(prediction)

                            # Save to context
                            user.set_context_data(
                                context, ContextDataKey.CREATED_PREDICTION, prediction
                            )
                        except AttributeError:
                            raise StepValidationException(phrases.PREDICTION_CREATE_INVALID_POLL)
                    else:
                        prediction: Prediction = user.get_context_data(
                            context, ContextDataKey.CREATED_PREDICTION
                        )

                        if inbound_keyboard is not None:
                            # Only if prediction is new or sent
                            if prediction.is_new_or_sent():
                                # Change allow multiple choices
                                if (
                                    PredictionCreateReservedKeys.ALLOW_MULTIPLE_CHOICES
                                    in inbound_keyboard.info
                                ):
                                    prediction.allow_multiple_choices = inbound_keyboard.info[
                                        PredictionCreateReservedKeys.ALLOW_MULTIPLE_CHOICES
                                    ]

                                # Change allow bet withdrawal
                                if (
                                    PredictionCreateReservedKeys.ALLOW_BET_WITHDRAWAL
                                    in inbound_keyboard.info
                                ):
                                    prediction.can_withdraw_bet = inbound_keyboard.info[
                                        PredictionCreateReservedKeys.ALLOW_BET_WITHDRAWAL
                                    ]

                            # Change is public
                            if PredictionCreateReservedKeys.IS_PUBLIC in inbound_keyboard.info:
                                prediction.is_public = inbound_keyboard.info[
                                    PredictionCreateReservedKeys.IS_PUBLIC
                                ]

                            # Only if prediction is new or sent
                            if prediction.is_new_or_sent():
                                # Remove close date
                                if (
                                    PredictionCreateReservedKeys.REMOVE_CLOSE_DATE
                                    in inbound_keyboard.info
                                ):
                                    prediction.end_date = None

                    # Send message with keyboard to set options and end date
                    if prediction.is_new_or_sent():
                        # Allow multiple choices
                        allow_multiple_choices_active_emoji = (
                            Emoji.ENABLED if prediction.allow_multiple_choices else ""
                        )
                        allow_multiple_choices_key = Keyboard(
                            text=(
                                allow_multiple_choices_active_emoji
                                + phrases.PVT_KEY_PREDICTION_CREATE_ALLOW_MULTIPLE_CHOICES
                            ),
                            screen=Screen.PVT_PREDICTION_CREATE,
                            info={
                                PredictionCreateReservedKeys.ALLOW_MULTIPLE_CHOICES: (
                                    not prediction.allow_multiple_choices
                                ),
                                ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_SETTINGS,
                            },
                        )
                        inline_keyboard.append([allow_multiple_choices_key])

                        # Allow bet withdrawal
                        allow_bet_withdrawal_active_emoji = (
                            Emoji.ENABLED if prediction.can_withdraw_bet else ""
                        )
                        allow_bet_withdrawal_key = Keyboard(
                            text=(
                                allow_bet_withdrawal_active_emoji
                                + phrases.PVT_KEY_PREDICTION_CREATE_ALLOW_BET_WITHDRAWAL
                            ),
                            screen=Screen.PVT_PREDICTION_CREATE,
                            info={
                                PredictionCreateReservedKeys.ALLOW_BET_WITHDRAWAL: (
                                    not prediction.can_withdraw_bet
                                ),
                                ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_SETTINGS,
                            },
                        )
                        inline_keyboard.append([allow_bet_withdrawal_key])

                    # Is public
                    is_public_active_emoji = Emoji.ENABLED if prediction.is_public else ""
                    is_public_key = Keyboard(
                        text=is_public_active_emoji + phrases.PVT_KEY_PREDICTION_CREATE_IS_PUBLIC,
                        screen=Screen.PVT_PREDICTION_CREATE,
                        info={
                            PredictionCreateReservedKeys.IS_PUBLIC: not prediction.is_public,
                            ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_SETTINGS,
                        },
                    )
                    inline_keyboard.append([is_public_key])

                    # Prediction new or open
                    if prediction.is_new_or_sent():
                        if prediction.end_date is None:
                            # Set close date
                            set_close_date_key = Keyboard(
                                text=phrases.PVT_KEY_PREDICTION_CREATE_SET_CLOSE_DATE,
                                screen=Screen.PVT_PREDICTION_CREATE,
                                info={ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_CLOSE_DATE},
                            )
                            inline_keyboard.append([set_close_date_key])
                        else:
                            # Remove close date
                            remove_close_date_key = Keyboard(
                                text=phrases.PVT_KEY_PREDICTION_CREATE_REMOVE_CLOSE_DATE,
                                screen=Screen.PVT_PREDICTION_CREATE,
                                info={
                                    PredictionCreateReservedKeys.REMOVE_CLOSE_DATE: (
                                        not prediction.can_withdraw_bet
                                    ),
                                    ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_SETTINGS,
                                },
                            )
                            inline_keyboard.append([remove_close_date_key])

                    # Prediction closed, cut off date
                    if prediction.is_closed():
                        # Set cut off date
                        set_cut_off_date_key = Keyboard(
                            text=phrases.PVT_KEY_PREDICTION_CREATE_SET_CUT_OFF_DATE,
                            screen=Screen.PVT_PREDICTION_CREATE,
                            info={ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_CUT_OFF_DATE},
                        )
                        inline_keyboard.append([set_cut_off_date_key])

                    # Prediction still new
                    if prediction.get_status() is PredictionStatus.NEW:
                        # Change poll (if prediction already saved)
                        if prediction.id is not None:
                            change_question_and_options_key = Keyboard(
                                text=phrases.PVT_KEY_PREDICTION_CHANGE_POLL,
                                screen=Screen.PVT_PREDICTION_CREATE,
                                info={ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_POLL_CHANGE},
                            )
                            inline_keyboard.append([change_question_and_options_key])

                        # Save
                        if prediction.id is None:
                            save_key = Keyboard(
                                text=phrases.KEY_SAVE,
                                screen=Screen.PVT_PREDICTION_CREATE,
                                info={ReservedKeyboardKeys.SCREEN_STEP: Step.END},
                            )
                            inline_keyboard.append([save_key])
                        else:  # Edit, automatically save
                            prediction.save()
                    else:
                        prediction.save()

                    ot_text = get_prediction_text(prediction, is_creator_recap=True, user=user)
                    user.set_context_data(context, ContextDataKey.CREATED_PREDICTION, prediction)

                case Step.REQUEST_CLOSE_DATE:  # Request close date
                    # Only if prediction in new or open
                    if not prediction.is_new_or_sent():
                        raise StepValidationException(phrases.PREDICTION_SETTING_CANNOT_BE_CHANGED)

                    go_to_next_step = False  # Stay in this step until close date is validated
                    if inbound_keyboard is not None:
                        timezone_text, offset_text = get_user_timezone_and_offset_text(user)
                        ot_text = phrases.PREDICTION_CREATE_REQUEST_CLOSE_DATE.format(
                            default_datetime_format(user.get_current_time()),
                            timezone_text,
                            offset_text,
                            get_deeplink(screen=Screen.PVT_SETTINGS_TIMEZONE),
                        )
                    else:  # Validate close date
                        if not prediction.is_new_or_sent():
                            raise StepValidationException(
                                phrases.PREDICTION_SETTING_CANNOT_BE_CHANGED
                            )
                        try:
                            close_date = get_datetime_from_natural_language(
                                update.message.text, user
                            )
                            if datetime_is_before(close_date):
                                raise DateValidationException(
                                    phrases.PREDICTION_CREATE_INVALID_CLOSE_DATE_PAST
                                )

                            prediction.end_date = close_date
                            user.set_context_data(
                                context, ContextDataKey.CREATED_PREDICTION, prediction
                            )

                            # Go back to request settings
                            user.private_screen_step = Step.REQUEST_SETTINGS
                            return await manage(
                                update, context, inbound_keyboard, user, is_refresh=True
                            )
                        except (AttributeError, DateValidationException) as e:
                            timezone_text, offset_text = get_user_timezone_and_offset_text(user)
                            ot_text = (
                                str(e)
                                if isinstance(e, DateValidationException) and e.message is not None
                                else phrases.PREDICTION_CREATE_INVALID_CLOSE_DATE
                            )
                            raise StepValidationException(
                                ot_text.format(
                                    default_datetime_format(user.get_current_time()),
                                    timezone_text,
                                    offset_text,
                                    get_deeplink(screen=Screen.PVT_SETTINGS_TIMEZONE),
                                )
                            )

                case Step.REQUEST_POLL_CHANGE:
                    ot_text = phrases.PREDICTION_CREATE_REQUEST_POLL
                    next_step = Step.REQUEST_SETTINGS

                    await set_back_button_to_settings(user)

                case Step.REQUEST_CUT_OFF_DATE:  # Request cut off date
                    if not prediction.is_closed():
                        raise StepValidationException(phrases.PREDICTION_SETTING_CANNOT_BE_CHANGED)

                    go_to_next_step = False  # Stay in this step until cut off date is validated
                    user.private_screen_stay_step = Step.REQUEST_SETTINGS
                    if inbound_keyboard is not None:
                        # Request input
                        if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
                            timezone_text, offset_text = get_user_timezone_and_offset_text(user)
                            ot_text = phrases.PREDICTION_CREATE_REQUEST_CUT_OFF_DATE.format(
                                default_datetime_format(prediction.send_date, user),
                                default_datetime_format(prediction.end_date, user),
                                (
                                    phrases.TEXT_NOT_SET
                                    if prediction.cut_off_date is None
                                    else default_datetime_format(prediction.cut_off_date, user)
                                ),
                                default_datetime_format(user.get_current_time()),
                                timezone_text,
                                offset_text,
                                get_deeplink(screen=Screen.PVT_SETTINGS_TIMEZONE),
                            )
                        else:  # Confirm
                            user.private_screen_stay_step = None
                            if inbound_keyboard.info[ReservedKeyboardKeys.CONFIRM]:
                                validate_cut_off_date(prediction.cut_off_date, prediction, user)
                                prediction.should_save = True
                                await cut_off_invalid_bets(context, prediction)

                            # Go back to request settings
                            user.private_screen_step = Step.REQUEST_SETTINGS
                            return await manage(
                                update, context, inbound_keyboard, user, is_refresh=True
                            )
                    else:  # Validate cut off date
                        try:
                            cut_off_date = get_datetime_from_natural_language(
                                update.message.text, user
                            )
                            try:
                                validate_cut_off_date(cut_off_date, prediction, user)
                            except DateValidationException as e:
                                raise StepValidationException(str(e))

                            # Request confirmation
                            prediction.cut_off_date = cut_off_date
                            prediction.should_save = False
                            user.set_context_data(
                                context, ContextDataKey.CREATED_PREDICTION, prediction
                            )

                            # Get bets that will be removed with this cut off
                            invalid_bets: list[PredictionOptionUser] = get_invalid_bets(
                                prediction, cut_off_date
                            )
                            total_removed_wager = sum([bet.wager for bet in invalid_bets])
                            ot_text = phrases.PREDICTION_CUT_OFF_DATE_CONFIRMATION_REQUEST.format(
                                default_datetime_format(cut_off_date, user),
                                len(invalid_bets),
                                total_removed_wager,
                            )

                            # Get yes no keyboard
                            inline_keyboard = [
                                get_yes_no_keyboard(
                                    user,
                                    screen=Screen.PVT_PREDICTION_CREATE,
                                    extra_keys={
                                        ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_CUT_OFF_DATE
                                    },
                                )
                            ]
                        except (AttributeError, DateValidationException) as e:
                            timezone_text, offset_text = get_user_timezone_and_offset_text(user)
                            ot_text = (
                                str(e)
                                if isinstance(e, DateValidationException) and e.message is not None
                                else phrases.PREDICTION_CREATE_INVALID_CLOSE_DATE
                            )
                            raise StepValidationException(
                                ot_text.format(
                                    default_datetime_format(user.get_current_time()),
                                    timezone_text,
                                    offset_text,
                                    get_deeplink(screen=Screen.PVT_SETTINGS_TIMEZONE),
                                )
                            )

                case Step.END:  # End
                    # Create prediction
                    prediction.save()
                    # Save options
                    await save_prediction_options(prediction)

                    # Add prediction creation cooldown
                    user.prediction_creation_cooldown_end_date = get_datetime_in_future_hours(
                        Env.PREDICTION_CREATE_COOLDOWN_DURATION.get_int()
                    )

                    # Reset user private screen
                    user.reset_private_screen()
                    # Show saved alert
                    ot_text = phrases.PREDICTION_CREATE_SUCCESS
                    await full_message_send(context, str(ot_text), update=update, show_alert=True)

                    return await go_to_prediction_detail(
                        context, inbound_keyboard, prediction, update, user
                    )
                case _:
                    raise PrivateChatException(PrivateChatError.UNKNOWN_EXTRA_STEP)

            if next_step is not None:
                user.private_screen_step = next_step
            elif user.private_screen_step is not None and go_to_next_step:
                user.private_screen_step += 1
        except StepValidationException as e:
            if prediction and prediction.id is not None:
                await set_back_button_to_settings(user)
            ot_text = str(e)

        if prediction is not None and prediction.id is not None:
            if Step(user.private_screen_step) == Step.REQUEST_SETTINGS:
                # From edit prediction, back button should go back to prediction detail
                if (
                    inbound_keyboard is not None
                    and ReservedKeyboardKeys.SCREEN_STEP in inbound_keyboard.info
                    and not is_refresh
                ):
                    # noinspection PyTypeChecker
                    inbound_keyboard.info.pop(ReservedKeyboardKeys.SCREEN_STEP)
                    user.reset_private_screen()

            if (
                inbound_keyboard is not None
                and PredictionCreateReservedKeys.PREDICTION_ID in inbound_keyboard.info
            ):
                # noinspection PyTypeChecker
                inbound_keyboard.info[PredictionCreateReservedKeys.PREDICTION_ID] = prediction.id

        # Send message
        await full_message_send(
            context,
            str(ot_text),
            update=update,
            inbound_keyboard=inbound_keyboard,
            previous_screens=user.get_private_screen_list(),
            keyboard=inline_keyboard,
            user=user,
        )


def validate_cut_off_date(cut_off_date: datetime, prediction: Prediction, user: User):
    """
    Validate cut off date
    :param cut_off_date: The cut off date
    :param prediction: The prediction
    :param user: The user
    :return: None, raises exception if invalid
    """

    try:
        # Is before send time
        if datetime_is_before(cut_off_date, prediction.send_date):
            raise DateValidationException()

        # Is after end date
        if not datetime_is_before(cut_off_date, prediction.end_date):
            raise DateValidationException()

        # Is after previous cut off date
        prediction_saved = Prediction.get_by_id(prediction.id)
        if prediction_saved.cut_off_date is not None and not datetime_is_before(
            cut_off_date, prediction_saved.cut_off_date
        ):
            raise DateValidationException()

    except DateValidationException:
        timezone_text, offset_text = get_user_timezone_and_offset_text(user)
        raise DateValidationException(
            phrases.PREDICTION_CREATE_INVALID_CUT_OFF_DATE.format(
                default_datetime_format(prediction.send_date, user),
                default_datetime_format(prediction.end_date, user),
                (
                    phrases.TEXT_NOT_SET
                    if prediction.cut_off_date is None
                    else default_datetime_format(prediction.cut_off_date, user)
                ),
                default_datetime_format(user.get_current_time()),
                timezone_text,
                offset_text,
                get_deeplink(screen=Screen.PVT_SETTINGS_TIMEZONE),
            )
        )


async def set_back_button_to_settings(user):
    """
    Set back button to settings
    :param user: The user
    """

    # For back button, stay on this screen
    user.private_screen_stay = True
    user.private_screen_stay_step = Step.REQUEST_SETTINGS


async def save_prediction_options(prediction: Prediction):
    """
    Save prediction options
    :param prediction: The prediction
    :return: None
    """
    # Delete old options
    PredictionOption.delete().where(PredictionOption.prediction == prediction).execute()

    for i, option in enumerate(prediction.options):
        if str(option).strip() != "":
            prediction_option = PredictionOption()
            prediction_option.prediction = prediction
            prediction_option.number = i + 1
            prediction_option.option = option
            prediction_option.save()


async def go_to_prediction_detail(
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard | None,
    prediction: Prediction,
    update: Update,
    user: User,
):
    """
    Go to prediction detail screen
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param prediction: The prediction
    :param update: The update
    :param user: The user
    :return: None
    """

    # Remove prediction from context
    user.remove_context_data(context, ContextDataKey.CREATED_PREDICTION)

    # Go to prediction detail screen removing last screen
    user.remove_last_private_screen()
    inbound_keyboard.screen = Screen.PVT_PREDICTION_DETAIL
    inbound_keyboard.info = {PredictionDetailReservedKeys.PREDICTION_ID: prediction.id}
    inbound_keyboard.previous_screen_list = user.get_private_screen_list()

    from src.chat.private.screens.screen_prediction_detail import (
        manage as prediction_detail_manage,
    )

    return await prediction_detail_manage(update, context, inbound_keyboard, user)


async def validate(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> bool:
    """
    Validate the prediction create screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    """

    try:
        # Prediction creation cooldown active
        if not datetime_is_before(user.prediction_creation_cooldown_end_date):
            raise PredictionException(
                phrases.PREDICTION_CREATE_COOLDOWN_ACTIVE.format(
                    get_remaining_duration(user.prediction_creation_cooldown_end_date)
                )
            )
    except PredictionException as e:
        await full_message_send(context, str(e), update=update, inbound_keyboard=inbound_keyboard)
        return False

    return True
