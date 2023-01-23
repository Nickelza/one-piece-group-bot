from enum import IntEnum


class DevilFruitStatus(IntEnum):
    """
    Enum for the status of a Devil Fruit
    """

    NEW = 1  # Just created
    COMPLETED = 2  # Abilities added
    ENABLED = 3  # Enabled in the system
    ENQUEUED = 4  # Enqueued for sending
    RELEASED = 5  # Released in the system
    COLLECTED = 6  # Collected by a user
    EATEN = 7  # Eaten by a user
