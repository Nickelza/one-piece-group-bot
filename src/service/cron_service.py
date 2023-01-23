import datetime

from apscheduler.triggers.cron import CronTrigger


def get_next_run(cron_expression: str, start_datetime: datetime = None, previous_fire_time: datetime = None
                 ) -> datetime:
    """
    Get the next run time
    :param cron_expression: The cron expression
    :param start_datetime: The start datetime. If None, the current datetime is used
    :param previous_fire_time: The previous fire time
    :return: The next run time
    """

    if start_datetime is None:
        start_datetime = datetime.datetime.now(datetime.timezone.utc)

    cron_trigger = CronTrigger.from_crontab(cron_expression)
    return cron_trigger.get_next_fire_time(previous_fire_time, start_datetime)


def convert_seconds_to_time(seconds: int) -> str:
    """
    Converts seconds to days, hours, minutes, seconds
    :param seconds: Seconds to convert
    :return: Days, hours e.g. 1 day 2 hours 5 minutes
    """
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)

    result = ''
    if days > 0:
        if days == 1:
            result += f'{days} day'
        else:
            result += f'{days} days'

    if hours > 0:
        if len(result) > 0:
            result += ' '
        if hours == 1:
            result += f'{hours} hour'
        else:
            result += f'{hours} hours'

    if hours <= 1:  # Show minutes only in last hour
        if len(result) > 0:
            result += ' '
        if minutes > 0:
            if minutes == 1:
                result += f'{minutes} minute'
            else:
                result += f'{minutes} minutes'

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


def get_remaining_time(end_datetime: datetime) -> str:
    """
    Get the remaining time until the end_datetime
    :param end_datetime: The end datetime
    :return: The remaining time in days and hours e.g. 1 day 2h hours
    """
    # Remove offset awareness from end_datetime
    end_datetime = end_datetime.replace(tzinfo=None)
    return convert_seconds_to_time((end_datetime - datetime.datetime.now()).total_seconds())


def get_remaining_time_from_next_cron(cron_expression: str, start_datetime: datetime = None) -> str:
    """
    Get the remaining time until the next cron run
    :param cron_expression: The cron expression
    :param start_datetime: The start datetime. If None, the current datetime is used
    :return: The remaining time in days and hours e.g. 1 day 2h hours
    """
    if start_datetime is None:
        start_datetime = datetime.datetime.now(datetime.timezone.utc)

    next_run = get_next_run(cron_expression, start_datetime)
    return get_remaining_time(next_run)


def get_datetime_in_future_days(days: int) -> datetime:
    """
    Get the datetime in the future
    :param days: The number of days in the future
    :return: The datetime in the future
    """

    return datetime.datetime.now() + datetime.timedelta(days=days)
