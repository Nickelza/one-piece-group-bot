import datetime
import random

import parsedatetime
import pytz
from apscheduler.triggers.cron import CronTrigger
from croniter import croniter
from geopy.geocoders import Nominatim
from telegram import Update
from telegram.ext import ContextTypes
from timezonefinder import TimezoneFinder

import constants as c
import resources.Environment as Env
from resources import phrases
from src.model.User import User
from src.model.enums.Screen import Screen
from src.model.error.CustomException import DateValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send, escape_valid_markdown_chars
from src.utils.string_utils import get_unit_value_from_string


def get_next_run(
    cron_expression: str,
    start_datetime: datetime.datetime = None,
    previous_fire_time: datetime.datetime = None,
) -> datetime.datetime:
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


def get_previous_run(cron_expression: str, start_datetime: datetime = None) -> datetime:
    """
    Get the previous run time
    :param cron_expression: The cron expression
    :param start_datetime: The start datetime. If None, the current datetime is used
    :return: The previous run time
    """

    if start_datetime is None:
        start_datetime = datetime.datetime.now(datetime.timezone.utc)

    itr = croniter(cron_expression, start_datetime)
    return itr.get_prev(datetime.datetime)


def next_run_is_today(cron_expression: str) -> bool:
    """
    Check if the next run is today
    :param cron_expression: The cron expression
    :return: Whether the next run is today
    """

    next_run = get_next_run(cron_expression)
    return next_run.date() == datetime.datetime.now().date()


