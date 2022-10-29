from datetime import datetime

import constants as c


def default_datetime_format(date_time: datetime) -> str:
    """
    Default datetime format
    :param date_time: The datetime
    :return: The formatted datetime
    """
    return date_time.strftime(c.STANDARD_DATE_TIME_FORMAT)
