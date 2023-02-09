from enum import IntEnum


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

    def get_description(self) -> str:
        """
        Get the description of the feature

        :return: The description of the feature
        """

        return FEATURE_DESCRIPTION_MAP[self]

    @staticmethod
    def get_all() -> list['Feature']:
        """
        Get all the features

        :return: All the features
        """
        return [Feature.BOUNTY_GIFT,
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
                Feature.STATUS]

    @staticmethod
    def get_restricted() -> list['Feature']:
        """
        Get all the features that are restricted to the main group_chat

        :return: All the features that are restricted
        """
        return [Feature.BOUNTY_MESSAGES_GAIN, Feature.MESSAGE_FILTER, Feature.SILENCE]

    @staticmethod
    def get_non_restricted() -> list['Feature']:
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


FEATURE_DESCRIPTION_MAP = {
    Feature.BOUNTY_GIFT: "Bounty Gift",
    Feature.BOUNTY_MESSAGES_GAIN: "Bounty Messages Gain",
    Feature.CHALLENGE: "Challenge",
    Feature.CREW: "Crew",
    Feature.DEVIL_FRUIT_APPEARANCE: "Devil Fruit Appearance",
    Feature.DOC_Q: "Doc Q",
    Feature.FIGHT: "Fight",
    Feature.LEADERBOARD: "Leaderboard",
    Feature.MESSAGE_FILTER: "Message Filter",
    Feature.PREDICTION: "Prediction",
    Feature.SILENCE: "Silence",
    Feature.STATUS: "Status"
}
