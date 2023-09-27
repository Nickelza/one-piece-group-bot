from datetime import datetime

import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

import constants as c
import resources.Environment as Env
from src.model.User import User


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
    current_offset = datetime.now(timezone).utcoffset()
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
