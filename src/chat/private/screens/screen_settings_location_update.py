from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
from src.model.User import User
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send
from src.service.settings_service import get_current_setting_text, get_toggle_keyboard


def manage(update: Update, context: CallbackContext, user: User, inbound_keyboard: Keyboard) -> None:
    """
    Manage the location update settings screen
    :param update: The update
    :param context: The context
    :param user: The user
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    # Toggle
    if 'a' in inbound_keyboard.info:
        user.should_send_location_update = inbound_keyboard.info['a']
        user.save()

    ot_text = get_current_setting_text(user.should_send_location_update, phrases.PVT_TXT_SETTINGS_LOCATION_UPDATE)
    inline_keyboard: list[list[Keyboard]] = [[get_toggle_keyboard(user.should_send_location_update,
                                                                  inbound_keyboard.screen)]]
    full_message_send(context, ot_text, update=update, keyboard=inline_keyboard,
                      inbound_keyboard=inbound_keyboard)
