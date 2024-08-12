import os
import sys
from distutils.util import strtobool

from dotenv import load_dotenv

import constants as c


class Environment:
    instances: list["Environment"] = []

    def __init__(self, name: str, default_value: str = None, can_be_empty: bool = False):
        self.name = name
        self.default_value = default_value
        self.can_be_empty = can_be_empty

        Environment.instances.append(self)

    def get_or_none(self) -> str | None:
        """
        Get the environment variable or None if it is not set
        :return: The environment variable or None if it is not set
        :rtype: str | None
        """
        # If default value is set, return the environment variable or the default value
        if self.default_value is not None:
            return os.environ.get(self.name, self.default_value)

        # Get the environment variable or return None if it is not set
        value = os.environ.get(self.name)

        # If the environment variable is not set and the environment variable can be empty,
        # return None
        if value is None and self.can_be_empty:
            return None

        # If the environment variable is not set and the environment variable can not be empty,
        # raise an exception
        if value is None:
            raise Exception(f"Environment variable {self.name} is not set")

        return value

    def get(self) -> str:
        """
        Get the environment variable
        :return: The environment variable
        """
        value = self.get_or_none()
        if value is None and not self.can_be_empty:
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
        from src.utils.math_utils import format_percentage_value

        return format_percentage_value(float(self.get()))

    def get_bool(self) -> bool:
        """
        Get the environment variable as a boolean
        :return: The environment variable as a boolean
        """
        return True if strtobool(self.get()) else False

    def get_list(self) -> list[str]:
        """
        Get the environment variable as a list
        :return: The environment variable as a list
        """
        return self.get().split(c.STANDARD_SPLIT_CHAR)

    def get_belly(self):
        """
        Get the environment variable as a belly amount
        :return: The environment variable as a belly amount
        """

        return "{0:,}".format(self.get_int())

    def __str__(self) -> str:
        return self.get()


if len(sys.argv) > 1:
    load_dotenv(sys.argv[1])
else:
    load_dotenv()

# Bot
BOT_TOKEN = Environment("BOT_TOKEN")
BOT_DROP_PENDING_UPDATES = Environment("BOT_DROP_PENDING_UPDATES", default_value="False")
BOT_ID = Environment("BOT_ID")
BOT_USERNAME = Environment("BOT_USERNAME")

# CONFIG
# Which timezone to use
TZ = Environment("TZ", default_value="Etc/UTC")
# Log level
LOG_LEVEL = Environment("LOG_LEVEL", default_value="INFO")

# DATABASE
# Database name
DB_NAME = Environment("DB_NAME")
# Database host
DB_HOST = Environment("DB_HOST")
# Database port
DB_PORT = Environment("DB_PORT")
# Database user
DB_USER = Environment("DB_USER")
# Database password
DB_PASSWORD = Environment("DB_PASSWORD")
# Log queries
DB_LOG_QUERIES = Environment("DB_LOG_QUERIES", default_value="False")

# TELEGRAM CHAT
# Limit interaction to authorized users
LIMIT_TO_AUTHORIZED_USERS = Environment("LIMIT_TO_AUTHORIZED_USERS", default_value="False")
# List of authorized users
AUTHORIZED_USERS = Environment("AUTHORIZED_USERS", default_value="")
# Limit interaction to users members of authorized groups
LIMIT_TO_AUTHORIZED_GROUPS = Environment("LIMIT_TO_AUTHORIZED_GROUPS", default_value="False")
# List of authorized groups
AUTHORIZED_GROUPS = Environment("AUTHORIZED_GROUPS", default_value="")
# Group chat id
MAIN_GROUP_ID = Environment("MAIN_GROUP_ID", can_be_empty=True)
# Chat ID for error logs
ERROR_LOG_CHAT_ID = Environment("ERROR_LOG_CHAT_ID", can_be_empty=True)
# OPMA bot id
OPMA_BOT_ID = Environment("OPMA_BOT_ID", default_value="921260484")
# Updates channel id
UPDATES_CHAT_ID = Environment("UPDATES_CHAT_ID")
# Support group id
SUPPORT_GROUP_LINK = Environment("SUPPORT_GROUP_LINK", default_value="https://t.me/bountysystem")

# TgRest Channel ID
TG_REST_CHANNEL_ID = Environment("TG_REST_CHANNEL_ID", can_be_empty=True)

# ANTI SPAM
# How many messages can be sent in private chat before spam is detected. Default: 30
ANTI_SPAM_PRIVATE_CHAT_MESSAGE_LIMIT = Environment(
    "ANTI_SPAM_PRIVATE_CHAT_MESSAGE_LIMIT", default_value="30"
)
# How many messages can be sent in group chat before spam is detected. Default: 20
ANTI_SPAM_GROUP_CHAT_MESSAGE_LIMIT = Environment(
    "ANTI_SPAM_GROUP_CHAT_MESSAGE_LIMIT", default_value="20"
)
# Time interval in seconds to check for spam. Default: 60
ANTI_SPAM_TIME_INTERVAL_SECONDS = Environment(
    "ANTI_SPAM_TIME_INTERVAL_SECONDS", default_value="60"
)

# REDDIT
# Enable reddit posts from r/onepiece and r/memepiece
ENABLE_REDDIT_POSTS = Environment("ENABLE_REDDIT_POSTS", default_value="False")
# Reddit client id
REDDIT_CLIENT_ID = Environment("REDDIT_CLIENT_ID", can_be_empty=True)
# Reddit client secret
REDDIT_CLIENT_SECRET = Environment("REDDIT_CLIENT_SECRET", can_be_empty=True)
# Reddit username
REDDIT_USER_AGENT = Environment("REDDIT_USER_AGENT", can_be_empty=True)
# Reddit One Piece Subreddit
REDDIT_ONE_PIECE_SUBREDDIT = Environment("REDDIT_ONE_PIECE_SUBREDDIT", default_value="onepiece")
# Reddit Meme Piece Subreddit
REDDIT_MEME_PIECE_SUBREDDIT = Environment("REDDIT_MEME_PIECE_SUBREDDIT", default_value="memepiece")

# SUPABASE
# Supabase rest url
SUPABASE_REST_URL = Environment("SUPABASE_REST_URL", can_be_empty=True)
# Supabase API key
SUPABASE_API_KEY = Environment("SUPABASE_API_KEY", can_be_empty=True)

# SENTRY
# Enable Sentry
SENTRY_ENABLED = Environment("SENTRY_ENABLED", default_value="False")
# Sentry DSN
SENTRY_DSN = Environment("SENTRY_DSN", can_be_empty=True)
# Sentry environment
SENTRY_ENVIRONMENT = Environment("SENTRY_ENVIRONMENT", default_value="default")
# Sentry enable tracing
SENTRY_ENABLE_TRACING = Environment("SENTRY_ENABLE_TRACING", default_value="False")
# Sentry traces sample rate (0-1). Higher is more frequent but less performant. Default: 1.0
SENTRY_TRACES_SAMPLE_RATE = Environment("SENTRY_TRACES_SAMPLE_RATE", default_value="1.0")
# Sentry profiles sample rate (0-1). Higher is more frequent but less performant. Default: 1.0
SENTRY_PROFILES_SAMPLE_RATE = Environment("SENTRY_PROFILES_SAMPLE_RATE", default_value="1.0")
# Sentry log level. Default: INFO
SENTRY_LOG_LEVEL = Environment("SENTRY_LOG_LEVEL", default_value="INFO")
# Sentry log event level. Default: INFO
SENTRY_LOG_EVENT_LEVEL = Environment("SENTRY_LOG_EVENT_LEVEL", default_value="INFO")

# TIMERS
# Check for files to clean up. Default: 12 hours
CRON_TEMP_DIR_CLEANUP = Environment("CRON_TEMP_DIR_CLEANUP", default_value="0 */12 * * *")
ENABLE_TIMER_TEMP_DIR_CLEANUP = Environment("ENABLE_TIMER_TEMP_DIR_CLEANUP", default_value="True")
SHOULD_LOG_TIMER_TEMP_DIR_CLEANUP = Environment(
    "SHOULD_LOG_TIMER_TEMP_DIR_CLEANUP", default_value="False"
)
SHOULD_RUN_ON_STARTUP_TEMP_DIR_CLEANUP = Environment(
    "SHOULD_RUN_ON_STARTUP_TEMP_DIR_CLEANUP", default_value="False"
)

# Create and send the leaderboard. Default: Every sunday at midnight
CRON_SEND_LEADERBOARD = Environment("CRON_SEND_LEADERBOARD", default_value="0 0 * * Sun")
ENABLE_TIMER_SEND_LEADERBOARD = Environment("ENABLE_TIMER_SEND_LEADERBOARD", default_value="True")
SHOULD_LOG_TIMER_SEND_LEADERBOARD = Environment(
    "SHOULD_LOG_TIMER_SEND_LEADERBOARD", default_value="False"
)
SHOULD_RUN_ON_STARTUP_SEND_LEADERBOARD = Environment(
    "SHOULD_RUN_ON_STARTUP_SEND_LEADERBOARD", default_value="False"
)

