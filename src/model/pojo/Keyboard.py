import json

from telegram import CallbackQuery

import constants as c
from src.model.enums.MessageSource import MessageSource
from src.model.enums.Screen import Screen


class Keyboard:
    def __init__(self, text: str, info: dict = None, screen: Screen = None, previous_screen_list: list[Screen] = None,
                 url: str = None):
        """
        Creates a keyboard object
        :param text: The text to be displayed on the keyboard
        :param info: The info embedded in the keyboard callback data
        :param screen: The screen to transition to
        :param previous_screen_list: The previous screens list
        :param url: The url to be displayed on the keyboard
        """
        self.text = text
        self.info: dict = info
        self.screen: Screen = screen
        self.previous_screen_list: list[Screen] = previous_screen_list if previous_screen_list is not None else []
        self.url: str = url
        self.callback_data: str = self.create_callback_data()

    def create_callback_data(self) -> str:
        """
        Creates the callback data for the keyboard
        :return: The callback data
        """

        # Create string data
        if self.info is not None:
            info_with_screen = self.info.copy()
        else:
            info_with_screen = {}

        if self.screen is not None:
            info_with_screen[c.SCREEN_CODE] = int(self.screen.value[1:])

        if self.previous_screen_list is not None:
            info_with_screen[c.PREVIOUS_SCREEN_CODE] = [int(screen.value[1:]) for screen in self.previous_screen_list]

        return json.dumps(info_with_screen, separators=(',', ':'))

    def refresh_callback_data(self):
        """
        Refreshes the callback data of the keyboard
        """
        self.callback_data = self.create_callback_data()


def get_keyboard_from_callback_query(callback_query: CallbackQuery, message_source: MessageSource):
    """
    Create a Keyboard object from a CallbackQuery object
    :param callback_query: CallbackQuery object
    :param message_source: Source of the message
    :return: Keyboard object
    """
    info: dict = json.loads(callback_query.data)

    try:
        if c.SCREEN_CODE in info:
            screen = Screen(message_source.value + str(info[c.SCREEN_CODE]))
        else:
            screen = None
    except (ValueError, KeyError):
        screen = Screen.UNKOWN

    if c.PREVIOUS_SCREEN_CODE in info:
        previous_screen_list = [Screen(message_source.value + str(screen)) for screen in info[c.PREVIOUS_SCREEN_CODE]]
    else:
        previous_screen_list = []

    text: str = ''

    return Keyboard(text, info=info, screen=screen, previous_screen_list=previous_screen_list)
