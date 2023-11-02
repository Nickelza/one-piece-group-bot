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
    return percentage * 10000 >= random.randint(0, 1000000)


def get_random_int(min_value: int, max_value: int) -> int:
    """
    Gets a random int between the min and max values
    :param min_value: The minimum value
    :param max_value: The maximum value
    :return: The random int
    """

    return random.randint(min_value, max_value)


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


def get_cumulative_percentage_sum(percentages: list[float]) -> float:
    """
    Calculate the cumulative sum of percentages.

    This function takes a list of percentages and calculates the cumulative sum by iteratively adding each percentage to
    the result and adjusting the remaining percentage for subsequent iterations.

    :param percentages: A list of percentages to sum.
    :return: The cumulative sum of the percentages.
    """
    result = 0
    remaining_percentage = 100

    for percentage in percentages:
        # Calculate the percentage of the remaining percentage
        percentage_of_remaining_percentage = (remaining_percentage * percentage) / 100
        result += percentage_of_remaining_percentage
        remaining_percentage -= percentage_of_remaining_percentage

    return result


def format_percentage_value(percentage: float, decimals: int = 2) -> int | float:
    """
    Convert a percentage to an integer value or a float value with specified decimals.

    :param percentage: The percentage to convert.
    :param decimals: Number of decimal places (default is 2).
    :return: An integer or float value.
    """

    if percentage % 1 == 0:
        return int(percentage)

    return round(percentage, decimals)
