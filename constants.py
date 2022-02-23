import os

# Environment variables
ENV_TOKEN = 'TOKEN'
# Chat ID's
ENV_OPD_GROUP_ID = 'OPD_GROUP_ID'
# Database
ENV_DB_NAME = 'DB_NAME'
ENV_DB_HOST = 'DB_HOST'
ENV_DB_PORT = 'DB_PORT'
ENV_DB_USER = 'DB_USER'
ENV_DB_PASSWORD = 'DB_PASSWORD'

ENV_REDDIT_CLIENT_ID = 'REDDIT_CLIENT_ID'
ENV_REDDIT_CLIENT_SECRET = 'REDDIT_CLIENT_SECRET'
ENV_REDDIT_USER_AGENT = 'REDDIT_USER_AGENT'

ENV_TEMP_DIR_CLEANUP_TIME_SECONDS = 'TEMP_DIR_CLEANUP_TIME_SECONDS'
ENV_CRON_TEMP_DIR_CLEANUP = 'CRON_TEMP_DIR_CLEANUP'

TIMER_TEMP_DIR_CLEANUP_NAME = 'cleanup_temp_folder'
TIMER_REDDIT_POST_ONEPIECE_NAME = 'timer_reddit_post_onepiece'
TIMER_REDDIT_POST_MEMEPIECE_NAME = 'timer_reddit_post_memepiece'

# Timers
REDDIT_POST_TIMERS = [
    {
        'name': TIMER_REDDIT_POST_ONEPIECE_NAME,
        'cron': '0 0,12 * * *',  # every day at 00:00 and 12:00
        'subreddit': 'onepiece'
    },
    {
        'name': TIMER_REDDIT_POST_MEMEPIECE_NAME,
        'cron': '0 6,18 * * *',  # every day at 06:00 and 18:00
        'subreddit': 'memepiece'
    },
]

REDDIT_USER_URL_PREFIX = 'https://www.reddit.com/user/'
REDDIT_SUBREDDIT_URL_PREFIX = 'https://www.reddit.com/r/'

TG_DEFAULT_PARSE_MODE = 'MarkdownV2'
TG_MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
TG_DEFAULT_IMAGE_COMPRESSION_QUALITY = 80

TEMP_DIR = os.path.join(os.path.dirname(__file__), 'temp')
