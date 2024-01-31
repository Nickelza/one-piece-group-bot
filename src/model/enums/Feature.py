from enum import IntEnum

from resources import phrases


class Feature(IntEnum):
    BOUNTY_GIFT = 1
    BOUNTY_MESSAGES_GAIN = 2
    CHALLENGE = 3
    CREW = 4
    DEVIL_FRUIT_APPEARANCE = 5
    DOC_Q = 6
    FIGHT = 7
    LEADERBOARD = 8
    MESSAGE_FILTER = 9
    PREDICTION = 10
    SILENCE = 11
    STATUS = 12
    DEVIL_FRUIT_SELL = 13
    BOUNTY_LOAN = 14
    PLUNDER = 15

    def get_description(self) -> str:
        """
        Get the description of the feature

        :return: The description of the feature
        """

        return FEATURE_DESCRIPTION_MAP[self]

    @staticmethod
    def get_all() -> list["Feature"]:
        """
        Get all the features

        :return: All the features
        """
        return [
            Feature.BOUNTY_GIFT,
            Feature.BOUNTY_MESSAGES_GAIN,
            Feature.CHALLENGE,
            Feature.CREW,
            Feature.DEVIL_FRUIT_APPEARANCE,
            Feature.DOC_Q,
            Feature.FIGHT,
            Feature.LEADERBOARD,
            Feature.MESSAGE_FILTER,
            Feature.PREDICTION,
            Feature.SILENCE,
            Feature.STATUS,
            Feature.DEVIL_FRUIT_SELL,
            Feature.BOUNTY_LOAN,
            Feature.PLUNDER,
        ]

    @staticmethod
    def get_restricted() -> list["Feature"]:
        """
        Get all the features that are restricted to the main group_chat

        :return: All the features that are restricted
        """
        return [Feature.BOUNTY_MESSAGES_GAIN, Feature.MESSAGE_FILTER, Feature.SILENCE]

    @staticmethod
    def get_non_restricted() -> list["Feature"]:
        """
        Get all the features that are not restricted to the main group_chat

        :return: All the features that are not restricted
        """

        return list(set(Feature.get_all()) - set(Feature.get_restricted()))

    def is_restricted(self) -> bool:
        """
        Checks if the feature is restricted to the main group_chat

        :return: True if the feature is restricted, False otherwise
        """

        return self in Feature.get_restricted()

    @staticmethod
    def get_pinnable() -> list["Feature"]:
        """
        Get all the features that can be pinned

        :return: All the features that can be pinned
        """

        return [Feature.LEADERBOARD, Feature.PREDICTION]

    def is_pinnable(self) -> bool:
        """
        Checks if the feature can be pinned

        :return: True if the feature can be pinned, False otherwise
        """

        return self in Feature.get_pinnable()


FEATURE_DESCRIPTION_MAP = {
    Feature.BOUNTY_GIFT: phrases.FEATURE_BOUNTY_GIFT,
    Feature.BOUNTY_MESSAGES_GAIN: phrases.FEATURE_BOUNTY_MESSAGES_GAIN,
    Feature.CHALLENGE: phrases.FEATURE_CHALLENGE,
    Feature.CREW: phrases.FEATURE_CREW,
    Feature.DEVIL_FRUIT_APPEARANCE: phrases.FEATURE_DEVIL_FRUIT_APPEARANCE,
    Feature.DOC_Q: phrases.FEATURE_DOC_Q,
    Feature.FIGHT: phrases.FEATURE_FIGHT,
    Feature.LEADERBOARD: phrases.FEATURE_LEADERBOARD,
    Feature.MESSAGE_FILTER: phrases.FEATURE_MESSAGE_FILTER,
    Feature.PREDICTION: phrases.FEATURE_PREDICTION,
    Feature.SILENCE: phrases.FEATURE_SILENCE,
    Feature.STATUS: phrases.FEATURE_STATUS,
    Feature.DEVIL_FRUIT_SELL: phrases.FEATURE_DEVIL_FRUIT_SELL,
    Feature.BOUNTY_LOAN: phrases.FEATURE_BOUNTY_LOAN,
    Feature.PLUNDER: phrases.FEATURE_PLUNDER,
}
