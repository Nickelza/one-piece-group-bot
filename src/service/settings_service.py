import resources.phrases as phrases
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard


def get_current_setting_text(enabled: bool, prefix: str = '') -> str:
    """
    Get the current setting text
    :param enabled: The enabled/disabled status
    :param prefix: The prefix
    :return: The current setting text
    """

    if enabled:
        enabled_disabled_text = phrases.CURRENT_SETTING.format(phrases.ENABLED)
    else:
        enabled_disabled_text = phrases.CURRENT_SETTING.format(phrases.DISABLED)

    return prefix + '\n\n' + enabled_disabled_text


def get_toggle_keyboard(enabled: bool, screen: Screen, inbound_keyboard: Keyboard) -> Keyboard:
    """
    Get the toggle keyboard
    :param enabled: The enabled/disabled current status
    :param screen: The screen
    :param inbound_keyboard: The inbound keyboard. If not None, adds the inbound keyboard info to the new keyboard
    :return: The toggle keyboard
    """

    default_keyboard_data = inbound_keyboard.info if inbound_keyboard is not None else {}

    return Keyboard(
        (phrases.DISABLE if enabled else phrases.ENABLE),
        info=default_keyboard_data | {ReservedKeyboardKeys.TOGGLE: (not enabled)},
        screen=screen
    )
