import datetime

from apscheduler.triggers.cron import CronTrigger


def get_next_run(cron_expression: str, start_datetime: datetime = None) -> datetime:
    """
    Get the next run time
    :param cron_expression: The cron expression
    :param start_datetime: The start datetime. If None, the current datetime is used
    :return: The next run time
    """

    if start_datetime is None:
        start_datetime = datetime.datetime.now()

    cron_trigger = CronTrigger.from_crontab(cron_expression)
    return cron_trigger.get_next_fire_time(None, start_datetime)


def convert_seconds_to_time(seconds: int) -> str:
    """
    Converts seconds to days, hours, minutes, seconds
    :param seconds: Seconds to convert
    :return: Days, hours e.g. 1 day 2h hours
    """
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)

    result = ''
    if days > 0:
        if days == 1:
            result += f'{days} day '
        else:
            result += f'{days} days '

    if hours > 0:
        result += f'{hours} hours'

    return result


def cron_datetime_difference(cron_expression: str, start_datetime: datetime = None) -> str:
    """
    Get the difference between the next run time and the current datetime
    :param cron_expression: The cron expression
    :param start_datetime: The start datetime. If None, the current datetime is used
    :return: The difference in days and hours e.g. 1 day 2h hours
    """

    if start_datetime is None:
        start_datetime = datetime.datetime.now(datetime.timezone.utc)

    next_run = get_next_run(cron_expression, start_datetime)
    return convert_seconds_to_time((next_run - start_datetime).total_seconds())