# Reset bounty poster limit. Default: Every day at 00:10
CRON_RESET_BOUNTY_POSTER_LIMIT = Environment(
    "CRON_RESET_BOUNTY_POSTER_LIMIT", default_value="10 0 * * *"
)
ENABLE_TIMER_RESET_BOUNTY_POSTER_LIMIT = Environment(
    "ENABLE_TIMER_RESET_BOUNTY_POSTER_LIMIT", default_value="True"
)
SHOULD_LOG_TIMER_RESET_BOUNTY_POSTER_LIMIT = Environment(
    "SHOULD_LOG_TIMER_RESET_BOUNTY_POSTER_LIMIT", default_value="False"
)
SHOULD_RUN_ON_STARTUP_RESET_BOUNTY_POSTER_LIMIT = Environment(
    "SHOULD_RUN_ON_STARTUP_RESET_BOUNTY_POSTER_LIMIT", default_value="False"
)

# Reset can change region. Default: Every sunday at midnight
CRON_RESET_CAN_CHANGE_REGION = Environment(
    "CRON_RESET_CAN_CHANGE_REGION", default_value="0 0 * * Sun"
)
ENABLE_TIMER_RESET_CAN_CHANGE_REGION = Environment(
    "ENABLE_TIMER_RESET_CAN_CHANGE_REGION", default_value="True"
)
SHOULD_LOG_TIMER_RESET_CAN_CHANGE_REGION = Environment(
    "SHOULD_LOG_TIMER_RESET_CAN_CHANGE_REGION", default_value="False"
)
SHOULD_RUN_ON_STARTUP_RESET_CAN_CHANGE_REGION = Environment(
    "SHOULD_RUN_ON_STARTUP_RESET_CAN_CHANGE_REGION", default_value="False"
)

# Bounty bonus for users in region. Default: Every day at 00:10
CRON_ADD_REGION_BOUNTY_BONUS = Environment(
    "CRON_ADD_REGION_BOUNTY_BONUS", default_value="10 0 * * *"
)
ENABLE_TIMER_ADD_REGION_BOUNTY_BONUS = Environment(
    "ENABLE_TIMER_ADD_REGION_BOUNTY_BONUS", default_value="True"
)
SHOULD_LOG_TIMER_ADD_REGION_BOUNTY_BONUS = Environment(
    "SHOULD_LOG_TIMER_ADD_REGION_BOUNTY_BONUS", default_value="False"
)
SHOULD_RUN_ON_STARTUP_ADD_REGION_BOUNTY_BONUS = Environment(
    "SHOULD_RUN_ON_STARTUP_ADD_REGION_BOUNTY_BONUS", default_value="False"
)
# Bounty bonus for Crew members. Default: Every day at 00:10
CRON_ADD_CREW_BOUNTY_BONUS = Environment("CRON_ADD_CREW_BOUNTY_BONUS", default_value="10 0 * * *")
ENABLE_TIMER_ADD_CREW_BOUNTY_BONUS = Environment(
    "ENABLE_TIMER_ADD_CREW_BOUNTY_BONUS", default_value="True"
)
SHOULD_LOG_TIMER_ADD_CREW_BOUNTY_BONUS = Environment(
    "SHOULD_LOG_TIMER_ADD_CREW_BOUNTY_BONUS", default_value="False"
)
SHOULD_RUN_ON_STARTUP_ADD_CREW_BOUNTY_BONUS = Environment(
    "SHOULD_RUN_ON_STARTUP_ADD_CREW_BOUNTY_BONUS", default_value="False"
)
# Bounty bonus for Crew members with bounty higher than crew average. Default: Every day at 00:10
CRON_ADD_CREW_MVP_BOUNTY_BONUS = Environment(
    "CRON_ADD_CREW_MVP_BOUNTY_BONUS", default_value="10 0 * * *"
)
ENABLE_TIMER_ADD_CREW_MVP_BOUNTY_BONUS = Environment(
    "ENABLE_TIMER_ADD_CREW_MVP_BOUNTY_BONUS", default_value="True"
)
SHOULD_LOG_TIMER_ADD_CREW_MVP_BOUNTY_BONUS = Environment(
    "SHOULD_LOG_TIMER_ADD_CREW_MVP_BOUNTY_BONUS", default_value="False"
)
SHOULD_RUN_ON_STARTUP_ADD_CREW_MVP_BOUNTY_BONUS = Environment(
    "SHOULD_RUN_ON_STARTUP_ADD_CREW_MVP_BOUNTY_BONUS", default_value="False"
)
# Daily Reward. Default: Every 12 hours
CRON_DAILY_REWARD = Environment("CRON_DAILY_REWARD", default_value="0 */12 * * *")
ENABLE_TIMER_DAILY_REWARD = Environment("ENABLE_TIMER_DAILY_REWARD", default_value="True")
SHOULD_LOG_TIMER_DAILY_REWARD = Environment("SHOULD_LOG_TIMER_DAILY_REWARD", default_value="False")
SHOULD_RUN_ON_STARTUP_DAILY_REWARD = Environment(
    "SHOULD_RUN_ON_STARTUP_DAILY_REWARD", default_value="False"
)
# Maximum amount of bounty that can be gained from messages. Default: Every day at 00:10
CRON_RESET_BOUNTY_MESSAGE_LIMIT = Environment(
    "CRON_RESET_BOUNTY_MESSAGE_LIMIT", default_value="10 0 * * *"
)
ENABLE_TIMER_RESET_BOUNTY_MESSAGE_LIMIT = Environment(
    "ENABLE_TIMER_RESET_BOUNTY_MESSAGE_LIMIT", default_value="True"
)
SHOULD_LOG_TIMER_RESET_BOUNTY_MESSAGE_LIMIT = Environment(
    "SHOULD_LOG_TIMER_RESET_BOUNTY_MESSAGE_LIMIT", default_value="False"
)
SHOULD_RUN_ON_STARTUP_RESET_BOUNTY_MESSAGE_LIMIT = Environment(
    "SHOULD_RUN_ON_STARTUP_RESET_BOUNTY_MESSAGE_LIMIT", default_value="False"
)

# Reddit post One Piece. Default: Every day at 00:00 and 12:00
CRON_REDDIT_POST_ONE_PIECE = Environment(
    "CRON_REDDIT_POST_ONE_PIECE", default_value="0 0,12 * * *"
)
ENABLE_TIMER_REDDIT_POST_ONE_PIECE = Environment(
    "ENABLE_TIMER_REDDIT_POST_ONE_PIECE", default_value="True"
)
SHOULD_LOG_TIMER_REDDIT_POST_ONE_PIECE = Environment(
    "SHOULD_LOG_TIMER_REDDIT_POST_ONE_PIECE", default_value="False"
)
SHOULD_RUN_ON_STARTUP_REDDIT_POST_ONE_PIECE = Environment(
    "SHOULD_RUN_ON_STARTUP_REDDIT_POST_ONE_PIECE", default_value="False"
)
# Reddit Meme post Piece. Default: Every day at 06:00 and 18:00
CRON_REDDIT_POST_MEME_PIECE = Environment(
    "CRON_REDDIT_POST_MEME_PIECE", default_value="0 6,18 * * *"
)
ENABLE_TIMER_REDDIT_POST_MEME_PIECE = Environment(
    "ENABLE_TIMER_REDDIT_POST_MEME_PIECE", default_value="True"
)
SHOULD_LOG_TIMER_REDDIT_POST_MEME_PIECE = Environment(
    "SHOULD_LOG_TIMER_REDDIT_POST_MEME_PIECE", default_value="False"
)
SHOULD_RUN_ON_STARTUP_REDDIT_POST_MEME_PIECE = Environment(
    "SHOULD_RUN_ON_STARTUP_REDDIT_POST_MEME_PIECE", default_value="False"
)

# Send scheduled predictions. Default: Every 1 minute
CRON_SEND_SCHEDULED_PREDICTIONS = Environment(
    "CRON_SEND_SCHEDULED_PREDICTIONS", default_value="*/1 * * * *"
)
ENABLE_TIMER_SEND_SCHEDULED_PREDICTIONS = Environment(
    "ENABLE_TIMER_SEND_SCHEDULED_PREDICTIONS", default_value="True"
)
SHOULD_LOG_TIMER_SEND_SCHEDULED_PREDICTIONS = Environment(
    "SHOULD_LOG_TIMER_SEND_SCHEDULED_PREDICTIONS", default_value="False"
)
SHOULD_RUN_ON_STARTUP_SEND_SCHEDULED_PREDICTIONS = Environment(
    "SHOULD_RUN_ON_STARTUP_SEND_SCHEDULED_PREDICTIONS", default_value="False"
)

