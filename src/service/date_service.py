import datetime
import random

import pytz
from apscheduler.triggers.cron import CronTrigger
from geopy.geocoders import Nominatim
from telegram import Update
from telegram.ext import ContextTypes
from timezonefinder import TimezoneFinder

import constants as c
import resources.Environment as Env
from resources import phrases
from src.model.User import User
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send
from src.service.string_service import get_unit_value_from_string


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
    weeks = int(seconds // 604800)
    days = int((seconds % 604800) // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)

    result = ''
    if weeks > 0:
        if weeks == 1:
            result += f'{weeks} week'
        else:
            result += f'{weeks} weeks'

    # Show days only in last week
    if days > 0 and weeks == 0:
        if days == 1:
            result += f'{days} day'
        else:
            result += f'{days} days'

    # Show hours only in last day
    if hours > 0 and days == 0 and weeks == 0:
        if len(result) > 0:
            result += ' '
        if hours == 1:
            result += f'{hours} hour'
        else:
            result += f'{hours} hours'

    # Show minutes only in last hour
    if minutes > 0 and hours == 0 and days == 0 and weeks == 0:
        if len(result) > 0:
            result += ' '
        if minutes > 0 and seconds > 60:
            if minutes == 1:
                result += f'{minutes} minute'
            else:
                result += f'{minutes} minutes'

    # Show seconds only in last minute
    if seconds > 0 and minutes <= 1 and hours == 0 and days == 0 and weeks == 0:
        if len(result) > 0:
            result += ' '
        if seconds > 0:
            if seconds == 1:
                result += f'{seconds} second'
            else:
                result += f'{seconds} seconds'

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


def get_remaining_time_in_seconds(end_datetime: datetime, start_datetime: datetime = None) -> int:
    """
    Get the remaining time in seconds until the end_datetime
    :param end_datetime: The end datetime
    :param start_datetime: The start datetime. If None, the current datetime is used
    :return: The remaining time in seconds
    """
    # Remove offset awareness from end_datetime
    end_datetime = end_datetime.replace(tzinfo=None)
    if start_datetime is None:
        start_datetime = datetime.datetime.now(datetime.timezone.utc)
    start_datetime = start_datetime.replace(tzinfo=None)

    # If the end_datetime is in the past, return 0
    if end_datetime < start_datetime:
        return 0

    return int((end_datetime - start_datetime).total_seconds())


def get_remaining_time_in_minutes(end_datetime: datetime, start_datetime: datetime = None) -> int:
    """
    Get the remaining time in minutes until the end_datetime
    :param end_datetime: The end datetime
    :param start_datetime: The start datetime. If None, the current datetime is used
    :return: The remaining time in minutes
    """
    return get_remaining_time_in_seconds(end_datetime, start_datetime) // 60


def get_datetime_in_future_seconds(seconds: int) -> datetime:
    """
    Get the datetime in the future
    :param seconds: The number of seconds in the future
    :return: The datetime in the future
    """

    return datetime.datetime.now() + datetime.timedelta(seconds=int(seconds))


def get_datetime_in_future_hours(hours: float) -> datetime:
    """
    Get the datetime in the future
    :param hours: The number of hours in the future
    :return: The datetime in the future
    """

    return get_datetime_in_future_seconds(int(hours * 3600))


def get_datetime_in_future_days(days: int) -> datetime:
    """
    Get the datetime in the future
    :param days: The number of days in the future
    :return: The datetime in the future
    """

    return get_datetime_in_future_hours(days * 24)


def get_random_time_between(start_datetime: datetime, end_datetime: datetime) -> datetime:
    """
    Get a random time between the start and end datetime
    :param start_datetime: The start datetime
    :param end_datetime: The end datetime
    :return: The random datetime
    """

    return start_datetime + datetime.timedelta(
        seconds=random.randint(0, int((end_datetime - start_datetime).total_seconds())))


def get_random_time_between_by_cron(cron_expression: str) -> datetime:
    """
    Get a random time between now and the next cron run
    :param cron_expression: The cron expression
    :return: The random datetime
    """

    return get_random_time_between(datetime.datetime.now(datetime.timezone.utc), get_next_run(cron_expression))


def get_random_time_between_by_hours(hours: int) -> datetime:
    """
    Get a random time between now and next n hours
    :param hours: The number of hours
    :return: The random datetime
    """

    return get_random_time_between(datetime.datetime.now(), get_datetime_in_future_hours(hours))


def get_random_time_between_by_seconds(seconds: int) -> datetime:
    """
    Get a random time between now and next n seconds
    :param seconds: The number of seconds
    :return: The random datetime
    """

    return get_random_time_between(datetime.datetime.now(), get_datetime_in_future_seconds(seconds))


def default_datetime_format(date_time: datetime, user: User = None) -> str:
    """
    Default datetime format
    :param date_time: The datetime
    :param user: The user. If given, the timezone of the user will be used
    :return: The formatted datetime
    """

    return get_time_with_timezone(date_time, user).strftime(c.STANDARD_DATE_TIME_FORMAT)


def default_date_format(date: datetime, user: User = None) -> str:
    """
    Default date format
    :param date: The date
    :param user: The user. If given, the timezone of the user will be used
    :return: The formatted date
    """

    return get_time_with_timezone(date, user).strftime(c.STANDARD_DATE_FORMAT)


def get_time_with_timezone(date_time: datetime, user: User) -> datetime:
    """
    Get the time with timezone
    :param date_time: The datetime
    :param user: The user. If given, the timezone of the user will be used
    :return: The time with timezone
    """

    if user is None:
        return date_time

    # If datetime is without timezone, add the default timezone in case it's not timezone aware
    if date_time.tzinfo is None:
        date_time = date_time.replace(tzinfo=pytz.timezone(Env.TZ.get()))

    timezone = user.timezone if user.timezone is not None else Env.TZ.get()

    return date_time.astimezone(pytz.timezone(timezone))


def get_utc_offset(timezone_name: str) -> str:
    """
    Get the UTC offset for a timezone
    return: The UTC offset
    """
    if timezone_name is None:
        timezone_name = Env.TZ.get()

    # Get the timezone object
    timezone = pytz.timezone(timezone_name)
    # Get the current UTC offset for the timezone
    current_offset = datetime.datetime.now(timezone).utcoffset()
    # Extract hours and minutes from the offset
    hours, minutes = divmod(current_offset.total_seconds(), 3600)
    # Determine if the offset is positive or negative
    if hours < 0:
        sign = "-"
    else:
        sign = "+"

    # Format the offset as a string
    offset_str = f"{sign}{abs(int(hours)):02}:{abs(int(minutes)):02}"

    return offset_str


def get_timezone_from_location(location_name):
    # Initialize a geolocator
    geolocator = Nominatim(user_agent="timezone_app")
    # Get the location (latitude and longitude) from the location name
    location = geolocator.geocode(location_name)

    if location:
        # Get the timezone from the coordinates
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
        return timezone_str
    else:
        return None


def get_duration_from_string(duration: str) -> int:
    """
    Get the duration from a string (e.g. 1h, 2min, 3sec)
    :param duration: The duration
    :return: The duration in seconds
    """

    try:
        return int(duration) * 60  # Default duration is in minutes
    except ValueError:
        # Extract the contingent non-numeric characters
        return get_unit_value_from_string(duration, c.DURATION_UNIT_TO_SECONDS)


async def validate_duration(update: Update, context: ContextTypes.DEFAULT_TYPE, duration: str,
                            add_delete_button: bool = True, inbound_keyboard: Keyboard = None,
                            previous_screens: list[Screen] = None, previous_screen_list_keyboard_info: dict = None
                            ) -> bool:
    """
    Validates the duration
    :param update: Telegram update
    :param context: Telegram context
    :param duration: The duration
    :param add_delete_button: Whether to add a delete button to the keyboard
    :param inbound_keyboard: The inbound keyboard
    :param previous_screens: The previous screens, for the back button if in private chat
    :param previous_screen_list_keyboard_info: The previous screen list keyboard info, for the back button if in private
    :return: Whether the duration is valid
    """

    try:
        get_duration_from_string(duration)
        return True
    except ValueError:
        await full_message_send(context, phrases.ACTION_INVALID_DURATION, update=update,
                                add_delete_button=add_delete_button, inbound_keyboard=inbound_keyboard,
                                previous_screens=previous_screens,
                                previous_screen_list_keyboard_info=previous_screen_list_keyboard_info)
        return False


def datetime_is_past(dt: datetime) -> bool:
    """
    Check if the datetime is before the current datetime
    :param dt: The datetime
    :return: Whether the datetime is after the current datetime
    """

    if dt is None:
        return True

    return dt < datetime.datetime.now()
