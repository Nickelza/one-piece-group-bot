import os

ROOT_DIR = os.path.dirname(__file__)

REDDIT_USER_URL_PREFIX = 'https://www.reddit.com/user/'
REDDIT_SUBREDDIT_URL_PREFIX = 'https://www.reddit.com/r/'

TG_PARSE_MODE_MARKDOWN = 'MarkdownV2'
TG_DEFAULT_PARSE_MODE = TG_PARSE_MODE_MARKDOWN
TG_DEFAULT_IMAGE_COMPRESSION_QUALITY = 80
TG_PROFILE_PHOTO_EXTENSION = 'jpg'

TEMP_DIR = os.path.join(ROOT_DIR, 'temp')
ASSETS_DIR = os.path.join(ROOT_DIR, 'assets')
ASSETS_IMAGES_DIR = os.path.join(ASSETS_DIR, 'images')
ASSETS_SAVED_MEDIA_DIR = os.path.join(ASSETS_IMAGES_DIR, 'saved_media')
ASSETS_FONTS_DIR = os.path.join(ASSETS_DIR, 'fonts')

# Command
STANDARD_SPLIT_CHAR = "|"
COMMAND_PREFIX_ALIASES = ["/", ".", ",", "!"]

# Bounty poster
BOUNTY_POSTER_EXTENSION = 'jpg'

# LIST
STANDARD_LIST_SIZE = 10
STANDARD_LIST_KEYBOARD_ROW_SIZE = 5
FEATURE_KEYBOARD_ROW_SIZE = 2

STANDARD_DATE_FORMAT = '%Y-%m-%d'
STANDARD_DATE_TIME_FORMAT = '%Y-%m-%d %H:%M'

MAGNITUDE_AMOUNT_TO_NUMBER = {
    "k": 1000,
    "thousand": 1000,
    "kk": 1000000,
    "million": 1000000,
    "billion": 1000000000,
    "trillion": 1000000000000,
}
