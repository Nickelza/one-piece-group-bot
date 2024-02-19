import hashlib
import json
import logging

from telegram import CallbackQuery
from telegram.ext import ContextTypes

import constants as c
from src.model.User import User
from src.model.enums.ContextDataKey import ContextDataKey
from src.model.enums.MessageSource import MessageSource
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen


class Keyboard:
    def __init__(
        self,
        text: str,
        info: dict = None,
        screen: Screen = None,
        previous_screen_list: list[Screen] = None,
        url: str = None,
        inherit_authorized_users: bool = True,
        authorized_users: list[User] = None,
        inbound_info: dict = None,
        from_deeplink: bool = False,
        is_deeplink: bool = False,
        only_authorized_users_can_interact: bool = True,
        switch_inline_query: str = None,
        exclude_key_from_inbound_info: list[str] = None,
    ):
        """
        Creates a keyboard object
        :param text: The text to be displayed on the keyboard
        :param info: The info embedded in the keyboard callback data
        :param screen: The screen to transition to
        :param previous_screen_list: The previous screens list
        :param url: The url to be displayed on the keyboard
        :param inherit_authorized_users: If the authorized users list should be inherited from the
        default value
        :param authorized_users: The authorized users list
        :param inbound_info: The inbound info to be added to the keyboard info
        :param from_deeplink: If the keyboard is being created from a deeplink
        :param is_deeplink: If the keyboard is a deeplink, generate the deeplink url
        :param only_authorized_users_can_interact: If only authorized users can interact with the
        keyboard
        :param switch_inline_query: The switch inline query
        :param exclude_key_from_inbound_info: The keys to be excluded from the inbound info
        """
        self.text = text
        self.info: dict = info if info is not None else {}
        self.screen: Screen = screen
        self.previous_screen_list: list[Screen] = (
            previous_screen_list if previous_screen_list is not None else []
        )
        self.url: str = url
        self.callback_data: str = self.create_callback_data()
        self.inherit_authorized_users: bool = inherit_authorized_users
        self.authorized_users: list[User] = (
            authorized_users if authorized_users is not None else []
        )
        self.from_deeplink: bool = from_deeplink
        self.is_deeplink: bool = is_deeplink
        self.only_authorized_users_can_interact: bool = only_authorized_users_can_interact
        self.switch_inline_query: str = switch_inline_query
        self.is_simulated: bool = False
        self.exclude_key_from_inbound_info: list[str] = (
            exclude_key_from_inbound_info if exclude_key_from_inbound_info is not None else []
        )
        self.inbound_info = inbound_info.copy() if inbound_info else {}

        if len(self.inbound_info) > 0:
            for key in self.exclude_key_from_inbound_info:
                self.inbound_info.pop(key, None)
            self.info = self.inbound_info | self.info
            self.refresh_callback_data()

        if self.is_deeplink:
            self.set_deeplink_url()

    def create_callback_data(self) -> str:
        """
        Creates the callback data for the keyboard
        :return: The callback data
        """

        # Create string data
        info_with_screen = self.info.copy()

        if self.screen is not None:
            info_with_screen[ReservedKeyboardKeys.SCREEN] = int(self.screen[1:])

        temp_screen_code: int = (
            info_with_screen[ReservedKeyboardKeys.SCREEN]
            if ReservedKeyboardKeys.SCREEN in info_with_screen
            else None
        )

        if self.previous_screen_list is not None and len(self.previous_screen_list) > 0:
            info_with_screen[ReservedKeyboardKeys.PREVIOUS_SCREEN] = [
                int(screen[1:])
                for screen in self.previous_screen_list
                if int(screen[1:]) != temp_screen_code
            ]

        # Convert boolean to int
        for key, value in info_with_screen.items():
            if isinstance(value, bool):
                info_with_screen[key] = int(value)

        return json.dumps(info_with_screen, separators=(",", ":"))

    def refresh_callback_data(self):
        """
        Refreshes the callback data of the keyboard
        """
        self.callback_data = self.create_callback_data()

    def set_and_get_callback_data_in_context(self, context: ContextTypes.DEFAULT_TYPE) -> str:
        """
        Get the callback data in the context if longer than allowed
        :param context: The context
        """

        if len(self.callback_data) < c.TG_KEYBOARD_DATA_MAX_LEN:
            return self.callback_data

        # Inner key is md5 hash of the callback data
        inner_key = hashlib.md5(self.callback_data.encode()).hexdigest()
        User.set_context_data(
            context, ContextDataKey.KEYBOARD_DATA, self.callback_data, inner_key=inner_key
        )
        logging.debug(f"Keyboard data too long, saved in context with inner key {inner_key}")
        return json.dumps({ReservedKeyboardKeys.CONTEXT: inner_key}, separators=(",", ":"))

    @staticmethod
    def get_from_callback_query_or_info(
        context: ContextTypes.DEFAULT_TYPE,
        message_source: MessageSource,
        callback_query: CallbackQuery = None,
        info_str: str = None,
        from_deeplink: bool = False,
    ) -> "Keyboard":
        """
        Create a Keyboard object from a CallbackQuery object
        :param context: The context
        :param callback_query: CallbackQuery object
        :param message_source: Source of the message
        :param info_str: The info to be added to the keyboard info
        :param from_deeplink: If the keyboard is being created from a deeplink
        :return: Keyboard object
        """

        if callback_query is None and info_str is None:
            raise ValueError("Either callback_query or info must be provided")

        if info_str is not None:
            info: dict = json.loads(info_str)
        else:
            info: dict = json.loads(callback_query.data)

        # Data was too long, so get it from context
        if ReservedKeyboardKeys.CONTEXT in info:
            info_str_from_context = User.get_context_data(
                context,
                ContextDataKey.KEYBOARD_DATA,
                inner_key=info[ReservedKeyboardKeys.CONTEXT],
            )
            # Remove the context data
            User.remove_context_data(
                context, ContextDataKey.KEYBOARD_DATA, info[ReservedKeyboardKeys.CONTEXT]
            )
            info = json.loads(info_str_from_context)

        try:
            if ReservedKeyboardKeys.SCREEN in info:
                screen = Screen(message_source + str(info[ReservedKeyboardKeys.SCREEN]))
            else:
                screen = None
        except (ValueError, KeyError):
            screen = Screen.UNKNOWN

        if ReservedKeyboardKeys.PREVIOUS_SCREEN in info:
            previous_screen_list = [
                Screen(message_source + str(screen))
                for screen in info[ReservedKeyboardKeys.PREVIOUS_SCREEN]
            ]
        else:
            previous_screen_list = []

        text: str = ""

        return Keyboard(
            text,
            info=info,
            screen=screen,
            previous_screen_list=previous_screen_list,
            from_deeplink=from_deeplink,
        )

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

    def set_deeplink_url(self):
        """
        Set the deeplink url for the keyboard
        """

        from src.service.message_service import get_deeplink

        self.url = get_deeplink(self.callback_data)

    def set_screen(self, screen: Screen):
        """
        Set the screen
        :param screen: The screen
        """

        self.screen = screen
        self.info[ReservedKeyboardKeys.SCREEN] = int(screen[1:])

    def has_key(self, key: str) -> bool:
        """
        Check if the keyboard info has a key
        :param key: The key
        :return: If the key exists
        """

        return key in self.info
