from datetime import datetime, timedelta

from peewee import JOIN
from telegram import Message
from telegram.error import TelegramError
from telegram.ext import ContextTypes

import resources.Environment as Env
from resources import phrases
from src.model.Group import Group
from src.model.GroupChat import GroupChat
from src.model.GroupChatDisabledFeature import GroupChatDisabledFeature
from src.model.GroupChatEnabledFeaturePin import GroupChatEnabledFeaturePin
from src.model.GroupChatFeaturePinMessage import GroupChatFeaturePinMessage
from src.model.enums.Feature import Feature
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


def is_main_group(group_chat: GroupChat) -> bool:
    """
    Checks if the update is from the main group_chat
    :param group_chat: The group chat
    :return: True if the message is from the main group_chat, False otherwise
    """

    group: Group = group_chat.group
    return int(group.tg_group_id) == Env.OPD_GROUP_ID.get_int()


def get_main_group() -> Group:
    """
    Gets the main group_chat
    :return: The main group_chat
    """

    return Group.get(Group.tg_group_id == str(Env.OPD_GROUP_ID.get_int()))


def feature_is_enabled(group_chat: GroupChat, feature: Feature) -> bool:
    """
    Checks if a feature is enabled
    :param group_chat: The group chat chat
    :param feature: The feature
    :return: True if the feature is enabled, False otherwise
    """

    return GroupChatDisabledFeature.get_or_none((GroupChatDisabledFeature.group_chat == group_chat) &
                                                (GroupChatDisabledFeature.feature == feature)) is None


def get_group_or_topic_text(group_chat: GroupChat) -> str:
    """
    Gets the group chat or group_chat text
    :param group_chat: The group chat
    :return: The group chat or group_chat text
    """

    if group_chat.tg_topic_id is not None:
        return phrases.TEXT_TOPIC
    else:
        return phrases.TEXT_GROUP


def allow_bounty_from_messages(group_chat: GroupChat) -> bool:
    """
    Checks if the group chat/group_chat allows bounty from messages
    :param group_chat: The group chat
    :return: True if the group chat/group_chat allows bounty from messages, False otherwise
    """

    if not is_main_group(group_chat):
        return False

    return feature_is_enabled(group_chat, Feature.BOUNTY_MESSAGES_GAIN)


def get_group_chats_with_feature_enabled(feature: Feature, filter_by_groups: list[Group] = None,
                                         excluded_group_chats: list[GroupChat] = None) -> list[GroupChat]:
    """
    Gets the group chats with a feature enabled
    :param feature: The feature
    :param filter_by_groups: The groups to filter by
    :param excluded_group_chats: The group chat chats to exclude from the result
    :return: The list of group chats with the feature enabled
    """

    if filter_by_groups is None:
        filter_by_groups = []

    if len(filter_by_groups) > 0:
        group_filter = GroupChat.group.in_(filter_by_groups)
    else:
        group_filter = True

    if excluded_group_chats is None:
        excluded_group_chats = []

    return (
        GroupChat.select().distinct()
        .join(GroupChatDisabledFeature, JOIN.LEFT_OUTER)
        .join(Group, on=(Group.id == GroupChat.group))
        .where((Group.is_active == True)
               & (GroupChat.is_active == True)
               & (GroupChat.id.not_in([egc.id for egc in excluded_group_chats]))
               & group_filter
               & ((GroupChatDisabledFeature.feature != feature) | (GroupChatDisabledFeature.feature.is_null()))))


async def broadcast_to_chats_with_feature_enabled_dispatch(context: ContextTypes.DEFAULT_TYPE, feature: Feature,
                                                           text: str, inline_keyboard: list[list[Keyboard]] = None,
                                                           excluded_group_chats: list[GroupChat] = None) -> None:
    """
    Broadcasts a message to all the chats with a feature enabled
    :param context: The context
    :param feature: The feature
    :param text: The message
    :param inline_keyboard: The outbound keyboard
    :param excluded_group_chats: The chats to exclude from the broadcast
    """

    context.application.create_task(broadcast_to_chats_with_feature_enabled(
        context, feature, text, inline_keyboard=inline_keyboard, excluded_group_chats=excluded_group_chats))


