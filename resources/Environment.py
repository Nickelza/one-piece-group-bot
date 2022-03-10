import os
from distutils.util import strtobool


class Environment:
    def __init__(self, name: str, default_value: str = None, can_be_empty: bool = False):
        self.name = name
        self.default_value = default_value
        self.can_be_empty = can_be_empty

    def get(self) -> str | None:
        # If default value is set, return the environment variable or the default value
        if self.default_value is not None:
            return os.environ.get(self.name, self.default_value)

        # Get the environment variable or return None if it is not set
        value = os.environ.get(self.name)

        # If the environment variable is not set and the environment variable can be empty, return None
        if value is None and self.can_be_empty:
            return None

        # If the environment variable is not set and the environment variable can not be empty, raise an exception
        if value is None:
            raise Exception(f"Environment variable {self.name} is not set")

        return value

    def get_int(self) -> int:
        """
        Get the environment variable as an integer
        :return: The environment variable as an integer
        """
        return int(self.get())

    def get_float(self) -> float:
        """
        Get the environment variable as a float
        :return: The environment variable as a float
        """
        return float(self.get())

    def get_bool(self) -> bool:
        """
        Get the environment variable as a boolean
        :return: The environment variable as a boolean
        """
        return strtobool(self.get())


# Bot
BOT_TOKEN = Environment('BOT_TOKEN')
BOT_DROP_PENDING_UPDATES = Environment('BOT_DROP_PENDING_UPDATES', default_value='False')

# CONFIG
# Which timezone to use
TZ = Environment('TZ', default_value='Etc/UTC')

# DATABASE
# Database name
DB_NAME = Environment('DB_NAME')
# Database host
DB_HOST = Environment('DB_HOST')
# Database port
DB_PORT = Environment('DB_PORT')
# Database user
DB_USER = Environment('DB_USER')
# Database password
DB_PASSWORD = Environment('DB_PASSWORD')

# TELEGRAM CHAT
# Group chat id
OPD_GROUP_ID = Environment('OPD_GROUP_ID')
# Main channel id
OPD_CHANNEL_ID = Environment('OPD_CHANNEL_ID')
# ChatID for admin commands
ADMIN_GROUP_ID = Environment('ADMIN_GROUP_ID')

# REDDIT
# Reddit client id
REDDIT_CLIENT_ID = Environment('REDDIT_CLIENT_ID')
# Reddit client secret
REDDIT_CLIENT_SECRET = Environment('REDDIT_CLIENT_SECRET')
# Reddit username
REDDIT_USER_AGENT = Environment('REDDIT_USER_AGENT')

# TIMERS
# Check for files to clean up. Default: 12 hours
CRON_TEMP_DIR_CLEANUP = Environment('CRON_TEMP_DIR_CLEANUP', default_value='0 */12 * * *')
# Create and send the leaderboard. Default: Every sunday at midnight
CRON_SEND_LEADERBOARD = Environment('CRON_SEND_LEADERBOARD', default_value='0 0 * * Sun')
# Reset bounties. Default: Every first day of the month at 00:10
CRON_RESET_BOUNTY = Environment('CRON_RESET_BOUNTY', default_value='10 0 1 * *')
# Send an alert messaging informing when the next bounty reset is. Default: Every last day of the month at 00:10
CRON_RESET_BOUNTY_ALERT = Environment('CRON_RESET_BOUNTY_ALERT', default_value='10 0 last * *')
# Reset Doc Q game playability. Default: Every day at midnight
CRON_RESET_DOC_Q_GAME = Environment('CRON_RESET_DOC_Q_GAME', default_value='0 0 * * *')  # Every day at midnight
# Reset bounty poster limit. Default: Every day at 00:10
CRON_RESET_BOUNTY_POSTER_LIMIT = Environment('CRON_RESET_BOUNTY_POSTER_LIMIT', default_value='10 0 * * *')

# How much time should temp files be kept before they are deleted. Default: 6 hours
TEMP_DIR_CLEANUP_TIME_SECONDS = Environment('TEMP_DIR_CLEANUP_TIME_SECONDS', '21600')

# BOUNTY
# How much a single message is worth. Default: 50,000
BELLY_BASE_MESSAGE = Environment('BELLY_BASE_MESSAGE', default_value='50000')
# Multiplier to use for each message. Default: 0.05
BELLY_CHARACTER_MULTIPLIER = Environment('BELLY_CHARACTER_MULTIPLIER', default_value='0.05')
# How much multiple of the base message can the multiplier by character be, before it is capped. Default: 2
BELLY_CHARACTER_MAX_MULTIPLE = Environment('BELLY_CHARACTER_MAX_MULTIPLE', default_value='2')
# Multiplier for messages in reply to a channel post. Default: 1.3
BELLY_REPLY_TO_CHANNEL_POST_MULTIPLIER = Environment('BELLY_REPLY_TO_CHANNEL_POST_MULTIPLIER', default_value='1.3')
# Multiplier for stickers. Default: 0.2
BELLY_STICKER_MULTIPLIER = Environment('BELLY_STICKER_MULTIPLIER', default_value='0.2')
# Multiplier for animations. Default: 0.2
BELLY_ANIMATION_MULTIPLIER = Environment('BELLY_ANIMATION_MULTIPLIER', default_value='0.2')

# BOUNTY POSTER
# How many times Pirate King can display bounty poster before it is reset. Default: -1 (unlimited)
BOUNTY_POSTER_LIMIT_PIRATE_KING = Environment('BOUNTY_POSTER_LIMIT_PIRATE_KING', default_value='-1')
# How many times Emperors can display bounty poster before it is reset. Default: 1
BOUNTY_POSTER_LIMIT_EMPEROR = Environment('BOUNTY_POSTER_LIMIT_EMPEROR', default_value='1')
# How many times First Mates can display bounty poster before it is reset. Default: 0
BOUNTY_POSTER_LIMIT_FIRST_MATE = Environment('BOUNTY_POSTER_LIMIT_FIRST_MATE', default_value='0')
# How many times Supernovas can display bounty poster before it is reset. Default: 0
BOUNTY_POSTER_LIMIT_SUPERNOVA = Environment('BOUNTY_POSTER_LIMIT_SUPERNOVA', default_value='0')
# How many times Rookies can display bounty poster before it is reset. Default: 0
BOUNTY_POSTER_LIMIT_ROOKIE = Environment('BOUNTY_POSTER_LIMIT_ROOKIE', default_value='0')

# How many entries should be shown in the leaderboard. Default: 20
LEADERBOARD_LIMIT = Environment('LEADERBOARD_LIMIT', default_value='20')

# DOC Q
# How much bounty is required to play the Doc Q game. Default: 10,000,000
DOC_Q_GAME_REQUIRED_BOUNTY = Environment('DOC_Q_GAME_REQUIRED_BOUNTY', default_value='10000000')
# How many options should be shown in the Doc Q game. Default: 5
DOC_Q_GAME_OPTIONS_COUNT = Environment('DOC_Q_GAME_OPTIONS_COUNT', default_value='5')
# Chance of winning the game. Default: 0.2
DOC_Q_GAME_WIN_ODD = Environment('DOC_Q_GAME_WIN_ODD', default_value='0.2')
# Show correct option. Default: True
DOC_Q_GAME_SHOW_CORRECT_OPTION = Environment('DOC_Q_GAME_SHOW_CORRECT_OPTION', default_value='True')
