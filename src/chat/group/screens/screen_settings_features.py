from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import constants as c
import resources.phrases as phrases
from src.model.GroupChat import GroupChat
from src.model.GroupChatDisabledFeature import GroupChatDisabledFeature
from src.model.GroupChatEnabledFeaturePin import GroupChatEnabledFeaturePin
from src.model.enums.Emoji import Emoji
from src.model.enums.Feature import Feature
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.group_service import is_main_group, get_group_or_topic_text
from src.service.message_service import full_message_send


class FeaturesReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    FEATURE = "a"
    PIN_TOGGLE = "b"


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
    group_chat: GroupChat,
    added_to_group: bool = False,
) -> None:
    """
    Manage the features screen
    :param update: The update object
    :param context: The context object
    :param inbound_keyboard: The inbound keyboard
    :param group_chat: The group chat
    :param added_to_group: If the Bot was just added to the group chat
    :return: None
    """

    if inbound_keyboard is not None and FeaturesReservedKeys.FEATURE in inbound_keyboard.info:
        feature: Feature = Feature(inbound_keyboard.info[FeaturesReservedKeys.FEATURE])

        # Pin toggle
        if FeaturesReservedKeys.PIN_TOGGLE in inbound_keyboard.info:
            # Pin toggle
            if inbound_keyboard.info[FeaturesReservedKeys.PIN_TOGGLE]:
                # Pin feature
                feature_pin = GroupChatEnabledFeaturePin()
                feature_pin.group_chat = group_chat
                feature_pin.feature = feature
                feature_pin.save()
            else:
                # Unpin feature
                GroupChatEnabledFeaturePin.delete().where(
                    (GroupChatEnabledFeaturePin.group_chat == group_chat)
                    & (GroupChatEnabledFeaturePin.feature == feature)
                ).execute()
        else:
            if inbound_keyboard.info[ReservedKeyboardKeys.TOGGLE]:
                #  Enable feature - Remove from disabled features
                GroupChatDisabledFeature.delete().where(
                    (GroupChatDisabledFeature.group_chat == group_chat)
                    & (GroupChatDisabledFeature.feature == feature)
                ).execute()
            else:
                # Disable feature - Add to disabled features
                disabled_feature = GroupChatDisabledFeature()
                disabled_feature.group_chat = group_chat
                disabled_feature.feature = feature
                disabled_feature.save()

                # Delete the feature pin
                GroupChatEnabledFeaturePin.delete().where(
                    (GroupChatEnabledFeaturePin.group_chat == group_chat)
                    & (GroupChatEnabledFeaturePin.feature == feature)
                ).execute()

        # Refresh backlinks
        group_chat = GroupChat.get_by_id(group_chat.id)

    outbound_keyboard = get_features_keyboard(group_chat)

    thanks_text = phrases.THANKS_FOR_ADDING_TO_GROUP if added_to_group else ""
    ot_text = phrases.GRP_TXT_FEATURES.format(thanks_text, get_group_or_topic_text(group_chat))

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=outbound_keyboard,
        add_delete_button=True,
        use_close_delete=True,
        inbound_keyboard=inbound_keyboard,
        should_auto_delete=False,
    )


def get_features_keyboard(group_chat: GroupChat) -> list[list[Keyboard]]:
    """
    Get the feature keyboard
    :param group_chat: The group chat
    :return: The feature keyboard
    """

    # Get all features
    if is_main_group(group_chat):
        features: list[Feature] = Feature.get_all()
    else:
        features: list[Feature] = Feature.get_non_restricted()

    # Order alphabetically
    features.sort(key=lambda x: x.get_description())

    # Move pinnable features to the end
    pinnable_features = Feature.get_pinnable()
    for pinnable_feature in pinnable_features:
        features.remove(pinnable_feature)
        features.append(pinnable_feature)

    # Get all disabled features, avoids multiple queries, Backref
    disabled_features: list[Feature] = [
        disabled_feature.feature for disabled_feature in group_chat.disabled_features
    ]

    keyboard: list[list[Keyboard]] = [[]]
    keyboard_row: list[Keyboard] = []

    for feature in features:
        is_enabled_feature = feature not in disabled_features
        emoji = Emoji.ENABLED if is_enabled_feature else Emoji.DISABLED_EMPTY
        button_info: dict = {
            FeaturesReservedKeys.FEATURE: feature.value,
            ReservedKeyboardKeys.TOGGLE: not is_enabled_feature,
        }
        button: Keyboard = Keyboard(
            f"{emoji} {feature.get_description()}",
            info=button_info,
            screen=Screen.GRP_SETTINGS_FEATURES,
        )

        # If feature is pinnable, add button in a new row with the pin toggle button
        if feature.is_pinnable() and is_enabled_feature:
            # Backref
            is_enabled_pin = feature in [
                enabled_feature.feature for enabled_feature in group_chat.enabled_features_pin
            ]
            is_enabled_emoji = Emoji.RADIO_BUTTON if is_enabled_pin else ""
            pin_button_info = {
                FeaturesReservedKeys.FEATURE: feature.value,
                FeaturesReservedKeys.PIN_TOGGLE: not is_enabled_pin,
            }
            pin_toggle: Keyboard = Keyboard(
                f"{is_enabled_emoji} {Emoji.PIN}",
                info=pin_button_info,
                screen=Screen.GRP_SETTINGS_FEATURES,
            )

            # Relative feature button and pin button in the same new row
            if len(keyboard_row) > 0:
                keyboard.append(keyboard_row)
                keyboard_row = []

            keyboard_row.append(button)
            keyboard_row.append(pin_toggle)
        else:
            keyboard_row.append(button)

        if len(keyboard_row) == c.FEATURE_KEYBOARD_ROW_SIZE:
            keyboard.append(keyboard_row)
            keyboard_row = []

    if len(keyboard_row) > 0:
        keyboard.append(keyboard_row)

    return keyboard
