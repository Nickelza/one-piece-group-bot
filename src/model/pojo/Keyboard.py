import json
import constants as c
from src.model.enums.GroupScreen import GroupScreen

from telegram import CallbackQuery


class Keyboard:
    def __init__(self, text: str, screen: GroupScreen, info: dict, url: str = None):
        self.text = text
        self.screen: GroupScreen = screen
        self.info: dict = info
        self.url: str = url

        # Create string data
        info_with_screen = info.copy()
        info_with_screen[c.SCREEN_CODE] = screen.value
        self.callback_data: str = json.dumps(info_with_screen)


def get_keyboard_from_callback_query(callback_query: CallbackQuery):
    """
    Create a Keyboard object from a CallbackQuery object
    :param callback_query: CallbackQuery object
    :return: Keyboard object
    """
    info: dict = json.loads(callback_query.data)

    screen: GroupScreen = GroupScreen.SCREEN_UNKNOWN
    try:
        screen = GroupScreen(int(info[c.SCREEN_CODE]))
    except ValueError:
        screen = GroupScreen.SCREEN_UNKNOWN

    text: str = ''

    return Keyboard(text, screen, info)
