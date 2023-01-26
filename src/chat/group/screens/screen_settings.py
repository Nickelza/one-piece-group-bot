from strenum import StrEnum
from telegram import Update
from telegram.ext import ContextTypes

import constants as c
import resources.phrases as phrases
from src.model.Group import Group
from src.model.GroupDisableFeature import GroupDisabledFeature
from src.model.Topic import Topic
from src.model.TopicDisableFeature import TopicDisabledFeature
from src.model.enums.Emoji import Emoji
from src.model.enums.Feature import Feature
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.group_service import is_main_group
from src.service.message_service import full_message_send


class SettingsReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    FEATURE = 'a'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, group: Group,
                 topic: Topic, added_to_group: bool = False) -> None:
    """
    Manage the settings screen
    :param update: The update object
    :param context: The context object
    :param inbound_keyboard: The inbound keyboard
    :param group: The group
    :param topic: The topic
    :param added_to_group: If the Bot was just added to the group
    :return: None
    """

    is_topic = topic is not None

    if inbound_keyboard is not None:
        feature: Feature = Feature(inbound_keyboard.info[SettingsReservedKeys.FEATURE])
        if inbound_keyboard.info[ReservedKeyboardKeys.TOGGLE]:
            #  Enable feature - Remove from disabled features
            if is_topic:
                TopicDisabledFeature.delete().where((TopicDisabledFeature.topic == topic) &
                                                    (TopicDisabledFeature.feature == feature)).execute()
            else:
                GroupDisabledFeature.delete().where((GroupDisabledFeature.group == group) &
                                                    (GroupDisabledFeature.feature == feature)).execute()
        else:
            # Disable feature - Add to disabled features
            if is_topic:
                disabled_feature = TopicDisabledFeature()
                disabled_feature.topic = topic
                disabled_feature.feature = feature
                disabled_feature.save()
            else:
                disabled_feature = GroupDisabledFeature()
                disabled_feature.group = group
                disabled_feature.feature = feature
                disabled_feature.save()

        # Refresh backlinks
        if is_topic:
            topic = Topic.get_by_id(topic.id)
        else:
            group = Group.get_by_id(group.id)

    outbound_keyboard = get_settings_keyboard(update, group, topic, is_topic)

    thanks_text = phrases.THANKS_FOR_ADDING_TO_GROUP if added_to_group else ''
    chat_type_text = phrases.TEXT_GROUP if not is_topic else phrases.TEXT_TOPIC
    ot_text = phrases.GRP_TXT_SETTINGS.format(thanks_text, chat_type_text)

    await full_message_send(context, ot_text, update=update, keyboard=outbound_keyboard, add_delete_button=True,
                            use_close_delete=True)


def get_settings_keyboard(update: Update, group: Group, topic: Topic, is_topic: bool) -> list[list[Keyboard]]:
    """
    Get the settings keyboard
    :param update: The update object
    :param group: The group
    :param topic: The topic
    :param is_topic: Whether the settings are for a topic
    :return: The settings keyboard
    """

    # Get all features
    if is_main_group(update):
        features: list[Feature] = Feature.get_all()
    else:
        features: list[Feature] = Feature.get_non_restricted()

    # Get all disabled features, avoids multiple queries
    if is_topic:
        disabled_features: list[Feature] = [disabled_feature.feature for disabled_feature in topic.disabled_features]
    else:
        disabled_features: list[Feature] = [disabled_feature.feature for disabled_feature in group.disabled_features]

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
