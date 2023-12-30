from enum import IntEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.chat.group.screens.screen_prediction_bet import validate
from src.chat.private.screens.screen_prediction_detail_place_bet import (
    PredictionPlaceBetReservedKeys,
)
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.User import User
from src.model.error.PrivateChatError import PrivateChatError, PrivateChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import (
    full_message_send,
    get_create_or_edit_status,
    escape_valid_markdown_chars,
)
from src.service.prediction_service import save_prediction_option_user


class Step(IntEnum):
    REQUEST_AMOUNT = 0
    END = 1


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the place bet send amount screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    should_ignore_input, should_create_item, should_validate_input = get_create_or_edit_status(
        user, inbound_keyboard
    )

    if not should_ignore_input:
        # Validate that the user can bet on this prediction
        if inbound_keyboard is not None:
            prediction_option: PredictionOption = PredictionOption.get_by_id(
                inbound_keyboard.get(PredictionPlaceBetReservedKeys.PREDICTION_OPTION_ID)
            )
        else:
            prediction_option: PredictionOption = PredictionOption.get_by_id(
                user.private_screen_in_edit_id
            )

        try:
            amount = update.message.text
        except AttributeError:
            amount = None

        prediction: Prediction = prediction_option.prediction
        previous_screens = user.get_private_screen_list()[:-1]
        previous_screen_list_keyboard_info = {
            PredictionPlaceBetReservedKeys.PREDICTION_ID: prediction.id
        }

        validation_tuple = await validate(
            update,
            context,
            user,
            amount=amount,
            inbound_keyboard=inbound_keyboard,
            prediction_option=prediction_option,
            previous_screens=previous_screens,
            previous_screen_list_keyboard_info=previous_screen_list_keyboard_info,
        )

        for validation in validation_tuple:
            if validation is None:  # Validation failed, error message sent in validate method
                return

        user.private_screen_in_edit_id = prediction_option.id

        if user.private_screen_step is None:
            user.private_screen_step = Step.REQUEST_AMOUNT

        match Step(user.private_screen_step):
            case Step.REQUEST_AMOUNT:  # Request amount
                ot_text = phrases.PREDICTION_PLACE_BET_DETAIL_TEXT.format(
                    escape_valid_markdown_chars(prediction.question),
                    escape_valid_markdown_chars(prediction_option.option),
                )

            case Step.END:  # End
                wager: int = validation_tuple[2]
                await save_prediction_option_user(prediction_option, user, wager)

                # Bet success message
                ot_text = phrases.PREDICTION_BET_SUCCESS

                # Return to the prediction detail screen, skipping the place bet screen
                previous_screens = previous_screens[:-1]

                # Reset user private screen
                user.reset_private_screen()

            case _:
                raise PrivateChatException(PrivateChatError.UNKNOWN_EXTRA_STEP)

        if user.private_screen_step is not None:
            user.private_screen_step += 1

        # Send message
        await full_message_send(
            context,
            str(ot_text),
            update=update,
            inbound_keyboard=inbound_keyboard,
            previous_screens=previous_screens,
            previous_screen_list_keyboard_info=previous_screen_list_keyboard_info,
        )
