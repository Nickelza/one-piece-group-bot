import random


def get_value_from_percentage(total: float, percentage: float) -> float:
    """
    Gets a value from a percentage
    :param total: The value to get the percentage from
    :param percentage: The percentage to get the value from
    :return: The value from the percentage
    """

    return (total * percentage) / 100


def get_random_win(percentage: float) -> bool:
    """
    Gets a random win based on the percentage
    :param percentage: The percentage to get a win for
    :return: True if the percentage is greater than a random number, False otherwise
    """
    return percentage >= random.randint(1, 100)


def get_percentage_from_value(value: float, total: float, add_decimal=True) -> float:
    """
    Gets a percentage from a value
    :param value: The value to get the percentage from
    :param total: The total value
    :param add_decimal: True if the percentage should have a decimals, False otherwise
    :return: The percentage from the value
    """

    try:
        result = (value / total) * 100
        if not add_decimal:
            return int(result)

        return result
    except ZeroDivisionError:
        return 0


def add_percentage_to_value(value: float, percentage: float) -> float:
    """
    Adds a percentage to a value
    :param value: The value to add the percentage to
    :param percentage: The percentage to add to the value
    :return: The value with the percentage added
    """

    if percentage is None or percentage == 0:
        return value

    return value + get_value_from_percentage(value, percentage)


def subtract_percentage_from_value(value: float, percentage: float) -> float:
    """
    Subtracts a percentage from a value
    :param value: The value to subtract the percentage from
    :param percentage: The percentage to subtract from the value
    :return: The value with the percentage subtracted
    """

    return value - get_value_from_percentage(value, percentage)