# Close scheduled predictions. Default: Every 1 minute
CRON_CLOSE_SCHEDULED_PREDICTIONS = Environment(
    "CRON_CLOSE_SCHEDULED_PREDICTIONS", default_value="*/1 * * * *"
)
ENABLE_TIMER_CLOSE_SCHEDULED_PREDICTIONS = Environment(
    "ENABLE_TIMER_CLOSE_SCHEDULED_PREDICTIONS", default_value="True"
)
SHOULD_LOG_TIMER_CLOSE_SCHEDULED_PREDICTIONS = Environment(
    "SHOULD_LOG_TIMER_CLOSE_SCHEDULED_PREDICTIONS", default_value="False"
)
SHOULD_RUN_ON_STARTUP_CLOSE_SCHEDULED_PREDICTIONS = Environment(
    "SHOULD_RUN_ON_STARTUP_CLOSE_SCHEDULED_PREDICTIONS", default_value="False"
)

# Refresh active predictions group message. Default: Every 20 minutes
CRON_REFRESH_ACTIVE_PREDICTIONS_GROUP_MESSAGE = Environment(
    "CRON_REFRESH_ACTIVE_PREDICTIONS_GROUP_MESSAGE", default_value="*/20 * * * *"
)
ENABLE_TIMER_REFRESH_ACTIVE_PREDICTIONS_GROUP_MESSAGE = Environment(
    "ENABLE_TIMER_REFRESH_ACTIVE_PREDICTIONS_GROUP_MESSAGE", default_value="True"
)
SHOULD_LOG_TIMER_REFRESH_ACTIVE_PREDICTIONS_GROUP_MESSAGE = Environment(
    "SHOULD_LOG_TIMER_REFRESH_ACTIVE_PREDICTIONS_GROUP_MESSAGE", default_value="False"
)
SHOULD_RUN_ON_STARTUP_REFRESH_ACTIVE_PREDICTIONS_GROUP_MESSAGE = Environment(
    "SHOULD_RUN_ON_STARTUP_REFRESH_ACTIVE_PREDICTIONS_GROUP_MESSAGE", default_value="False"
)

# Schedule Devil Fruit Zoan release. Default: Every sunday at 00:10, to make sure inactive ones
# were already revoked
CRON_SCHEDULE_DEVIL_FRUIT_ZOAN_RELEASE = Environment(
    "CRON_SCHEDULE_DEVIL_FRUIT_ZOAN_RELEASE", default_value="10 0 * * Sun"
)
ENABLE_TIMER_SCHEDULE_DEVIL_FRUIT_ZOAN_RELEASE = Environment(
    "ENABLE_TIMER_SCHEDULE_DEVIL_FRUIT_ZOAN_RELEASE", default_value="True"
)
SHOULD_LOG_TIMER_SCHEDULE_DEVIL_FRUIT_ZOAN_RELEASE = Environment(
    "SHOULD_LOG_TIMER_SCHEDULE_DEVIL_FRUIT_ZOAN_RELEASE", default_value="False"
)
SHOULD_RUN_ON_STARTUP_SCHEDULE_DEVIL_FRUIT_ZOAN_RELEASE = Environment(
    "SHOULD_RUN_ON_STARTUP_SCHEDULE_DEVIL_FRUIT_ZOAN_RELEASE", default_value="False"
)

# Respawn Devil Fruit. Default: Every 1 minute
CRON_RESPAWN_DEVIL_FRUIT = Environment("CRON_RESPAWN_DEVIL_FRUIT", default_value="*/1 * * * *")
ENABLE_TIMER_RESPAWN_DEVIL_FRUIT = Environment(
    "ENABLE_TIMER_RESPAWN_DEVIL_FRUIT", default_value="True"
)
SHOULD_LOG_TIMER_RESPAWN_DEVIL_FRUIT = Environment(
    "SHOULD_LOG_TIMER_RESPAWN_DEVIL_FRUIT", default_value="False"
)
SHOULD_RUN_ON_STARTUP_RESPAWN_DEVIL_FRUIT = Environment(
    "SHOULD_RUN_ON_STARTUP_RESPAWN_DEVIL_FRUIT", default_value="False"
)

# Deactivate inactive groups and group chats and group users. Default: Every day at midnight
CRON_DEACTIVATE_INACTIVE_GROUP_CHATS = Environment(
    "CRON_DEACTIVATE_INACTIVE_GROUP_CHATS", default_value="0 0 * * *"
)
ENABLE_TIMER_DEACTIVATE_INACTIVE_GROUP_CHATS = Environment(
    "ENABLE_TIMER_DEACTIVATE_INACTIVE_GROUP_CHATS", default_value="True"
)
SHOULD_LOG_TIMER_DEACTIVATE_INACTIVE_GROUP_CHATS = Environment(
    "SHOULD_LOG_TIMER_DEACTIVATE_INACTIVE_GROUP_CHATS", default_value="False"
)
SHOULD_RUN_ON_STARTUP_DEACTIVATE_INACTIVE_GROUP_CHATS = Environment(
    "SHOULD_RUN_ON_STARTUP_DEACTIVATE_INACTIVE_GROUP_CHATS", default_value="False"
)

# End inactive games. Default: Every 5 minutes
CRON_END_INACTIVE_GAMES = Environment("CRON_END_INACTIVE_GAMES", default_value="*/5 * * * *")
ENABLE_TIMER_END_INACTIVE_GAMES = Environment(
    "ENABLE_TIMER_END_INACTIVE_GAMES", default_value="True"
)
SHOULD_LOG_TIMER_END_INACTIVE_GAMES = Environment(
    "SHOULD_LOG_TIMER_END_INACTIVE_GAMES", default_value="False"
)
SHOULD_RUN_ON_STARTUP_END_INACTIVE_GAMES = Environment(
    "SHOULD_RUN_ON_STARTUP_END_INACTIVE_GAMES", default_value="False"
)

# Set expired bounty loans. Default: Every 1 minute
CRON_SET_EXPIRED_BOUNTY_LOANS = Environment(
    "CRON_SET_EXPIRED_BOUNTY_LOANS", default_value="*/1 * * * *"
)
ENABLE_TIMER_SET_EXPIRED_BOUNTY_LOANS = Environment(
    "ENABLE_TIMER_SET_EXPIRED_BOUNTY_LOANS", default_value="True"
)
SHOULD_LOG_TIMER_SET_EXPIRED_BOUNTY_LOANS = Environment(
    "SHOULD_LOG_TIMER_SET_EXPIRED_BOUNTY_LOANS", default_value="False"
)
SHOULD_RUN_ON_STARTUP_SET_EXPIRED_BOUNTY_LOANS = Environment(
    "SHOULD_RUN_ON_STARTUP_SET_EXPIRED_BOUNTY_LOANS", default_value="False"
)

# Fight and plunder decrease scout count. Default: Every 15 minutes
CRON_FIGHT_PLUNDER_SCOUT_COUNT_DECREASE = Environment(
    "CRON_FIGHT_PLUNDER_SCOUT_COUNT_DECREASE", default_value="*/15 * * * *"
)
ENABLE_TIMER_FIGHT_PLUNDER_SCOUT_COUNT_DECREASE = Environment(
    "ENABLE_TIMER_FIGHT_PLUNDER_SCOUT_COUNT_DECREASE", default_value="True"
)
SHOULD_LOG_TIMER_FIGHT_PLUNDER_SCOUT_COUNT_DECREASE = Environment(
    "SHOULD_LOG_TIMER_FIGHT_PLUNDER_SCOUT_COUNT_DECREASE", default_value="False"
)
SHOULD_RUN_ON_STARTUP_FIGHT_PLUNDER_SCOUT_COUNT_DECREASE = Environment(
    "SHOULD_RUN_ON_STARTUP_FIGHT_PLUNDER_SCOUT_COUNT_DECREASE", default_value="False"
)

# Generic task. Default: Every 1 minute
CRON_MINUTE_TASKS = Environment("CRON_MINUTE_TASKS", default_value="*/1 * * * *")
ENABLE_TIMER_MINUTE_TASKS = Environment("ENABLE_TIMER_MINUTE_TASKS", default_value="True")
SHOULD_LOG_TIMER_MINUTE_TASKS = Environment("SHOULD_LOG_TIMER_MINUTE_TASKS", default_value="False")
SHOULD_RUN_ON_STARTUP_MINUTE_TASKS = Environment(
    "SHOULD_RUN_ON_STARTUP_MINUTE_TASKS", default_value="False"
)

