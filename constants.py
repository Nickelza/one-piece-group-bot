import os

ROOT_DIR = os.path.dirname(__file__)

REDDIT_USER_URL_PREFIX = "https://www.reddit.com/user/"
REDDIT_SUBREDDIT_URL_PREFIX = "https://www.reddit.com/r/"

TG_PARSE_MODE_MARKDOWN = "MarkdownV2"
TG_DEFAULT_PARSE_MODE = TG_PARSE_MODE_MARKDOWN
TG_DEFAULT_IMAGE_COMPRESSION_QUALITY = 80
TG_PROFILE_PHOTO_EXTENSION = "jpg"
TG_KEYBOARD_DATA_MAX_LEN = 64

TEMP_DIR = os.path.join(ROOT_DIR, "temp")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
ASSETS_IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
ASSETS_SAVED_MEDIA_DIR = os.path.join(ASSETS_IMAGES_DIR, "saved_media")
ASSETS_FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# Command
STANDARD_SPLIT_CHAR = "|"
COMMAND_PREFIX_ALIASES = ["/", ".", ",", "!"]

# Bounty poster
BOUNTY_POSTER_EXTENSION = "jpg"

# LIST
STANDARD_LIST_SIZE = 10
STANDARD_LIST_KEYBOARD_ROW_SIZE = 5
FEATURE_KEYBOARD_ROW_SIZE = 2
USER_KEYBOARD_ROW_SIZE = 2
MAX_LIMIT = 18446744073709551610  # Max unsigned bigint

STANDARD_DATE_FORMAT = "%Y-%m-%d"
STANDARD_DATE_TIME_FORMAT = "%Y-%m-%d %H:%M"

MAGNITUDE_AMOUNT_TO_NUMBER = {
    "k": 1000,
    "thousand": 1000,
    "kk": 1000000,
    "million": 1000000,
    "billion": 1000000000,
    "trillion": 1000000000000,
}

DURATION_UNIT_TO_SECONDS = {
    "seconds": 1,
    "minutes": 60,
    "hrs": 3600,
    "hours": 3600,
    "days": 86400,
    "weeks": 604800,
    "months": 2628000,
    "years": 31536000,
}

CURRENT_REQUESTS = {}
