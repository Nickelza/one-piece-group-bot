import os

ROOT_DIR = os.path.dirname(__file__)

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
TG_PROFILE_PHOTO_EXTENSION = 'jpg'

TEMP_DIR = os.path.join(ROOT_DIR, 'temp')

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

# Bounty poster
POSTER_EXTENSIION = 'jpg'
POSTER_ASSETS_PATH = os.path.join(ROOT_DIR, 'assets', 'bounty_poster')
POSTER_TEMPLATE_PATH = os.path.join(POSTER_ASSETS_PATH, 'image_components', 'template.png')
POSTER_NO_PHOTO_PATH = os.path.join(POSTER_ASSETS_PATH, 'image_components', 'no_photo.jpg')
POSTER_IMAGE_BOX_START_Y = 239
POSTER_IMAGE_BOX_H = 461
POSTER_NAME_FONT_SIZE = 150
POSTER_NAME_MAX_W = 595
POSTER_NAME_H = 109
POSTER_NAME_START_X = 95
POSTER_NAME_START_Y = 802
POSTER_NAME_END_Y = 911
POSTER_NAME_MAX_KERN = 65
POSTER_NAME_MAX_LENGTH = 16
POSTER_NAME_SPACE_SUB_MIN_LENGTH = 14
POSTER_NAME_SPACE_SUB_CHAR = '•'
POSTER_NAME_TEXTURE_PATH = os.path.join(POSTER_ASSETS_PATH, 'image_components', 'texture_name.jpg')
POSTER_NAME_FONT_PATH = os.path.join(POSTER_ASSETS_PATH, 'fonts', 'PlayfairDisplay-Bold.ttf')
POSTER_BERRY_FONT_SIZE = 57
POSTER_BERRY_MAX_W = 522
POSTER_BERRY_H = 35
POSTER_BERRY_START_X = 150
POSTER_BERRY_START_Y = 952
POSTER_BERRY_END_Y = 987
POSTER_BERRY_MAX_KERN = 40

POSTER_BERRY_TEXTURE_PATH = os.path.join(POSTER_ASSETS_PATH, 'image_components', 'texture_berry.jpg')
POSTER_BERRY_FONT_PATH = os.path.join(POSTER_ASSETS_PATH, 'fonts', 'Handpower.ttf')
POSTER_COMPONENT_NAME = 1
POSTER_COMPONENT_BERRY = 2