def convert_seconds_to_duration(seconds: int | float, show_full: bool = False) -> str:
    """
    Converts seconds to days, hours, minutes, seconds
    :param seconds: Seconds to convert
    :param show_full: Whether to show all units when available
    :return: Days, hours e.g. 1 day 2 hours 5 minutes
    """
    weeks = int(seconds // 604800)
    remaining_seconds = seconds % 604800
    days = int(remaining_seconds // 86400)
    remaining_seconds = seconds % 86400
    hours = int(remaining_seconds // 3600)
    remaining_seconds = seconds % 3600
    minutes = int(remaining_seconds // 60)
    remaining_seconds %= 60

    if seconds == 0:
        return "0 seconds"

    result = ""
    if weeks > 0:
        if weeks == 1:
            result += f"{weeks} week"
        else:
            result += f"{weeks} weeks"

    # Show days only in last week
    if days > 0 and (weeks == 0 or show_full):
        if days == 1:
            result += f"{days} day"
        else:
            result += f"{days} days"

    # Show hours only in last 2 days
    if hours > 0 and ((days <= 1 and weeks == 0) or show_full):
        if len(result) > 0:
            result += " "
        if hours == 1:
            result += f"{hours} hour"
        else:
            result += f"{hours} hours"

    # Show minutes only in last 24 hours
    if minutes > 0 and ((hours < 24 and days == 0 and weeks == 0) or show_full):
        if len(result) > 0:
            result += " "
        if minutes > 0:
            if minutes == 1:
                result += f"{minutes} minute"
            else:
                result += f"{minutes} minutes"

    # Show seconds only in last minute
    if remaining_seconds >= 0 and (
        (minutes <= 1 and hours == 0 and days == 0 and weeks == 0) or show_full
    ):
        if len(result) > 0:
            result += " "
        if remaining_seconds > 0:
            if remaining_seconds == 1:
                result += f"{remaining_seconds} second"
            else:
                result += f"{remaining_seconds} seconds"

    return result


def convert_minutes_to_duration(minutes: int, show_full: bool = False) -> str:
    """
    Converts minutes to days, hours, minutes, seconds
    :param minutes: Minutes to convert
    :param show_full: Whether to show all units when available
    :return: Days, hours e.g. 1 day 2 hours 5 minutes
    """
    return convert_seconds_to_duration(minutes * 60, show_full=show_full)


def convert_hours_to_duration(hours: int, show_full: bool = False) -> str:
    """
    Converts hours to days, hours, minutes, seconds
    :param hours: Hours to convert
    :param show_full: Whether to show all units when available
    :return: Days, hours e.g. 1 day 2 hours 5 minutes
    """
    return convert_seconds_to_duration(hours * 3600, show_full=show_full)


def convert_days_to_duration(days: int, show_full: bool = False) -> str:
    """
    Converts days to days, hours, minutes, seconds
    :param days: Days to convert
    :param show_full: Whether to show all units when available
    :return: Days, hours e.g. 1 day 2 hours 5 minutes
    """
    return convert_seconds_to_duration(days * 86400, show_full=show_full)


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
    return convert_seconds_to_duration((next_run - start_datetime).total_seconds())


def get_remaining_duration(
    end_datetime: datetime.datetime, start_datetime: datetime.datetime = None
) -> str:
    """
    Get the remaining time until the end_datetime
    :param end_datetime: The end datetime
    :param start_datetime: The start datetime. If None, the current datetime is used
    :return: The remaining time in days and hours e.g. 1 day 2h hours
    """
    if end_datetime is None:
        return convert_seconds_to_duration(0)

    if start_datetime is None:
        start_datetime = datetime.datetime.now()

    # Remove offset awareness from end_datetime
    end_datetime = end_datetime.replace(tzinfo=None)
    return convert_seconds_to_duration(int((end_datetime - start_datetime).total_seconds()))


def get_elapsed_seconds(start_datetime: datetime) -> int:
    """
    Get the elapsed time since the start_datetime
    :param start_datetime: The start datetime
    :return: The elapsed time in seconds
    """
    if start_datetime is None:
        return 0

    # Remove offset awareness from start_datetime
    start_datetime = start_datetime.replace(tzinfo=None)
    return int((datetime.datetime.now() - start_datetime).total_seconds())


def get_elapsed_hours(start_datetime: datetime) -> int:
    """
    Get the elapsed time since the start_datetime
    :param start_datetime: The start datetime
    :return: The elapsed time in hours
    """
    return get_elapsed_seconds(start_datetime) // 3600


def get_elapsed_duration(start_datetime: datetime) -> str:
    """
    Get the elapsed time since the start_datetime
    :param start_datetime: The start datetime
    :return: The elapsed time in days and hours e.g. 1 day 2h hours
    """

    return convert_seconds_to_duration(get_elapsed_seconds(start_datetime))


def get_remaining_time_from_next_cron(
    cron_expression: str, start_datetime: datetime = None
) -> str:
    """
    Get the remaining time until the next cron run
    :param cron_expression: The cron expression
    :param start_datetime: The start datetime. If None, the current datetime is used
    :return: The remaining time in days and hours e.g. 1 day 2h hours
    """
    if start_datetime is None:
        start_datetime = datetime.datetime.now(datetime.timezone.utc)

    next_run = get_next_run(cron_expression, start_datetime)
    return get_remaining_duration(next_run)


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


def get_datetime_in_future_seconds(seconds: int, start_time: datetime.datetime = None) -> datetime:
    """
    Get the datetime in the future
    :param seconds: The number of seconds in the future
    :param start_time: The start time. If None, the current datetime is used
    :return: The datetime in the future
    """

    if start_time is None:
        start_time = datetime.datetime.now()

    return start_time + datetime.timedelta(seconds=int(seconds))


def get_datetime_in_future_minutes(minutes: int, start_time: datetime.datetime = None) -> datetime:
    """
    Get the datetime in the future
    :param minutes: The number of minutes in the future
    :param start_time: The start time. If None, the current datetime is used
    :return: The datetime in the future
    """

    return get_datetime_in_future_seconds(minutes * 60, start_time)


def get_datetime_in_future_hours(hours: float, start_time: datetime.datetime = None) -> datetime:
    """
    Get the datetime in the future
    :param hours: The number of hours in the future
    :param start_time: The start time. If None, the current datetime is used
    :return: The datetime in the future
    """

    return get_datetime_in_future_seconds(int(hours * 3600), start_time)


def get_datetime_in_future_days(days: int, start_time: datetime.datetime = None) -> datetime:
    """
    Get the datetime in the future
    :param days: The number of days in the future
    :param start_time: The start time. If None, the current datetime is used
    :return: The datetime in the future
    """

    return get_datetime_in_future_hours(days * 24, start_time)


def get_random_time_between(start_datetime: datetime, end_datetime: datetime) -> datetime:
    """
    Get a random time between the start and end datetime
    :param start_datetime: The start datetime
    :param end_datetime: The end datetime
    :return: The random datetime
    """

    return start_datetime + datetime.timedelta(
        seconds=random.randint(0, int((end_datetime - start_datetime).total_seconds()))
    )


def get_random_time_between_by_cron(cron_expression: str) -> datetime:
    """
    Get a random time between now and the next cron run
    :param cron_expression: The cron expression
    :return: The random datetime
    """

    return get_random_time_between(
        datetime.datetime.now(datetime.timezone.utc), get_next_run(cron_expression)
    )


def get_random_time_between_by_days(days: int) -> datetime:
    """
    Get a random time between now and next n days
    :param days: The number of days
    :return: The random datetime
    """

    return get_random_time_between(datetime.datetime.now(), get_datetime_in_future_days(days))


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

    return get_random_time_between(
        datetime.datetime.now(), get_datetime_in_future_seconds(seconds)
    )


def default_datetime_format(
    date_time: datetime,
    user: User = None,
    add_remaining_time: bool = False,
    add_elapsed_time: bool = False,
    time_format: str = c.STANDARD_DATE_TIME_FORMAT,
) -> str:
    """
    Default datetime format
    :param date_time: The datetime
    :param user: The user. If given, the timezone of the user will be used
    :param add_remaining_time: Whether to add the remaining time
    :param add_elapsed_time: Whether to add the elapsed time
    :param time_format: The time format
    :return: The formatted datetime
    """

    text = get_time_with_timezone(date_time, user).strftime(time_format)

    if not add_remaining_time and not add_elapsed_time:
        return text

    if add_remaining_time:
        if datetime_is_before(date_time):
            return text

        return text + phrases.DATETIME_REMAINING_PARENTHESIS.format(
            get_remaining_duration(date_time)
        )

    if datetime_is_after(date_time):
        return text

    return text + phrases.DATETIME_ELAPSED_PARENTHESIS.format(get_elapsed_duration(date_time))


def default_date_format(
    date: datetime,
    user: User = None,
    add_remaining_time: bool = False,
    add_elapsed_time: bool = False,
) -> str:
    """
    Default date format
    :param date: The date
    :param user: The user. If given, the timezone of the user will be used
    :param add_remaining_time: Whether to add the remaining time
    :param add_elapsed_time: Whether to add the elapsed time
    :return: The formatted date
    """

    return default_datetime_format(
        date,
        user,
        add_remaining_time=add_remaining_time,
        add_elapsed_time=add_elapsed_time,
        time_format=c.STANDARD_DATE_FORMAT,
    )


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

    return date_time.astimezone(user.get_timezone())


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


async def validate_duration(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    duration: str,
    add_delete_button: bool = True,
    inbound_keyboard: Keyboard = None,
    previous_screens: list[Screen] = None,
    previous_screen_list_keyboard_info: dict = None,
) -> bool:
    """
    Validates the duration
    :param update: Telegram update
    :param context: Telegram context
    :param duration: The duration
    :param add_delete_button: Whether to add a delete button to the keyboard
    :param inbound_keyboard: The inbound keyboard
    :param previous_screens: The previous screens, for the back button if in private chat
    :param previous_screen_list_keyboard_info: The previous screen list keyboard info, for the back
     button if in private
    :return: Whether the duration is valid
    """

    try:
        get_duration_from_string(duration)
        return True
    except ValueError:
        await full_message_send(
            context,
            phrases.ACTION_INVALID_DURATION,
            update=update,
            add_delete_button=add_delete_button,
            inbound_keyboard=inbound_keyboard,
            previous_screens=previous_screens,
            previous_screen_list_keyboard_info=previous_screen_list_keyboard_info,
        )
        return False


def datetime_is_before(
    dt: datetime, starting_date: datetime = None, tz: pytz.tzinfo = None
) -> bool:
    """
    Check if the datetime is before the current datetime
    :param dt: The datetime
    :param starting_date: The starting date
    :param tz: The timezone
    :return: Whether the datetime is after the current datetime
    """

    if dt is None:
        return True

    if tz is None:
        tz = pytz.timezone(Env.TZ.get())

    # Add timezone to datetime if it's not timezone aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=tz)

    # If staring date in give, convert it to the same timezone as dt
    if starting_date is not None:
        if starting_date.tzinfo is None:
            starting_date = starting_date.replace(tzinfo=tz)
        else:
            starting_date = starting_date.astimezone(tz)
    else:
        starting_date = datetime.datetime.now(tz)

    return dt < starting_date


def datetime_is_after(
    dt: datetime, starting_date: datetime = None, tz: pytz.tzinfo = None
) -> bool:
    """
    Check if the datetime is after the current datetime
    :param dt: The datetime
    :param starting_date: The starting date
    :param tz: The timezone
    :return: Whether the datetime is after the current datetime
    """

    return not datetime_is_before(dt, starting_date, tz)


def get_datetime_from_natural_language(text: str, user: User) -> datetime.datetime:
    """
    Get the datetime from a natural language string
    :param text: The text
    :param user: The user
    :return: The datetime
    """

    cal = parsedatetime.Calendar()
    user_tz = user.get_timezone()

    # Get now
    now: datetime.datetime = datetime.datetime.now(user_tz).replace(microsecond=0)
    parsed_datetime = cal.parseDT(text, now, tzinfo=user_tz)[0].replace(microsecond=0)

    # If input is the same as now, it means the string is invalid
    if parsed_datetime == now:
        raise DateValidationException()

    # Convert to default timezone
    return parsed_datetime.astimezone(pytz.timezone(Env.TZ.get()))


def get_user_timezone_and_offset_text(user: User) -> (str, str):
    """
    Get the user timezone and offset text
    :param user: The user
    :return: The user timezone and offset text
    """

    timezone_text = (
        escape_valid_markdown_chars(user.timezone)
        if user.timezone is not None
        else phrases.PVT_TXT_SETTINGS_TIMEZONE_UNKNOWN
    )
    offset_text = get_utc_offset(user.timezone)

    return timezone_text, offset_text


def get_day_in_past(days: int = 0) -> datetime.datetime:
    """
    Get the day in the past
    :param days: The number of days in the past
    :return: The datetime
    """

    return datetime.datetime.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    ) - datetime.timedelta(days=days)


def is_same_day(date_1: datetime.datetime, date_2: datetime.datetime = None) -> bool:
    """
    Check if two dates are the same day
    :param date_1: The first date
    :param date_2: The second date
    :return: Whether the dates are the same day
    """

    if date_2 is None:
        date_2 = datetime.datetime.now()

    return date_1.date() == date_2.date()
