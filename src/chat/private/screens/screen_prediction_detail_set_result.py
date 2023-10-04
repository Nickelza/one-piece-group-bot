from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import constants as c
from resources import phrases
from src.chat.private.screens.screen_prediction_create import go_to_prediction_detail
from src.model.Prediction import Prediction
from src.model.PredictionOption import PredictionOption
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.PredictionStatus import PredictionStatus
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send, get_yes_no_keyboard, escape_valid_markdown_chars
from src.service.prediction_service import set_results


class PredictionDetailsSetResultReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    PREDICTION_ID = 'a'
    CORRECT_OPTIONS = 'b'
    OPTION_NUMBER = 'c'
    NO_CORRECT_OPTION = 'd'
    CONFIRM = 'e'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the prediction detail set result screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    prediction: Prediction = Prediction.get(
        Prediction.id == inbound_keyboard.get_int(PredictionDetailsSetResultReservedKeys.PREDICTION_ID))

    # Check that prediction is in closed status
    if prediction.get_status() is not PredictionStatus.BETS_CLOSED:
        await full_message_send(context, phrases.PREDICTION_IN_WRONG_STATUS, update=update,
                                inbound_keyboard=inbound_keyboard)
        return

    correct_options_numbers = inbound_keyboard.get(PredictionDetailsSetResultReservedKeys.CORRECT_OPTIONS)
    if correct_options_numbers is None:
        correct_options_numbers = []

    if PredictionDetailsSetResultReservedKeys.CONFIRM not in inbound_keyboard.info:
        # An option has been selected
        if PredictionDetailsSetResultReservedKeys.OPTION_NUMBER in inbound_keyboard.info:
            # Add or remove the option from the list of correct options
            option_number = inbound_keyboard.get_int(PredictionDetailsSetResultReservedKeys.OPTION_NUMBER)
            if option_number in correct_options_numbers:
                correct_options_numbers.remove(option_number)
            else:
                correct_options_numbers.append(option_number)

        # No correct option has been selected, remove all correct options
        if PredictionDetailsSetResultReservedKeys.NO_CORRECT_OPTION in inbound_keyboard.info:
            correct_options_numbers = []
    else:
        # Send confirmation request message
        if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
            if len(correct_options_numbers) == 0:
                correct_options_text = phrases.PREDICTION_SET_RESULT_CONFIRMATION_REQUEST_NO_CORRECT_OPTION
            else:
                correct_options_text = ''
                for option_number in correct_options_numbers:
                    prediction_option: PredictionOption = PredictionOption.get(
                        PredictionOption.prediction == prediction, PredictionOption.number == option_number)
                    correct_options_text += phrases.PREDICTION_TEXT_OPTION.format(
                        option_number, prediction_option.option)

            ot_text = phrases.PREDICTION_SET_RESULT_CONFIRMATION_REQUEST.format(correct_options_text)
            inline_keyboard: list[list[Keyboard]] = [
                get_yes_no_keyboard(
                    user, inbound_keyboard=inbound_keyboard, add_inbound_key_info=True,
                    keys_to_exclude=[ReservedKeyboardKeys.PREVIOUS_SCREEN,
                                     PredictionDetailsSetResultReservedKeys.OPTION_NUMBER])]  # To save space
            await full_message_send(context, ot_text, update=update, inbound_keyboard=inbound_keyboard,
                                    keyboard=inline_keyboard)
            return
        else:  # Confirm or cancel
            if inbound_keyboard.get_bool(ReservedKeyboardKeys.CONFIRM):
                PredictionOption.update(is_correct=True).where(
                    PredictionOption.prediction == prediction,
                    PredictionOption.number.in_(correct_options_numbers)).execute()

                await set_results(context, prediction)

                # Correct options have been set, show alert
                await full_message_send(context, phrases.PREDICTION_SET_RESULT_SUCCESS, update=update,
                                        show_alert=True)

                # Go back to details
                return await go_to_prediction_detail(context, inbound_keyboard, prediction, update, user)

            # Remove confirm key
            inbound_keyboard.info.pop(PredictionDetailsSetResultReservedKeys.CONFIRM)
            inbound_keyboard.info.pop(ReservedKeyboardKeys.CONFIRM)

    # Build text and keyboard
    options_text = ''
    inline_keyboard: list[list[Keyboard]] = []
    keyboard_line: list[Keyboard] = []
    prediction_options: list[PredictionOption] = PredictionOption.select().where(
        PredictionOption.prediction == prediction).order_by(PredictionOption.number.asc())

    inbound_info_without_not_correct_option = inbound_keyboard.info.copy()
    if PredictionDetailsSetResultReservedKeys.NO_CORRECT_OPTION in inbound_info_without_not_correct_option:
        inbound_info_without_not_correct_option.pop(PredictionDetailsSetResultReservedKeys.NO_CORRECT_OPTION)
    for index, prediction_option in enumerate(prediction_options):
        current_number = prediction_option.number
        correct_emoji = Emoji.CORRECT if current_number in correct_options_numbers else ''
        options_text += phrases.PREDICTION_TEXT_OPTION.format(
            current_number, escape_valid_markdown_chars(prediction_option.option)) + correct_emoji

        # Build keyboard
        button_info = {PredictionDetailsSetResultReservedKeys.OPTION_NUMBER: current_number,
                       PredictionDetailsSetResultReservedKeys.CORRECT_OPTIONS: correct_options_numbers}
        button = Keyboard(correct_emoji + str(current_number), info=button_info,
                          inbound_info=inbound_info_without_not_correct_option)
        keyboard_line.append(button)

        # Add new keyboard line if needed
        if (index + 1) % c.STANDARD_LIST_KEYBOARD_ROW_SIZE == 0 and index != 0:
            inline_keyboard.append(keyboard_line)
            keyboard_line = []

    # Add the last keyboard line if needed
    if len(keyboard_line) > 0:
        inline_keyboard.append(keyboard_line)

    # Add no correct option button
    button_info = {PredictionDetailsSetResultReservedKeys.NO_CORRECT_OPTION: True}
    no_correct_option_emoji = Emoji.ENABLED if len(correct_options_numbers) == 0 else ''
    button = Keyboard(no_correct_option_emoji + phrases.PVT_KEY_PREDICTION_NO_CORRECT_OPTION, info=button_info,
                      inbound_info=inbound_keyboard.info)
    inline_keyboard.append([button])

    # Add confirm button
    button_info = {PredictionDetailsSetResultReservedKeys.CONFIRM: True}
    button = Keyboard(phrases.KEY_CONFIRM, info=button_info, inbound_info=inbound_keyboard.info)
    inline_keyboard.append([button])

    ot_text = phrases.PREDICTION_SET_RESULT.format(escape_valid_markdown_chars(prediction.question), options_text)

    await full_message_send(context, ot_text, update=update, keyboard=inline_keyboard,
                            inbound_keyboard=inbound_keyboard)
