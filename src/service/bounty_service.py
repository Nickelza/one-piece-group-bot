def get_bounty_formatted(bounty: int) -> str:
    """
    Returns a formatted string of the bounty
    :param bounty: The bounty to format e.g. 1000000
    :return: The formatted string e.g. 1,000,000
    """

    return '{0:,}'.format(bounty)
