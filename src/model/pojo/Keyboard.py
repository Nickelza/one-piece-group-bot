import base64
import json

from telegram import CallbackQuery

import resources.Environment as Env
from src.model.User import User
from src.model.enums.MessageSource import MessageSource
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen


class Keyboard:
    def __init__(self, text: str, info: dict = None, screen: Screen = None, previous_screen_list: list[Screen] = None,
                 url: str = None, inherit_authorized_users: bool = True, authorized_users: list[User] = None,
                 inbound_info: dict = None, from_deeplink: bool = False, is_deeplink: bool = False):
        """
        Creates a keyboard object
        :param text: The text to be displayed on the keyboard
        :param info: The info embedded in the keyboard callback data
        :param screen: The screen to transition to
        :param previous_screen_list: The previous screens list
        :param url: The url to be displayed on the keyboard
        :param inherit_authorized_users: If the authorized users list should be inherited from the default value
        :param authorized_users: The authorized users list
        :param inbound_info: The inbound info to be added to the keyboard info
        :param from_deeplink: If the keyboard is being created from a deeplink
        :param is_deeplink: If the keyboard is a deeplink, generate the deeplink url
        """
        self.text = text
        self.info: dict = info if info is not None else {}
        self.screen: Screen = screen
        self.previous_screen_list: list[Screen] = previous_screen_list if previous_screen_list is not None else []
        self.url: str = url
        self.callback_data: str = self.create_callback_data()
        self.inherit_authorized_users: bool = inherit_authorized_users
        self.authorized_users: list[User] = authorized_users if authorized_users is not None else []
        self.from_deeplink: bool = from_deeplink
        self.is_deeplink: bool = is_deeplink

        if inbound_info is not None:
            self.info = inbound_info | self.info

        if self.is_deeplink:
            self.set_deeplink_url(self.screen)

    def create_callback_data(self) -> str:
        """
        Creates the callback data for the keyboard
        :return: The callback data
        """

        # Create string data
        info_with_screen = self.info.copy()

        if self.screen is not None:
            info_with_screen[ReservedKeyboardKeys.SCREEN] = int(self.screen[1:])

        temp_screen_code: int = (info_with_screen[ReservedKeyboardKeys.SCREEN]
                                 if ReservedKeyboardKeys.SCREEN in info_with_screen else None)

        if self.previous_screen_list is not None and len(self.previous_screen_list) > 0:
            info_with_screen[ReservedKeyboardKeys.PREVIOUS_SCREEN] = [
                int(screen[1:]) for screen in self.previous_screen_list if int(screen[1:]) != temp_screen_code]

        # Convert boolean to int
        for key, value in info_with_screen.items():
            if isinstance(value, bool):
                info_with_screen[key] = int(value)

        return json.dumps(info_with_screen, separators=(',', ':'))

    def refresh_callback_data(self):
        """
        Refreshes the callback data of the keyboard
        """
        self.callback_data = self.create_callback_data()

    @staticmethod
    def get_from_callback_query_or_info(message_source: MessageSource, callback_query: CallbackQuery = None,
                                        info_str: str = None, from_deeplink: bool = False) -> 'Keyboard':
        """
        Create a Keyboard object from a CallbackQuery object
        :param callback_query: CallbackQuery object
        :param message_source: Source of the message
        :param info_str: The info to be added to the keyboard info
        :param from_deeplink: If the keyboard is being created from a deeplink
        :return: Keyboard object
        """

        if callback_query is None and info_str is None:
            raise ValueError('Either callback_query or info must be provided')

        if info_str is not None:
            info: dict = json.loads(info_str)
        else:
            info: dict = json.loads(callback_query.data)

        try:
            if ReservedKeyboardKeys.SCREEN in info:
                screen = Screen(message_source + str(info[ReservedKeyboardKeys.SCREEN]))
            else:
                screen = None
        except (ValueError, KeyError):
            screen = Screen.UNKNOWN

        if ReservedKeyboardKeys.PREVIOUS_SCREEN in info:
            previous_screen_list = [
                Screen(message_source + str(screen)) for screen in info[ReservedKeyboardKeys.PREVIOUS_SCREEN]]
        else:
            previous_screen_list = []

        text: str = ''

        return Keyboard(text, info=info, screen=screen, previous_screen_list=previous_screen_list,
                        from_deeplink=from_deeplink)

    def get(self, key: str):
        """
        Get a value from the keyboard info
        :param key: The key
        :return: The value
        """

        return self.info.get(key)

    def get_int(self, key: str):
        """
        Get an int value from the keyboard info
        :param key: The key
        :return: The value
        """

        return int(self.info.get(key))

    def get_bool(self, key: str):
        """
        Get a bool value from the keyboard info
        :param key: The key
        :return: The value
        """

        return bool(self.info.get(key))

    def set_deeplink_url(self, screen):
        """
        Set the deeplink url for the keyboard
        """

        encoded_bytes = self.callback_data.encode('utf-8')
        encoded_string = base64.b64encode(encoded_bytes).decode('utf-8')

        self.url = f'https://t.me/{Env.BOT_USERNAME.get()}?start={encoded_string}'
