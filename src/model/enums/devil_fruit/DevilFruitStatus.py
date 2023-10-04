from enum import IntEnum


class DevilFruitStatus(IntEnum):
    """
    Enum for the status of a Devil Fruit
    """

    NEW = 1  # Just created
    COMPLETED = 2  # Abilities added
    ENABLED = 3  # Enabled in the system
    SCHEDULED = 4  # Scheduled to be released
    RELEASED = 5  # Released in the system
    COLLECTED = 6  # Collected by a user
    EATEN = 7  # Eaten by a user

    @staticmethod
    def get_released_statuses() -> list:
        """
        Get the statuses that are released
        :return: The statuses that are released
        """
        return [DevilFruitStatus.SCHEDULED, DevilFruitStatus.RELEASED, DevilFruitStatus.COLLECTED,
                DevilFruitStatus.EATEN]