# How much time should temp files be kept before they are deleted. Default: 6 hours
TEMP_DIR_CLEANUP_TIME_SECONDS = Environment("TEMP_DIR_CLEANUP_TIME_SECONDS", default_value="21600")

# BOUNTY
# How much should belly be upper rounded. Default: 1000
BELLY_UPPER_ROUND_AMOUNT = Environment("BELLY_UPPER_ROUND_AMOUNT", default_value="1000")

# After how many days from the last message should a group or group chat be considered inactive.
# Default: 7
INACTIVE_GROUP_DAYS = Environment("INACTIVE_GROUP_DAYS", default_value="7")
# After how many days from the last message should a user be considered inactive in a group.
# Default: 7
INACTIVE_GROUP_USER_DAYS = Environment("INACTIVE_GROUP_USER_DAYS", default_value="7")

# DAILY REWARD
# Base Bonus amount. Default: 10 Million
DAILY_REWARD_BONUS_BASE_AMOUNT = Environment(
    "DAILY_REWARD_BONUS_BASE_AMOUNT", default_value="10000000"
)
# Location base Bonus. Default: 2
DAILY_REWARD_BONUS_BASE_LOCATION = Environment(
    "DAILY_REWARD_BONUS_BASE_LOCATION", default_value="2"
)
# Streak base Bonus. Default: 1
DAILY_REWARD_BONUS_BASE_STREAK = Environment("DAILY_REWARD_BONUS_BASE_STREAK", default_value="1")
# Streak max Bonus. Default: 100
DAILY_REWARD_BONUS_MAX_STREAK = Environment("DAILY_REWARD_BONUS_MAX_STREAK", default_value="100")
# Crew level base Bonus. Default: 10
DAILY_REWARD_BONUS_BASE_CREW_LEVEL = Environment(
    "DAILY_REWARD_BONUS_BASE_CREW_LEVEL", default_value="10"
)
# Crew members with bounty higher than crew average. Default: 20
DAILY_REWARD_BONUS_CREW_MVP = Environment("DAILY_REWARD_BONUS_CREW_MVP", default_value="20")
# Every how many streak days is a prize given. Default: 7
DAILY_REWARD_STREAK_DAYS = Environment("DAILY_REWARD_STREAK_DAYS", default_value="7")
# Probability of obtaining Belly as a daily reward prize. Default: 90%
DAILY_REWARD_PRIZE_BELLY_PERCENTAGE = Environment(
    "DAILY_REWARD_PRIZE_BELLY_PERCENTAGE", default_value="90"
)
# Probability of obtaining SMILE as a daily reward prize. Default: 10%
DAILY_REWARD_PRIZE_SMILE_PERCENTAGE = Environment(
    "DAILY_REWARD_PRIZE_SMILE_PERCENTAGE", default_value="10"
)

# BOUNTY POSTER
# How many times Pirate King can display bounty poster before it is reset. Default: -1 (is boss)
BOUNTY_POSTER_LIMIT_PIRATE_KING = Environment(
    "BOUNTY_POSTER_LIMIT_PIRATE_KING", default_value="-1"
)
# How many times Warlords  can display bounty poster before it is reset. Default: 3
BOUNTY_POSTER_LIMIT_WARLORD = Environment("BOUNTY_POSTER_LIMIT_WARLORD", default_value="3")
# How many times Emperors can display bounty poster before it is reset. Default: 1
BOUNTY_POSTER_LIMIT_EMPEROR = Environment("BOUNTY_POSTER_LIMIT_EMPEROR", default_value="1")
# How many times First Mates can display bounty poster before it is reset. Default: 0
BOUNTY_POSTER_LIMIT_FIRST_MATE = Environment("BOUNTY_POSTER_LIMIT_FIRST_MATE", default_value="0")
# How many times Supernovas can display bounty poster before it is reset. Default: 0
BOUNTY_POSTER_LIMIT_SUPERNOVA = Environment("BOUNTY_POSTER_LIMIT_SUPERNOVA", default_value="0")
# How many times Rookies can display bounty poster before it is reset. Default: 0
BOUNTY_POSTER_LIMIT_ROOKIE = Environment("BOUNTY_POSTER_LIMIT_ROOKIE", default_value="0")

# How many crew entries should be shown in the leaderboard. Default: 5
LEADERBOARD_CREW_LIMIT = Environment("LEADERBOARD_CREW_LIMIT", default_value="5")
# How many active users are required to create a local leaderboard. Default: 20
LEADERBOARD_MIN_ACTIVE_USERS = Environment("LEADERBOARD_MIN_ACTIVE_USERS", default_value="20")

# DOC Q
# How much bounty is required to play the Doc Q game. Default: 10,000,000
DOC_Q_GAME_REQUIRED_BOUNTY = Environment("DOC_Q_GAME_REQUIRED_BOUNTY", default_value="10000000")
# How many options should be shown in the Doc Q game. Default: 5
DOC_Q_GAME_OPTIONS_COUNT = Environment("DOC_Q_GAME_OPTIONS_COUNT", default_value="5")
# Chance of winning the game. Default: 0.2
DOC_Q_GAME_WIN_ODD = Environment("DOC_Q_GAME_WIN_ODD", default_value="0.2")
# How many options should be shown in the Doc Q game if on final location. Default: 10
DOC_Q_GAME_OPTIONS_COUNT_FINAL_LOCATION = Environment(
    "DOC_Q_GAME_OPTIONS_COUNT_FINAL_LOCATION", default_value="10"
)
# Chance of winning the game if on final location. Default: 0.1
DOC_Q_GAME_WIN_ODD_FINAL_LOCATION = Environment(
    "DOC_Q_GAME_WIN_ODD_FINAL_LOCATION", default_value="0.1"
)
# Show correct option. Default: False
DOC_Q_GAME_SHOW_CORRECT_OPTION = Environment(
    "DOC_Q_GAME_SHOW_CORRECT_OPTION", default_value="False"
)
# How long a user has to wait before playing the game again in hours. Default: 24
DOC_Q_GAME_COOLDOWN_DURATION = Environment("DOC_Q_GAME_COOLDOWN_DURATION", default_value="24")

# Minimum wager for games. Default: 5 million
GAME_MIN_WAGER = Environment("GAME_MIN_WAGER", default_value="5000000")
# Maximum total wager for easy mode. Default: 50 million
GAME_MAX_TOTAL_WAGER_EASY = Environment("GAME_MAX_TOTAL_WAGER_EASY", default_value="50000000")
# Maximum total wager for medium mode. Default: 200 million
GAME_MAX_TOTAL_WAGER_MEDIUM = Environment("GAME_MAX_TOTAL_WAGER_MEDIUM", default_value="200000000")
# After how much time in seconds without action should a user be notified about their turn in seconds. Default: 60
GAME_TURN_NOTIFICATION_TIME_SECONDS = Environment(
    "GAME_TURN_NOTIFICATION_TIME_SECONDS", default_value="60"
)
# After how much time in seconds without action should a move be automatically made in seconds. Default: 60
GAME_TURN_AUTO_MOVE_TIME_SECONDS = Environment(
    "GAME_TURN_AUTO_MOVE_TIME_SECONDS", default_value="60"
)
# Game cooldown duration in hours. Default: 8
GAME_COOLDOWN_DURATION = Environment("GAME_COOLDOWN_DURATION", default_value="8")
# Game accept global cooldown duration in hours. Default: 2
GAME_GLOBAL_ACCEPT_COOLDOWN_DURATION = Environment(
    "GAME_GLOBAL_ACCEPT_COOLDOWN_DURATION", default_value="2"
)
# How much time to wait for opponent confirmation before timing out. Default: 60 seconds
GAME_CONFIRMATION_TIMEOUT = Environment("GAME_CONFIRMATION_TIMEOUT", default_value="60")
# How much time to wait after user has confirmed the game before starting the game.
# Default: 30 seconds
GAME_START_WAIT_TIME = Environment("GAME_START_WAIT_TIME", default_value="30")
# After how much time since the last interaction should a game be considered inactive. # Default: 10 minutes
GAME_INACTIVE_TIME_SINCE_INTERACTION_MINUTES = Environment(
    "GAME_INACTIVE_TIME_SINCE_INTERACTION_MINUTES", default_value="10"
)
# After how much time since the start should a game be considered inactive in minutes. Default: 60 minutes
GAME_INACTIVE_TIME_SINCE_START_MINUTES = Environment(
    "GAME_INACTIVE_TIME_SINCE_START_MINUTES", default_value="60"
)
# After how much time should a global game be considered inactive if an opponent has not yet accepted it in hours.
# Default: 12 hours
GAME_GLOBAL_INACTIVE_HOURS = Environment("GAME_GLOBAL_INACTIVE_HOURS", default_value="12")

# One Piece Wiki URL
ONE_PIECE_WIKI_URL = Environment(
    "ONE_PIECE_WIKI_URL", default_value="https://onepiece.fandom.com/wiki/"
)

