import resources.phrases as phrases
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

    return prefix + '\n' + enabled_disabled_text


def get_toggle_keyboard(enabled: bool, screen: Screen) -> Keyboard:
    """
    Get the toggle keyboard
    :param enabled: The enabled/disabled status
    :param screen: The screen
    :return: The toggle keyboard
    """

    return Keyboard(
        (phrases.DISABLE if enabled else phrases.ENABLE),
        info={'a': (not enabled)},
        screen=screen
    )
