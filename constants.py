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

# Timers
REDDIT_POST_TIMERS = [
    {
        'name': 'reddit_post_timer_onepiece',
        'cron': '0 0,12 * * *',  # every day at 00:00 and 12:00
        'subreddit': 'onepiece'
    },
    {
        'name': 'reddit_post_timer_memepiece',
        'cron': '0 6,18 * * *',  # every day at 06:00 and 18:00
        'subreddit': 'memepiece'
    },
]

REDDIT_USER_URL_PREFIX = 'https://www.reddit.com/user/'
REDDIT_SUBREDDIT_URL_PREFIX = 'https://www.reddit.com/r/'

DEFAULT_PARSE_MODE = 'MarkdownV2'
