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
    PREDICTION = 9

    def get_description(self) -> str:
        """
        Get the description of the feature

        :return: The description of the feature
        """

        return FEATURE_DESCRIPTION_MAP[self]

    @staticmethod
    def get_all_description() -> list[str]:
        """
        Get all the descriptions of the features

        :return: All the descriptions of the features
        """
        return [Feature.BOUNTY_GIFT.get_description(),
                Feature.BOUNTY_MESSAGES_GAIN.get_description(),
                Feature.CHALLENGE.get_description(),
                Feature.CREW.get_description(),
                Feature.DEVIL_FRUIT_APPEARANCE.get_description(),
                Feature.DOC_Q.get_description(),
                Feature.FIGHT.get_description(),
                Feature.LEADERBOARD.get_description(),
                Feature.PREDICTION.get_description()]

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
                Feature.PREDICTION]

    @staticmethod
    def get_non_restricted() -> list['Feature']:
        """
        Get all the features that are not restricted to the main group

        :return: All the features that are not restricted
        """
        return [Feature.BOUNTY_GIFT,
                Feature.CHALLENGE,
                Feature.CREW,
                Feature.DOC_Q,
                Feature.FIGHT,
                Feature.LEADERBOARD,
                Feature.PREDICTION]


FEATURE_DESCRIPTION_MAP = {
    Feature.BOUNTY_GIFT: "Bounty Gift",
    Feature.BOUNTY_MESSAGES_GAIN: "Bounty Messages Gain",
    Feature.CHALLENGE: "Challenge",
    Feature.CREW: "Crew",
    Feature.DEVIL_FRUIT_APPEARANCE: "Devil Fruit Appearance",
    Feature.DOC_Q: "Doc Q",
    Feature.FIGHT: "Fight",
    Feature.LEADERBOARD: "Leaderboard",
    Feature.PREDICTION: "Prediction"
}
