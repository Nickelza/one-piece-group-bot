def get_value_with_percentage(value: float, percentage: float) -> float:
    """
    Gets a value with a percentage added to it
    :param value: The value to add the percentage to
    :param percentage: The percentage to add
    :return: The value with the percentage added
    """
    return value + ((value * percentage) / 100)
