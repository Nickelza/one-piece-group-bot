import resources.Environment as Env
from resources import phrases
from src.model.Group import Group
from src.model.GroupDisableFeature import GroupDisabledFeature
from src.model.Topic import Topic
from src.model.TopicDisableFeature import TopicDisabledFeature
from src.model.enums.Feature import Feature


def is_main_group(group: Group) -> bool:
    """
    Checks if the update is from the main group
    :param group: The group
    :return: True if the message is from the main group, False otherwise
    """

    return int(group.tg_group_id) == Env.OPD_GROUP_ID.get_int()


def feature_is_enabled(group: Group, topic: Topic, feature: Feature) -> bool:
    """
    Checks if a feature is enabled
    :param group: The group
    :param topic: The topic
    :param feature: The feature
    :return: True if the feature is enabled, False otherwise
    """

    if topic is not None:
        return TopicDisabledFeature.get_or_none((TopicDisabledFeature.topic == topic) &
                                                (TopicDisabledFeature.feature == feature)) is None
    else:
        return GroupDisabledFeature.get_or_none((GroupDisabledFeature.group == group) &
                                                (GroupDisabledFeature.feature == feature)) is None


def get_group_or_topic_text(topic: Topic) -> str:
    """
    Gets the group or topic text
    :param topic: The topic
    :return: The group or topic text
    """

    if topic is not None:
        return phrases.TEXT_TOPIC
    else:
        return phrases.TEXT_GROUP


def get_message_url(group: Group, topic: Topic, message_id: int) -> str:
    """
    Gets the message url
    :param group: The group
    :param topic: The topic
    :param message_id: The message id
    :return: The message url
    """

    tg_group_id = str(group.tg_group_id).replace('-100', '')
    if topic is not None:
        return f"https://t.me/c/{tg_group_id}/{topic.tg_topic_id}/{message_id}"
    else:
        return f"https://t.me/c/{tg_group_id}/{message_id}"


def allow_bounty_from_messages(group: Group, topic: Topic) -> bool:
    """
    Checks if the group/topic allows bounty from messages
    :param group: The group
    :param topic: The topic
    :return: True if the group/topic allows bounty from messages, False otherwise
    """

    if not is_main_group(group):
        return False

    return feature_is_enabled(group, topic, Feature.BOUNTY_MESSAGES_GAIN)
