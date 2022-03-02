import os

# Timers
TIMER_TEMP_DIR_CLEANUP_NAME = 'cleanup_temp_folder'
TIMER_REDDIT_POST_ONEPIECE_NAME = 'timer_reddit_post_onepiece'
TIMER_REDDIT_POST_MEMEPIECE_NAME = 'timer_reddit_post_memepiece'
TIMER_SEND_LEADERBOARD_NAME = 'timer_send_leaderboard'
TIMER_RESET_BOUNTY_NAME = 'timer_reset_bounty'
TIMER_RESET_BOUNTY_ALERT_NAME = 'timer_reset_bounty_alert'
TIMER_RESET_DOC_Q_GAME_NAME = 'timer_reset_doc_q_game'

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

TG_PARSE_MODE_MARKDOWN = 'MarkdownV2'
TG_DEFAULT_PARSE_MODE = TG_PARSE_MODE_MARKDOWN
TG_MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
TG_DEFAULT_IMAGE_COMPRESSION_QUALITY = 80

TEMP_DIR = os.path.join(os.path.dirname(__file__), 'temp')

# Language code
LANG_CODE_EN = 'en'
DEFAULT_LANG_CODE = LANG_CODE_EN

SCREEN_CODE = 'sc'

# Saved Media
SAVED_MEDIA_NAME_DOC_Q = 'docq'

# EMOJI
# Doc Q Game
EMOJI_DOC_Q_GAME_OPTIONS = '🍎'
EMOJI_DOC_Q_GAME_WIN = '🎉'
EMOJI_DOC_Q_GAME_LOSE = '💥'
# Other
EMOJI_CANCEL = '❌'

# Commands
COMMAND_PREFIX = '/'
COMMAND_PREFIX_ALIASES = ["/", ".", ", ", "!"]
COMMAND_PVT_START = 'start'
COMMAND_GRP_DOC_Q_GAME = 'docq'
COMMAND_GRP_BOUNTY = 'bounty'
COMMAND_ADM_SAVE_MEDIA = 'savemedia'