# Show bullet location. Default: False
RUSSIAN_ROULETTE_SHOW_BULLET_LOCATION = Environment(
    "RUSSIAN_ROULETTE_SHOW_BULLET_LOCATION", default_value="False"
)
# How much time to wait before sending the next level in Who's Who game. Default: 30 seconds
WHOS_WHO_NEXT_LEVEL_WAIT_TIME = Environment("WHOS_WHO_NEXT_LEVEL_WAIT_TIME", default_value="30")
# Shambles grid size easy mode. Default: 7
SHAMBLES_GRID_SIZE_EASY = Environment("SHAMBLES_GRID_SIZE_EASY", default_value="7")
# Shambles grid size medium mode. Default: 10
SHAMBLES_GRID_SIZE_MEDIUM = Environment("SHAMBLES_GRID_SIZE_MEDIUM", default_value="10")
# Shambles grid size hard mode. Default: 13
SHAMBLES_GRID_SIZE_HARD = Environment("SHAMBLES_GRID_SIZE_HARD", default_value="13")
# How much time to wait before sending the next level in Shambles game. Default: 60 seconds
SHAMBLES_NEXT_LEVEL_WAIT_TIME = Environment("SHAMBLES_NEXT_LEVEL_WAIT_TIME", default_value="60")
# Starting lives in Guess or Life game. Default: 5
GUESS_OR_LIFE_STARTING_LIVES = Environment("GUESS_OR_LIFE_STARTING_LIVES", default_value="5")
# How much time to wait before issuing a new life in Guess or Life game. Default: 30 seconds
GUESS_OR_LIFE_NEW_LIFE_WAIT_TIME = Environment(
    "GUESS_OR_LIFE_NEW_LIFE_WAIT_TIME", default_value="30"
)
# Guess or Life max number of characters in Guess or Life game. Default: 100
GUESS_OR_LIFE_MAX_CHARACTERS = Environment("GUESS_OR_LIFE_MAX_CHARACTERS", default_value="100")
# Guess or Life max unique characters in easy mode. Default: 5
GUESS_OR_LIFE_MAX_UNIQUE_CHARACTERS_EASY = Environment(
    "GUESS_OR_LIFE_MAX_UNIQUE_CHARACTERS_EASY", default_value="5"
)
# Guess or Life m unique characters in medium mode. Default: 10
GUESS_OR_LIFE_MAX_UNIQUE_CHARACTERS_MEDIUM = Environment(
    "GUESS_OR_LIFE_MAX_UNIQUE_CHARACTERS_MEDIUM", default_value="10"
)
# How much time to wait before sending the next detail in Punk Records game. Default: 30 seconds
PUNK_RECORDS_NEXT_DETAIL_WAIT_TIME = Environment(
    "PUNK_RECORDS_NEXT_DETAIL_WAIT_TIME", default_value="30"
)
# How many details should be revealed at the start of the game. Default: 3
PUNK_RECORDS_STARTING_DETAILS = Environment("PUNK_RECORDS_STARTING_DETAILS", default_value="3")

LOCATION_PARADISE_IMAGE_URL = Environment(
    "LOCATION_PARADISE_IMAGE_URL", default_value="https://i.imgur.com/omBDMbu.jpg"
)
LOCATION_NEW_WORLD_IMAGE_URL = Environment(
    "LOCATION_NEW_WORLD_IMAGE_URL", default_value="https://i.imgur.com/J5EWet5.jpg"
)
LOCATION_FOOSHA_VILLAGE_IMAGE_URL = Environment(
    "LOCATION_FOOSHA_VILLAGE_IMAGE_URL", default_value="https://i.imgur.com/v8W3lHy.png"
)
LOCATION_SHELLS_TOWN_IMAGE_URL = Environment(
    "LOCATION_SHELLS_TOWN_IMAGE_URL", default_value="https://i.imgur.com/638z7dA.png"
)
LOCATION_ORANGE_TOWN_IMAGE_URL = Environment(
    "LOCATION_ORANGE_TOWN_IMAGE_URL", default_value="https://i.imgur.com/2v2UAHc.png"
)
LOCATION_ISLAND_OF_RARE_ANIMALS_IMAGE_URL = Environment(
    "LOCATION_ISLAND_OF_RARE_ANIMALS_IMAGE_URL", default_value="https://i.imgur.com/S8ejYiJ.png"
)
LOCATION_SYRUP_VILLAGE_IMAGE_URL = Environment(
    "LOCATION_SYRUP_VILLAGE_IMAGE_URL", default_value="https://imgur.com/klCUJHq.jpg"
)
LOCATION_BARATIE_IMAGE_URL = Environment(
    "LOCATION_BARATIE_IMAGE_URL", default_value="https://i.imgur.com/41PA2tE.jpg"
)
LOCATION_ARLONG_PARK_IMAGE_URL = Environment(
    "LOCATION_ARLONG_PARK_IMAGE_URL", default_value="https://i.imgur.com/6uAZaqn.jpg"
)
LOCATION_LOUGETOWN_IMAGE_URL = Environment(
    "LOCATION_LOUGETOWN_IMAGE_URL", default_value="https://i.imgur.com/NfwXoAI.jpg"
)
LOCATION_REVERSE_MOUNTAIN_IMAGE_URL = Environment(
    "LOCATION_REVERSE_MOUNTAIN_IMAGE_URL", default_value="https://i.imgur.com/iamqwq8.png"
)
LOCATION_WHISKEY_PEAK_IMAGE_URL = Environment(
    "LOCATION_WHISKEY_PEAK_IMAGE_URL", default_value="https://i.imgur.com/c5gfVLe.jpg"
)
LOCATION_LITTLE_GARDEN_IMAGE_URL = Environment(
    "LOCATION_LITTLE_GARDEN_IMAGE_URL", default_value="https://i.imgur.com/ns5U5S6.png"
)
LOCATION_DRUM_ISLAND_IMAGE_URL = Environment(
    "LOCATION_DRUM_ISLAND_IMAGE_URL", default_value="https://i.imgur.com/8lvNZbu.png"
)
LOCATION_ARABASTA_KINGDOM_IMAGE_URL = Environment(
    "LOCATION_ARABASTA_KINGDOM_IMAGE_URL", default_value="https://i.imgur.com/Cw9jqsJ.jpg"
)
LOCATION_JAYA_IMAGE_URL = Environment(
    "LOCATION_JAYA_IMAGE_URL", default_value="https://i.imgur.com/e1NLOjT.png"
)
LOCATION_SKYPIEA_IMAGE_URL = Environment(
    "LOCATION_SKYPIEA_IMAGE_URL", default_value="https://i.imgur.com/cfJ4o0Z.jpg"
)
LOCATION_LONG_RING_LONG_LAND_IMAGE_URL = Environment(
    "LOCATION_LONG_RING_LONG_LAND_IMAGE_URL", default_value="https://i.imgur.com/M1UZrls.png"
)
LOCATION_WATER_7_IMAGE_URL = Environment(
    "LOCATION_WATER_7_IMAGE_URL", default_value="https://i.imgur.com/IqbkOAP.png"
)
LOCATION_ENIES_LOBBY_IMAGE_URL = Environment(
    "LOCATION_ENIES_LOBBY_IMAGE_URL", default_value="https://i.imgur.com/56LeSDp.png"
)
LOCATION_THRILLER_BARK_IMAGE_URL = Environment(
    "LOCATION_THRILLER_BARK_IMAGE_URL", default_value="https://i.imgur.com/vZpyTyU.png"
)
LOCATION_SABAODY_ARCHIPELAGO_IMAGE_URL = Environment(
    "LOCATION_SABAODY_ARCHIPELAGO_IMAGE_URL", default_value="https://i.imgur.com/DYssFxB.jpg"
)
LOCATION_FISHMAN_ISLAND_IMAGE_URL = Environment(
    "LOCATION_FISHMAN_ISLAND_IMAGE_URL", default_value="https://i.imgur.com/kt7zEpu.jpg"
)
LOCATION_PUNK_HAZARD_IMAGE_URL = Environment(
    "LOCATION_PUNK_HAZARD_IMAGE_URL", default_value="https://i.imgur.com/H5AszLU.png"
)
LOCATION_DRESSROSA_IMAGE_URL = Environment(
    "LOCATION_DRESSROSA_IMAGE_URL", default_value="https://i.imgur.com/sGLRtpO.jpg"
)
LOCATION_ZOU_IMAGE_URL = Environment(
    "LOCATION_ZOU_IMAGE_URL", default_value="https://i.imgur.com/UD2YCV4.jpg"
)
LOCATION_WHOLE_CAKE_ISLAND_IMAGE_URL = Environment(
    "LOCATION_WHOLE_CAKE_ISLAND_IMAGE_URL", default_value="https://i.imgur.com/fEAM6eN.jpg"
)
LOCATION_WANO_COUNTRY_IMAGE_URL = Environment(
    "LOCATION_WANO_COUNTRY_IMAGE_URL", default_value="https://i.imgur.com/vznQ3W2.jpg"
)
LOCATION_EGGHEAD_IMAGE_URL = Environment(
    "LOCATION_EGGHEAD_IMAGE_URL", default_value="https://i.imgur.com/mPsUp7x.jpeg"
)

