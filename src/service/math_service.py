import random


def get_value_from_percentage(value: float, percentage: float) -> float:
    """
    Gets a value from a percentage
    :param value: The value to get the percentage from
    :param percentage: The percentage to get the value from
    :return: The value from the percentage
    """

    return (value * percentage) / 100


def get_random_win(percentage: float) -> bool:
    """
    Gets a random win based on the percentage
    :param percentage: The percentage to get a win for
    :return: True if the percentage is greater than a random number, False otherwise
    """
    return percentage >= random.randint(1, 100)
