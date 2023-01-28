from peewee import JOIN

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


def get_main_group() -> Group:
    """
    Gets the main group
    :return: The main group
    """

    return Group.get(Group.tg_group_id == str(Env.OPD_GROUP_ID.get_int()))


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


def get_topics_with_feature_enabled(feature: Feature, group: Group = None) -> list:
    """
    Gets the topics with a feature enabled
    :param feature: The feature
    :param group: The group to filter by (optional)
    :return: The list of topics
    """

    if group is None:
        return (
            Topic.select().distinct()
            .join(TopicDisabledFeature, JOIN.LEFT_OUTER)
            .join(Group, on=(Group.id == Topic.group))
            .where(((Group.is_active == True) & (Group.is_forum == True))
                   & ((TopicDisabledFeature.feature != feature) | (TopicDisabledFeature.feature.is_null()))))
    else:
        return (
            Topic.select().distinct()
            .join(TopicDisabledFeature, JOIN.LEFT_OUTER)
            .join(Group, on=(Group.id == Topic.group))
            .where((Topic.group == group)
                   & ((TopicDisabledFeature.feature != feature) | (TopicDisabledFeature.feature.is_null()))))


def get_groups_with_feature_enabled(feature: Feature) -> list:
    """
    Gets the groups with a feature enabled, if they are not topics
    :param feature: The feature
    :return: The list of groups
    """

    return (
        Group.select().distinct()
        .join(GroupDisabledFeature, JOIN.LEFT_OUTER)
        .where((Group.is_active == True)  # Not filtering by is_forum to include general forum
               & ((GroupDisabledFeature.feature != feature) | (GroupDisabledFeature.feature.is_null()))))


def get_chats_with_feature_enabled_dict(feature: Feature) -> list[dict[str, Group or Topic]]:
    """
    Gets the chats with a feature enabled, if they are not topics
    :param feature: The feature
    :return: The dict of chats
    """

    groups = get_groups_with_feature_enabled(feature)
    topics = get_topics_with_feature_enabled(feature)

    result = []
    for group in groups:
        result.append({"group": group, "topic": None})

    for topic in topics:
        result.append({"group": topic.group, "topic": topic})

    return result