# How long fight immunity lasts in hours. Default: 6 hours
FIGHT_IMMUNITY_DURATION = Environment("FIGHT_IMMUNITY_DURATION", default_value="6")
# How long a user has to wait before fighting another user in hours. Default: 2 hours
FIGHT_COOLDOWN_DURATION = Environment("FIGHT_COOLDOWN_DURATION", default_value="2")
# Maximum win probability for Pirate King. Default: 99.99%
FIGHT_MAX_WIN_PROBABILITY_PIRATE_KING = Environment(
    "FIGHT_MAX_WIN_PROBABILITY_PIRATE_KING", default_value="99"
)
# Maximum win probability for Emperor. Default: 95%
FIGHT_MAX_WIN_PROBABILITY_EMPEROR = Environment(
    "FIGHT_MAX_WIN_PROBABILITY_EMPEROR", default_value="95"
)
# Maximum win probability for First Mate. Default: 90%
FIGHT_MAX_WIN_PROBABILITY_FIRST_MATE = Environment(
    "FIGHT_MAX_WIN_PROBABILITY_FIRST_MATE", default_value="90"
)
# Maximum win probability for Supernova. Default: 85%
FIGHT_MAX_WIN_PROBABILITY_SUPERNOVA = Environment(
    "FIGHT_MAX_WIN_PROBABILITY_SUPERNOVA", default_value="85"
)
# Maximum win probability for Rookie. Default: 80%
FIGHT_MAX_WIN_PROBABILITY_ROOKIE = Environment(
    "FIGHT_MAX_WIN_PROBABILITY_ROOKIE", default_value="80"
)
# Maximum win probability when on final location. Default: 50%
FIGHT_MAX_WIN_PROBABILITY_FINAL_LOCATION = Environment(
    "FIGHT_MAX_WIN_PROBABILITY_FINAL_LOCATION", default_value="50"
)
# Maximum win probability when on Devil Fruit defense boost. Default: 99.99%
FIGHT_MAX_WIN_PROBABILITY_DEVIL_FRUIT_DEFENSE_BOOST = Environment(
    "FIGHT_MAX_WIN_PROBABILITY_DEVIL_FRUIT_DEFENSE_BOOST", default_value="99.99"
)
# Minimum win probability for Pirate King. Default: 1%
FIGHT_MIN_WIN_PROBABILITY_PIRATE_KING = Environment(
    "FIGHT_MIN_WIN_PROBABILITY_PIRATE_KING", default_value="1"
)
# Minimum win probability for Emperor. Default: 1%
FIGHT_MIN_WIN_PROBABILITY_EMPEROR = Environment(
    "FIGHT_MIN_WIN_PROBABILITY_EMPEROR", default_value="1"
)
# Minimum win probability for First Mate. Default: 1%
FIGHT_MIN_WIN_PROBABILITY_FIRST_MATE = Environment(
    "FIGHT_MIN_WIN_PROBABILITY_FIRST_MATE", default_value="1"
)
# Minimum win probability for Supernova. Default: 1%
FIGHT_MIN_WIN_PROBABILITY_SUPERNOVA = Environment(
    "FIGHT_MIN_WIN_PROBABILITY_SUPERNOVA", default_value="1"
)
# Minimum win probability for Rookie. Default: 1%
FIGHT_MIN_WIN_PROBABILITY_ROOKIE = Environment(
    "FIGHT_MIN_WIN_PROBABILITY_ROOKIE", default_value="1"
)
# For how much time after a fight or plunder attack is revenge allowed. Default: 24 hours
FIGHT_PLUNDER_REVENGE_DURATION_HOURS = Environment(
    "FIGHT_PLUNDER_REVENGE_DURATION_HOURS", default_value="24"
)
# Fight and plunder scouting base price. Default: 10.000
FIGHT_PLUNDER_SCOUT_BASE_PRICE = Environment(
    "FIGHT_PLUNDER_SCOUT_BASE_PRICE", default_value="10000"
)
# Fight and plunder scouting price multiplier for group. Default: 10
FIGHT_PLUNDER_SCOUT_FEE_MULTIPLIER_GROUP = Environment(
    "FIGHT_PLUNDER_SCOUT_FEE_MULTIPLIER_GROUP", default_value="10"
)

# Minimum wager for prediction bets. Default: 5 million
PREDICTION_BET_MIN_WAGER = Environment("PREDICTION_BET_MIN_WAGER", default_value="5000000")
# How long a user has to wait before creating a new prediction in hours. Default: 48 hours
PREDICTION_CREATE_COOLDOWN_DURATION = Environment(
    "PREDICTION_CREATE_COOLDOWN_DURATION", default_value="48"
)

# Send leaderboard message. Default: True
SEND_MESSAGE_LEADERBOARD = Environment("SEND_MESSAGE_LEADERBOARD", default_value="True")
# Send location update message. Default: True
SEND_MESSAGE_LOCATION_UPDATE = Environment("SEND_MESSAGE_LOCATION_UPDATE", default_value="True")
# Send move to new world proposal message. Default: True
SEND_MESSAGE_MOVE_TO_NEW_WORLD_PROPOSAL = Environment(
    "SEND_MESSAGE_MOVE_TO_NEW_WORLD_PROPOSAL", default_value="True"
)

# Required location to use DocQ. Default: 14 (Jaya)
REQUIRED_LOCATION_LEVEL_DOC_Q_GAME = Environment(
    "REQUIRED_LOCATION_LEVEL_DOC_Q_GAME", default_value="14"
)
# Required location to send stickers. Default: 10 (Whiskey Peak)
REQUIRED_LOCATION_LEVEL_SEND_STICKER = Environment(
    "REQUIRED_LOCATION_LEVEL_SEND_STICKER", default_value="10"
)
# Required location to send animations. Default: 10 (Whiskey Peak)
REQUIRED_LOCATION_LEVEL_SEND_ANIMATION = Environment(
    "REQUIRED_LOCATION_LEVEL_SEND_ANIMATION", default_value="10"
)
# Required location to forward messages. Default: 10 (Whiskey Peak)
REQUIRED_LOCATION_LEVEL_FORWARD_MESSAGE = Environment(
    "REQUIRED_LOCATION_LEVEL_FORWARD_MESSAGE", default_value="10"
)
# Required location to send dice emoji. Default: 21 (Fishman Island)
REQUIRED_LOCATION_LEVEL_SEND_DICE_EMOJI = Environment(
    "REQUIRED_LOCATION_LEVEL_SEND_DICE_EMOJI", default_value="21"
)
# Required location to use inline bots. Default: 21 (Fishman Island)
REQUIRED_LOCATION_LEVEL_USE_INLINE_BOTS = Environment(
    "REQUIRED_LOCATION_LEVEL_USE_INLINE_BOTS", default_value="21"
)
# Required location to fight. Default: 10 (Whiskey Peak)
REQUIRED_LOCATION_LEVEL_FIGHT = Environment("REQUIRED_LOCATION_LEVEL_FIGHT", default_value="10")
# Required location to play games. Default: 1 (Foosha Village)
REQUIRED_LOCATION_LEVEL_GAME = Environment("REQUIRED_LOCATION_LEVEL_GAME", default_value="1")
# Required location to bet on predictions. Default: 1 (Foosha Village)
REQUIRED_LOCATION_LEVEL_PREDICTION_BET = Environment(
    "REQUIRED_LOCATION_LEVEL_PREDICTION_BET", default_value="1"
)
# Required location to create predictions. Default: 21 (Fishman Island)
REQUIRED_LOCATION_LEVEL_PREDICTION_CREATE = Environment(
    "REQUIRED_LOCATION_LEVEL_PREDICTION_CREATE", default_value="21"
)
# Required location to collect Devil Fruit. Default: 10 (Whiskey Peak)
REQUIRED_LOCATION_LEVEL_DEVIL_FRUIT_COLLECT = Environment(
    "REQUIRED_LOCATION_LEVEL_DEVIL_FRUIT_COLLECT", default_value="10"
)
# Required location to view log stats. Default: 21 (Fishman Island)
REQUIRED_LOCATION_LEVEL_LOG_STATS = Environment(
    "REQUIRED_LOCATION_LEVEL_LOG_STATS", default_value="21"
)
# Required location to plunder. Default: 10 (Whiskey Peak)
REQUIRED_LOCATION_LEVEL_PLUNDER = Environment(
    "REQUIRED_LOCATION_LEVEL_PLUNDER", default_value="10"
)

