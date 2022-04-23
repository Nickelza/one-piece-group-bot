import json

from telegram import CallbackQuery

import constants as c
from src.model.enums.Screen import Screen


class Keyboard:
    def __init__(self, text: str, info: dict, screen: Screen = None, url: str = None):
        self.text = text
        self.screen = screen
        self.info: dict = info
        self.url: str = url

        # Create string data
        info_with_screen = info.copy()
        if screen is not None:
            info_with_screen[c.SCREEN_CODE] = screen.value
        self.callback_data: str = json.dumps(info_with_screen)


def get_keyboard_from_callback_query(callback_query: CallbackQuery):
    """
    Create a Keyboard object from a CallbackQuery object
    :param callback_query: CallbackQuery object
    :return: Keyboard object
    """
    info: dict = json.loads(callback_query.data)

    try:
        if c.SCREEN_CODE in info:
            screen = Screen(info[c.SCREEN_CODE])
        else:
            screen = None
    except (ValueError, KeyError):
        screen = Screen.UNKOWN

    text: str = ''

    return Keyboard(text, info, screen)
