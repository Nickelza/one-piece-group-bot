import os


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


# Bot
TOKEN = Environment('TOKEN')

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

# How much time should temp files be kept before they are deleted. Default: 6 hours
TEMP_DIR_CLEANUP_TIME_SECONDS = Environment('TEMP_DIR_CLEANUP_TIME_SECONDS', '21600')

# How many entries should be shown in the leaderboard. Default: 10
LEADERBOARD_LIMIT = Environment('LEADERBOARD_LIMIT', default_value='10')
