from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import constants as c
import resources.phrases as phrases
from src.model.GroupChat import GroupChat
from src.model.GroupChatDisabledFeature import GroupChatDisabledFeature
from src.model.enums.Emoji import Emoji
from src.model.enums.Feature import Feature
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.group_service import is_main_group, get_group_or_topic_text
from src.service.message_service import full_message_send


class SettingsReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    FEATURE = 'a'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, group_chat: GroupChat,
                 added_to_group: bool = False) -> None:
    """
    Manage the settings screen
    :param update: The update object
    :param context: The context object
    :param inbound_keyboard: The inbound keyboard
    :param group_chat: The group chat
    :param added_to_group: If the Bot was just added to the group chat
    :return: None
    """

    if inbound_keyboard is not None:
        feature: Feature = Feature(inbound_keyboard.info[SettingsReservedKeys.FEATURE])
        if inbound_keyboard.info[ReservedKeyboardKeys.TOGGLE]:
            #  Enable feature - Remove from disabled features
            GroupChatDisabledFeature.delete().where((GroupChatDisabledFeature.group_chat == group_chat) &
                                                    (GroupChatDisabledFeature.feature == feature)).execute()
        else:
            # Disable feature - Add to disabled features
            disabled_feature = GroupChatDisabledFeature()
            disabled_feature.group_chat = group_chat
            disabled_feature.feature = feature
            disabled_feature.save()

        # Refresh backlinks
        group_chat = GroupChat.get_by_id(group_chat.id)

    outbound_keyboard = get_settings_keyboard(group_chat)

    thanks_text = phrases.THANKS_FOR_ADDING_TO_GROUP if added_to_group else ''
    ot_text = phrases.GRP_TXT_SETTINGS.format(thanks_text, get_group_or_topic_text(group_chat))

    await full_message_send(context, ot_text, update=update, keyboard=outbound_keyboard, add_delete_button=True,
                            use_close_delete=True)


def get_settings_keyboard(group_chat: GroupChat) -> list[list[Keyboard]]:
    """
    Get the settings keyboard
    :param group_chat: The group chat
    :return: The settings keyboard
    """

    # Get all features
    if is_main_group(group_chat):
        features: list[Feature] = Feature.get_all()
    else:
        features: list[Feature] = Feature.get_non_restricted()

    # Get all disabled features, avoids multiple queries
    disabled_features: list[Feature] = [disabled_feature.feature for disabled_feature in group_chat.disabled_features]

    keyboard: list[list[Keyboard]] = [[]]
    keyboard_row: list[Keyboard] = []

    for feature in features:
        is_enabled = feature not in disabled_features
        emoji = Emoji.ENABLED if is_enabled else Emoji.DISABLED_EMPTY
        button_info: dict = {SettingsReservedKeys.FEATURE: feature.value, ReservedKeyboardKeys.TOGGLE: not is_enabled}
        button: Keyboard = Keyboard(f'{emoji.value} {feature.get_description()}', info=button_info,
                                    screen=Screen.GRP_SETTINGS)
        keyboard_row.append(button)

        if len(keyboard_row) == c.FEATURE_KEYBOARD_ROW_SIZE:
            keyboard.append(keyboard_row)
            keyboard_row = []

    if len(keyboard_row) > 0:
        keyboard.append(keyboard_row)

    return keyboard