async def broadcast_to_chats_with_feature_enabled(context: ContextTypes.DEFAULT_TYPE, feature: Feature,
                                                  text: str, inline_keyboard: list[list[Keyboard]] = None,
                                                  excluded_group_chats: list[GroupChat] = None) -> None:
    """
    Broadcasts a message to all the chats with a feature enabled
    :param context: The context
    :param feature: The feature
    :param text: The message
    :param inline_keyboard: The outbound keyboard
    :param excluded_group_chats: The chats to exclude from the broadcast
    """

    """
    Broadcasts a message to all the chats with a feature enabled
    :param context: The context
    :param feature: The feature
    :param text: The message
    :param inline_keyboard: The outbound keyboard
    :param excluded_group_chats: The chats to exclude from the broadcast
    """

    group_chats: list[GroupChat] = get_group_chats_with_feature_enabled(feature,
                                                                        excluded_group_chats=excluded_group_chats)
    feature_is_pinnable = feature.is_pinnable()

    # Unpin all previous messages of this feature
    if feature_is_pinnable:
        # Get all messages to unpin to avoid unpinning messages that are just pinned due to async call
        messages_to_unpin: list[GroupChatFeaturePinMessage] = list(GroupChatFeaturePinMessage.select().where(
            GroupChatFeaturePinMessage.feature == feature))
        await unpin_feature_messages_dispatch(context, messages_to_unpin)

    for group_chat in group_chats:
        group_chat: GroupChat = group_chat
        try:
            message: Message = await full_message_send(context, text, keyboard=inline_keyboard, group_chat=group_chat)

            if feature_is_pinnable:
                should_pin = GroupChatEnabledFeaturePin.get_or_none(
                    (GroupChatEnabledFeaturePin.group_chat == group_chat) &
                    (GroupChatEnabledFeaturePin.feature == feature)) is not None

                if should_pin:
                    await message.pin(disable_notification=True)
                    pin_message: GroupChatFeaturePinMessage = GroupChatFeaturePinMessage()
                    pin_message.group_chat = group_chat
                    pin_message.feature = feature
                    pin_message.message = message
                    pin_message.save()

        except TelegramError as te:
            save_group_chat_error(group_chat, str(te))


async def unpin_feature_messages_dispatch(context: ContextTypes.DEFAULT_TYPE,
                                          messages_to_unpin: list[GroupChatFeaturePinMessage]) -> None:
    """
    Unpins the feature messages
    :param context: The context
    :param messages_to_unpin: The messages to unpin
    """

    context.application.create_task(unpin_feature_messages(context, messages_to_unpin))


async def unpin_feature_messages(context: ContextTypes.DEFAULT_TYPE,
                                 messages_to_unpin: list[GroupChatFeaturePinMessage]) -> None:
    """
    Unpins the feature messages
    :param context: The context
    :param messages_to_unpin: The messages to unpin
    """

    for pin_message in messages_to_unpin:
        group_chat: GroupChat = pin_message.group_chat
        group: Group = group_chat.group
        try:
            await context.bot.unpin_chat_message(group.tg_group_id, pin_message.message_id)
        except TelegramError as te:
            save_group_chat_error(group_chat, str(te))

        pin_message.delete_instance()


def deactivate_inactive_group_chats() -> None:
    """
    Deactivates the inactive groups and group chats
    """

    inactive_days = Env.INACTIVE_GROUP_DAYS.get_int()

    (Group.update(is_active=False)
     .where(Group.last_message_date < datetime.now() - timedelta(days=inactive_days))
     .execute())

    (GroupChat.update(is_active=False)
     .where(GroupChat.last_message_date < datetime.now() - timedelta(days=inactive_days))
     .execute())


def save_group_chat_error(group_chat: GroupChat, error: str) -> None:
    """
    Saves the error for the group chat
    :param group_chat: The group chat
    :param error: The error
    """

    group_chat.last_error_date = datetime.now()
    group_chat.last_error_message = error
    group_chat.save()

    group: Group = group_chat.group
    group.last_error_date = datetime.now()
    group.last_error_message = error
    group.save()