# Whitelist of chat ids from which to forward messages. Default: Self Bot, OPMA Bot
WHITELIST_FORWARD_MESSAGE = Environment(
    "WHITELIST_FORWARD_MESSAGE",
    default_value=(BOT_ID.get() + c.STANDARD_SPLIT_CHAR + OPMA_BOT_ID.get()),
)
# Whitelist of bot ids which users can use inline mode. Default: Empty
WHITELIST_INLINE_BOTS = Environment("WHITELIST_INLINE_BOTS", default_value="")

# Price to create a crew. Default: 100,000,000
CREW_CREATE_PRICE = Environment("CREW_CREATE_PRICE", default_value="100000000")
# Maximum length of Crew name. Default: 50
CREW_NAME_MAX_LENGTH = Environment("CREW_MAX_NAME_LENGTH", default_value="50")
# Maximum length of Crew description. Default 200
CREW_DESCRIPTION_MAX_LENGTH = Environment("CREW_DESCRIPTION_MAX_LENGTH", default_value="200")
# Default maximum number of Crew members. Default: 10
CREW_MAX_MEMBERS = Environment("CREW_MAX_MEMBERS", default_value="10")
# How much percent should be removed from taxes for exchanges between Crew members. Default: 50%
CREW_TRANSACTION_TAX_DISCOUNT = Environment("CREW_TRANSACTION_TAX_DISCOUNT", default_value="50")
# Base price for Crew Powerups. Default: 100.000.000
CREW_POWERUP_BASE_PRICE = Environment("CREW_POWERUP_BASE_PRICE", default_value="100000000")
# How long a crew ability should last in days. Default: 7
CREW_ABILITY_DURATION_DAYS = Environment("CREW_ABILITY_DURATION_DAYS", default_value="7")
# Default value percentage for crew ability. Default: 50%
CREW_ABILITY_DEFAULT_VALUE_PERCENTAGE = Environment(
    "CREW_ABILITY_DEFAULT_VALUE_PERCENTAGE", default_value="50"
)
# Default maximum number of crew abilities. Default: 1
CREW_MAX_ABILITIES = Environment("CREW_MAX_ABILITIES", default_value="1")
# Minimum value percentage for crew random ability. Default: 1%
CREW_ABILITY_RANDOM_MIN_VALUE_PERCENTAGE = Environment(
    "CREW_ABILITY_RANDOM_MIN_VALUE_PERCENTAGE", default_value="1"
)
# Maximum value percentage for crew random ability. Default: 99%
CREW_ABILITY_RANDOM_MAX_VALUE_PERCENTAGE = Environment(
    "CREW_ABILITY_RANDOM_MAX_VALUE_PERCENTAGE", default_value="99"
)
# Maximum allowed level after level reset. Default: 5
CREW_MAX_LEVEL_AFTER_RESET = Environment("CREW_MAX_LEVEL_AFTER_RESET", default_value="5")
# How many Crews a user can request to join every n hours. Default: 3
CREW_JOIN_REQUESTS_PER_COOLDOWN = Environment("CREW_JOIN_REQUESTS_PER_COOLDOWN", default_value="3")
# How long a user has to wait before requesting to join another Crew in hours. Default: 24
CREW_JOIN_REQUEST_COOLDOWN_DURATION = Environment(
    "CREW_JOIN_REQUEST_COOLDOWN_DURATION", default_value="24"
)
# How long a user has to wait before requesting to join the same Crew again in days. Default: 7
CREW_JOIN_REQUEST_COOLDOWN_SAME_CREW_DURATION = Environment(
    "CREW_JOIN_REQUEST_COOLDOWN_SAME_CREW_DURATION", default_value="7"
)
# After long in minutes before a Davy Back Fight request expire. Default: 15 minutes
DAVY_BACK_FIGHT_REQUEST_EXPIRATION_TIME = Environment(
    "DAVY_BACK_FIGHT_REQUEST_EXPIRATION_TIME", default_value="15"
)
# How long in minutes after opponent confirmation will the Davy Back Fight start.
# Default: 15 minutes
DAVY_BACK_FIGHT_START_WAIT_TIME = Environment(
    "DAVY_BACK_FIGHT_START_WAIT_TIME", default_value="15"
)
# How long before bounty reset can a DBF be initiated in hours. Default: 48 hours
DAVY_BACK_FIGHT_BOUNTY_RESET_COOLDOWN_DURATION = Environment(
    "DAVY_BACK_FIGHT_BOUNTY_RESET_COOLDOWN_DURATION", default_value="48"
)
# Minimum number of members required to start a DBF. Default: 3
DAVY_BACK_FIGHT_MIN_PARTICIPANTS = Environment(
    "DAVY_BACK_FIGHT_MIN_PARTICIPANTS", default_value="3"
)
# Minimum duration of DBF in hours. Default: 1
DAVY_BACK_FIGHT_MIN_DURATION = Environment("DAVY_BACK_FIGHT_MIN_DURATION", default_value="1")
# Maximum duration of DBF in hours. Default: 48
DAVY_BACK_FIGHT_MAX_DURATION = Environment("DAVY_BACK_FIGHT_MAX_DURATION", default_value="48")
# Default duration of DBF in hours. Default: 24
DAVY_BACK_FIGHT_DEFAULT_DURATION = Environment(
    "DAVY_BACK_FIGHT_DEFAULT_DURATION", default_value="24"
)
# Minimum penalty period for losing a DBF in days. Default: 0
DAVY_BACK_FIGHT_MIN_LOSE_PENALTY_DURATION = Environment(
    "DAVY_BACK_FIGHT_MIN_LOSE_PENALTY_DURATION", default_value="0"
)
# Maximum penalty period for losing a DBF in days. Default: 7
DAVY_BACK_FIGHT_MAX_LOSE_PENALTY_DURATION = Environment(
    "DAVY_BACK_FIGHT_MAX_LOSE_PENALTY_DURATION", default_value="7"
)
# How much percent of Crew chest should be taken from the loser after a DBF. Default: 50%
DAVY_BACK_FIGHT_LOSER_CHEST_PERCENTAGE = Environment(
    "DAVY_BACK_FIGHT_LOSER_CHEST_PERCENTAGE", default_value="50"
)

# Minimum amount for Bounty Gift. Default: 10.000.000
BOUNTY_GIFT_MIN_AMOUNT = Environment("BOUNTY_GIFT_MIN_AMOUNT", default_value="10000000")
# Tax percentage increase after each Bounty Gift. Default: 1%
BOUNTY_GIFT_TAX_INCREASE = Environment("BOUNTY_GIFT_TAX_INCREASE", default_value="1")

# Minimum amount for Bounty Loan. Default: 10.000.000
BOUNTY_LOAN_MIN_AMOUNT = Environment("BOUNTY_LOAN_MIN_AMOUNT", default_value="10000000")
# Tax percentage increase after each Bounty Loan. Default: 1%
BOUNTY_LOAN_TAX_INCREASE = Environment("BOUNTY_LOAN_TAX_INCREASE", default_value="1")
# How many percent of newly gained bounty should be used to pay off loan in case of expiration.
# Default: 50%
BOUNTY_LOAN_GARNISH_PERCENTAGE = Environment("BOUNTY_LOAN_GARNISH_PERCENTAGE", default_value="50")
# Maximum duration of a loan in days. Default: 7
BOUNTY_LOAN_MAX_DURATION_DAYS = Environment("BOUNTY_LOAN_MAX_DURATION_DAYS", default_value="7")
# After how many days since expiration should a loan be forgiven if at least double the amount has
# been paid back.
# Default: 7
BOUNTY_LOAN_FORGIVENESS_DAYS = Environment("BOUNTY_LOAN_FORGIVENESS_DAYS", default_value="7")
# How long a user has to wait before issuing a new loan in hours. Default: 24
BOUNTY_LOAN_ISSUE_COOLDOWN_DURATION = Environment(
    "BOUNTY_LOAN_ISSUE_COOLDOWN_DURATION", default_value="24"
)
# How much interest on the loan before it is considered predatory. Default: 100%
BOUNTY_LOAN_PREDATORY_INTEREST_THRESHOLD = Environment(
    "BOUNTY_LOAN_PREDATORY_INTEREST_THRESHOLD", default_value="100"
)
# How much percent should be removed from taxes for exchanges from Pirate King. Default: 50%
PIRATE_KING_TRANSACTION_TAX_DISCOUNT = Environment(
    "PIRATE_KING_TRANSACTION_TAX_DISCOUNT", default_value="50"
)

