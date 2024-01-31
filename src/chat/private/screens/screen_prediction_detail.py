from datetime import datetime
from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.private.screens.screen_prediction import PredictionListPage
from src.model.Prediction import Prediction
from src.model.User import User
from src.model.enums.PredictionStatus import PredictionStatus
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.date_service import get_remaining_duration
from src.service.message_service import full_message_send, get_yes_no_keyboard
from src.service.prediction_service import (
    user_has_bet_on_prediction,
    delete_prediction,
    get_share_text,
    close_bets,
)


class PredictionDetailReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    PREDICTION_ID = "a"
    EDIT = "b"
    DELETE = "c"
    OPEN = "d"
    CLOSE = "e"


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the prediction detail screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    prediction_list_page = PredictionListPage()

    prediction_list_page.user = user
    # TODO Add init_legend_filter_results() when legend is implemented
    prediction_list_page.set_object(
        inbound_keyboard.get_int(PredictionDetailReservedKeys.PREDICTION_ID)
    )

    prediction: Prediction = prediction_list_page.object
    inline_keyboard: list[list[Keyboard]] = []

    # Delete prediction
    if PredictionDetailReservedKeys.DELETE in inbound_keyboard.info:
        if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
            # Request confirmation
            inline_keyboard = [
                get_yes_no_keyboard(
                    user, inbound_keyboard=inbound_keyboard, add_inbound_key_info=True
                )
            ]

            ot_text = phrases.PREDICTION_DELETE_CONFIRMATION.format(
                get_remaining_duration(user.prediction_creation_cooldown_end_date)
            )
            await full_message_send(
                context,
                ot_text,
                update=update,
                keyboard=inline_keyboard,
                inbound_keyboard=inbound_keyboard,
                add_back_button=False,
            )
            return
        else:
            is_confirmed = inbound_keyboard.get_bool(ReservedKeyboardKeys.CONFIRM)
            inbound_keyboard.info.pop(PredictionDetailReservedKeys.DELETE)
            inbound_keyboard.info.pop(ReservedKeyboardKeys.CONFIRM)

            if is_confirmed:
                await delete_prediction(prediction)
                # Return to prediction list
                await full_message_send(
                    context, phrases.PREDICTION_DELETE_SUCCESS, update=update, show_alert=True
                )
                from src.chat.private.screens.screen_prediction import manage as manage_prediction

                inbound_keyboard.info.pop(PredictionDetailReservedKeys.PREDICTION_ID)
                inbound_keyboard.set_screen(Screen.PVT_PREDICTION)

                user.remove_last_private_screen()
                inbound_keyboard.previous_screen_list = user.get_private_screen_list()
                return await manage_prediction(update, context, inbound_keyboard, user)

    # Open prediction
    if PredictionDetailReservedKeys.OPEN in inbound_keyboard.info:
        if prediction.get_status() is not PredictionStatus.NEW:
            await full_message_send(
                context, phrases.PREDICTION_ALREADY_OPEN, update=update, show_alert=True
            )
        elif ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
            # Request confirmation
            inline_keyboard = [
                get_yes_no_keyboard(
                    user, inbound_keyboard=inbound_keyboard, add_inbound_key_info=True
                )
            ]

            ot_text = phrases.PREDICTION_OPEN_CONFIRMATION.format(
                get_remaining_duration(user.prediction_creation_cooldown_end_date)
            )
            await full_message_send(
                context,
                ot_text,
                update=update,
                keyboard=inline_keyboard,
                inbound_keyboard=inbound_keyboard,
                add_back_button=False,
            )
            return
        else:
            is_confirmed = inbound_keyboard.get_bool(ReservedKeyboardKeys.CONFIRM)
            inbound_keyboard.info.pop(PredictionDetailReservedKeys.OPEN)
            inbound_keyboard.info.pop(ReservedKeyboardKeys.CONFIRM)

            if is_confirmed:
                prediction.status = PredictionStatus.SENT
                prediction.send_date = datetime.now()
                prediction.save()

                await full_message_send(
                    context, phrases.PREDICTION_OPEN_SUCCESS, update=update, show_alert=True
                )

    # Close prediction
    if PredictionDetailReservedKeys.CLOSE in inbound_keyboard.info:
        if prediction.get_status() is not PredictionStatus.SENT:
            await full_message_send(
                context, phrases.PREDICTION_ALREADY_CLOSED, update=update, show_alert=True
            )
        elif ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
            # Request confirmation
            inline_keyboard = [
                get_yes_no_keyboard(
                    user, inbound_keyboard=inbound_keyboard, add_inbound_key_info=True
                )
            ]

            ot_text = phrases.PREDICTION_CLOSE_CONFIRMATION.format(
                get_remaining_duration(user.prediction_creation_cooldown_end_date)
            )
            await full_message_send(
                context,
                ot_text,
                update=update,
                keyboard=inline_keyboard,
                inbound_keyboard=inbound_keyboard,
                add_back_button=False,
            )
            return
        else:
            is_confirmed = inbound_keyboard.get_bool(ReservedKeyboardKeys.CONFIRM)
            inbound_keyboard.info.pop(PredictionDetailReservedKeys.CLOSE)
            inbound_keyboard.info.pop(ReservedKeyboardKeys.CONFIRM)

            if is_confirmed:
                await close_bets(context, prediction)
                await full_message_send(
                    context, phrases.PREDICTION_CLOSE_SUCCESS, update=update, show_alert=True
                )

    if prediction.is_open():
        if should_show_place_bet_button(prediction, user):
            button_info = {PredictionDetailReservedKeys.PREDICTION_ID: prediction.id}
            inline_keyboard.append([
                Keyboard(
                    phrases.PVT_KEY_PREDICTION_DETAIL_PLACE_BET,
                    screen=Screen.PVT_PREDICTION_DETAIL_PLACE_BET,
                    info=button_info,
                )
            ])

        if should_show_remove_bet_button(prediction, user):
            button_info = {PredictionDetailReservedKeys.PREDICTION_ID: prediction.id}
            inline_keyboard.append([
                Keyboard(
                    phrases.PVT_KEY_PREDICTION_DETAIL_REMOVE_BET,
                    screen=Screen.PVT_PREDICTION_DETAIL_REMOVE_BET,
                    info=button_info,
                )
            ])

    # Creator management buttons
    if prediction.creator == user:
        # Open button if prediction is in new status
        if prediction.get_status() is PredictionStatus.NEW:
            button_info = {
                PredictionDetailReservedKeys.PREDICTION_ID: prediction.id,
                PredictionDetailReservedKeys.OPEN: True,
            }
            inline_keyboard.append(
                [Keyboard(phrases.KEY_OPEN, screen=Screen.PVT_PREDICTION_DETAIL, info=button_info)]
            )

        # Close button if prediction is in sent status
        if prediction.get_status() is PredictionStatus.SENT:
            button_info = {
                PredictionDetailReservedKeys.PREDICTION_ID: prediction.id,
                PredictionDetailReservedKeys.CLOSE: True,
            }
            inline_keyboard.append([
                Keyboard(phrases.KEY_CLOSE, screen=Screen.PVT_PREDICTION_DETAIL, info=button_info)
            ])

        # Send to group if is sent status
        if prediction.get_status() is PredictionStatus.SENT:
            button_info = {PredictionDetailReservedKeys.PREDICTION_ID: prediction.id}
            inline_keyboard.append([
                Keyboard(
                    phrases.KEY_SEND_TO_GROUP,
                    screen=Screen.PVT_PREDICTION_DETAIL_SEND_TO_GROUP,
                    info=button_info,
                )
            ])

        # Set result button if is closed status
        if prediction.get_status() is PredictionStatus.BETS_CLOSED:
            button_info = {PredictionDetailReservedKeys.PREDICTION_ID: prediction.id}
            inline_keyboard.append([
                Keyboard(
                    phrases.KEY_SET_RESULT,
                    screen=Screen.PVT_PREDICTION_DETAIL_SET_RESULT,
                    info=button_info,
                )
            ])

        # Edit button
        from src.chat.private.screens.screen_prediction_create import Step as PredictionCreateStep

        button_info = {
            PredictionDetailReservedKeys.PREDICTION_ID: prediction.id,
            PredictionDetailReservedKeys.EDIT: True,
            ReservedKeyboardKeys.SCREEN_STEP: PredictionCreateStep.REQUEST_SETTINGS,
        }
        inline_keyboard.append([
            Keyboard(
                phrases.PVT_KEY_PREDICTION_DETAIL_EDIT,
                screen=Screen.PVT_PREDICTION_CREATE,
                info=button_info,
            )
        ])

        # Delete button
        button_info = {
            PredictionDetailReservedKeys.PREDICTION_ID: prediction.id,
            PredictionDetailReservedKeys.DELETE: True,
        }
        inline_keyboard.append([
            Keyboard(
                phrases.KEYBOARD_OPTION_DELETE,
                screen=Screen.PVT_PREDICTION_DETAIL,
                info=button_info,
            )
        ])

        # Share button if is sent
        if prediction.get_status() is PredictionStatus.SENT:
            inline_keyboard.append([
                Keyboard(
                    phrases.KEY_SHARE,
                    switch_inline_query=get_share_text(context, user, prediction),
                )
            ])

    await full_message_send(
        context,
        prediction_list_page.get_item_detail_text(),
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )


def should_show_place_bet_button(prediction: Prediction, user: User) -> bool:
    """
    Check if the user should see the place bet button.
    :param prediction: The prediction
    :param user: The user
    :return: True if the user should see the place bet button
    """

    # Accepts multiple bets
    if prediction.allow_multiple_choices:
        return True

    # Prediction does not accept multiple bets, show button if user has not bet
    return not user_has_bet_on_prediction(prediction, user)


def should_show_remove_bet_button(prediction: Prediction, user: User) -> bool:
    """
    Check if the user should see the remove bet button.
    :param prediction: The prediction
    :param user: The user
    :return: True if the user should see the remove bet button
    """

    # Does not accept bet withdrawal
    if not prediction.can_withdraw_bet:
        return False

    # Prediction accepts bet withdrawal, show button if user has bet
    return user_has_bet_on_prediction(prediction, user)