# How many days a user can hold a devil fruit before it expires. Default: 2
DEVIL_FRUIT_EXPIRATION_DAYS = Environment("DEVIL_FRUIT_EXPIRATION_DAYS", default_value="2")
# After how many hours does a Devil Fruit respawn. Default: 24
DEVIL_FRUIT_RESPAWN_HOURS = Environment("DEVIL_FRUIT_RESPAWN_HOURS", default_value="24")
# How many leaderboards back a user has to appear in at least once to maintain an eaten
# Devil Fruit. Default: 4
DEVIL_FRUIT_MAINTAIN_MIN_LATEST_LEADERBOARD_APPEARANCE = Environment(
    "DEVIL_FRUIT_MAINTAIN_MIN_LATEST_LEADERBOARD_APPEARANCE", default_value="4"
)
# How many active users are required for each Devil Fruit in circulation. Default: 20
DEVIL_FRUIT_MIN_ACTIVE_USERS_PER_DEVIL_FRUIT = Environment(
    "DEVIL_FRUIT_MIN_ACTIVE_USERS_PER_DEVIL_FRUIT", default_value="20"
)
# How many Regular Zoan Devil Fruits are should be in circulation for each Ancient Zoan
# Devil Fruit. Default: 5
DEVIL_FRUIT_REGULAR_ZOAN_TO_ANCIENT_ZOAN_RATIO = Environment(
    "DEVIL_FRUIT_REGULAR_ZOAN_TO_ANCIENT_ZOAN_RATIO", default_value="5"
)
# How long a user has to wait before trying to collect a Devil Fruit again in hours. Default: 1
DEVIL_FRUIT_COLLECT_COOLDOWN_DURATION = Environment(
    "DEVIL_FRUIT_COLLECT_COOLDOWN_DURATION", default_value="1"
)
# Maximum days a SMILE lasts. Default: 14
DEVIL_FRUIT_SMILE_MAX_DAYS = Environment("DEVIL_FRUIT_SMILE_MAX_DAYS", default_value="14")
# Probability of getting a defective SMILE. Default: 10%
DEVIL_FRUIT_SMILE_DEFECTIVE_PERCENTAGE = Environment(
    "DEVIL_FRUIT_SMILE_DEFECTIVE_PERCENTAGE", default_value="10"
)

# If rookies or arrested users can view their status in groups. Default: True
ROOKIES_OR_ARRESTED_CAN_VIEW_STATUS_IN_GROUP = Environment(
    "ROOKIES_OR_ARRESTED_CAN_VIEW_STATUS_IN_GROUP", default_value="True"
)

# Tax brackets
# Level 0 total bounty. Default: 0
TAX_BRACKET_0_TOTAL_BOUNTY = Environment("TAX_BRACKET_0_TOTAL_BOUNTY", default_value="0")
# Level 0 percentage. Default: 0%
TAX_BRACKET_0_PERCENTAGE = Environment("TAX_BRACKET_0_PERCENTAGE", default_value="0")
# Level 1 total bounty. Default: 400mil
TAX_BRACKET_1_TOTAL_BOUNTY = Environment("TAX_BRACKET_1_TOTAL_BOUNTY", default_value="400000000")
# Level 1 percentage. Default: 5%
TAX_BRACKET_1_PERCENTAGE = Environment("TAX_BRACKET_1_PERCENTAGE", default_value="5")
# Level 2 total bounty. Default: 1bil
TAX_BRACKET_2_TOTAL_BOUNTY = Environment("TAX_BRACKET_2_TOTAL_BOUNTY", default_value="1000000000")
# Level 2 percentage. Default: 10%
TAX_BRACKET_2_PERCENTAGE = Environment("TAX_BRACKET_2_PERCENTAGE", default_value="10")
# Level 3 total bounty. Default: 2bil
TAX_BRACKET_3_TOTAL_BOUNTY = Environment("TAX_BRACKET_3_TOTAL_BOUNTY", default_value="2000000000")
# Level 3 percentage. Default: 20%
TAX_BRACKET_3_PERCENTAGE = Environment("TAX_BRACKET_3_PERCENTAGE", default_value="20")
# Level 4 total bounty. Default: 3bil
TAX_BRACKET_4_TOTAL_BOUNTY = Environment("TAX_BRACKET_4_TOTAL_BOUNTY", default_value="3000000000")
# Level 4 percentage. Default: 30%
TAX_BRACKET_4_PERCENTAGE = Environment("TAX_BRACKET_4_PERCENTAGE", default_value="30")
# Level 5 total bounty. Default: 4bil
TAX_BRACKET_5_TOTAL_BOUNTY = Environment("TAX_BRACKET_5_TOTAL_BOUNTY", default_value="4000000000")
# Level 5 percentage. Default: 40%
TAX_BRACKET_5_PERCENTAGE = Environment("TAX_BRACKET_5_PERCENTAGE", default_value="40")
# Level 6 total bounty. Default: 5bil
TAX_BRACKET_6_TOTAL_BOUNTY = Environment("TAX_BRACKET_6_TOTAL_BOUNTY", default_value="5000000000")
# Level 6 percentage. Default: 50%
TAX_BRACKET_6_PERCENTAGE = Environment("TAX_BRACKET_6_PERCENTAGE", default_value="50")
# Level 7 total bounty. Default: 6bil
TAX_BRACKET_7_TOTAL_BOUNTY = Environment("TAX_BRACKET_7_TOTAL_BOUNTY", default_value="6000000000")
# Level 7 percentage. Default: 60%
TAX_BRACKET_7_PERCENTAGE = Environment("TAX_BRACKET_7_PERCENTAGE", default_value="60")
# Level 8 total bounty. Default: 7bil
TAX_BRACKET_8_TOTAL_BOUNTY = Environment("TAX_BRACKET_8_TOTAL_BOUNTY", default_value="7000000000")
# Level 8 percentage. Default: 70%
TAX_BRACKET_8_PERCENTAGE = Environment("TAX_BRACKET_8_PERCENTAGE", default_value="70")
# Level 9 total bounty. Default: 8bil
TAX_BRACKET_9_TOTAL_BOUNTY = Environment("TAX_BRACKET_9_TOTAL_BOUNTY", default_value="8000000000")
# Level 9 percentage. Default: 80%
TAX_BRACKET_9_PERCENTAGE = Environment("TAX_BRACKET_9_PERCENTAGE", default_value="80")
# Level 10 total bounty. Default: 9bil
TAX_BRACKET_10_TOTAL_BOUNTY = Environment(
    "TAX_BRACKET_10_TOTAL_BOUNTY", default_value="9000000000"
)
# Level 10 percentage. Default: 90%
TAX_BRACKET_10_PERCENTAGE = Environment("TAX_BRACKET_10_PERCENTAGE", default_value="90")
# Level 11 total bounty. Default: 10bil
TAX_BRACKET_11_TOTAL_BOUNTY = Environment(
    "TAX_BRACKET_11_TOTAL_BOUNTY", default_value="10000000000"
)
# Level 11 percentage. Default: 99%
TAX_BRACKET_11_PERCENTAGE = Environment("TAX_BRACKET_11_PERCENTAGE", default_value="99")
# What percentage of the tax should go to the crew chest. Default: 50%
TAX_CREW_CHEST_PERCENTAGE = Environment("TAX_CREW_CHEST_PERCENTAGE", default_value="50")

# Minimum inactive hours to take into consideration for plunder. Default: 1
PLUNDER_MIN_INACTIVE_HOURS = Environment("PLUNDER_MIN_INACTIVE_HOURS", default_value="1")
# Maximum inactive hours to take into consideration for plunder. Default: 80
PLUNDER_MAX_INACTIVE_HOURS = Environment("PLUNDER_MAX_INACTIVE_HOURS", default_value="80")
# How long plunder immunity lasts in hours. Default: 24 hours
PLUNDER_IMMUNITY_DURATION = Environment("PLUNDER_IMMUNITY_DURATION", default_value="24")
# How long a user has to wait before plundering another user in hours. Default: 12 hours
PLUNDER_COOLDOWN_DURATION = Environment("PLUNDER_COOLDOWN_DURATION", default_value="12")
# How much times bounty more does a user has to repay in case of failed plunder. Default: 2
PLUNDER_REPAY_MULTIPLIER = Environment("PLUNDER_REPAY_MULTIPLIER", default_value="2")

# How much is each remaining minute of the sentence for bail in Impel Down. Default: 100k
IMPEL_DOWN_BAIL_PER_MINUTE = Environment("IMPEL_DOWN_BAIL_PER_MINUTE", default_value="100000")

# Values in minute for auto delete. Default: 1|2|5|15|30|60|120|180|360
AUTO_DELETE_DURATION_VALUES = Environment(
    "AUTO_DELETE_DURATION_VALUES", default_value="1|2|5|15|30|60|120|180|360"
)
