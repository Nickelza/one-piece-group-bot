import os
from distutils.util import strtobool


class Environment:
    def __init__(self, name: str, default_value: str = None, can_be_empty: bool = False):
        self.name = name
        self.default_value = default_value
        self.can_be_empty = can_be_empty

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

        # If the environment variable is not set and the environment variable can be empty, return None
        if value is None and self.can_be_empty:
            return None

        # If the environment variable is not set and the environment variable can not be empty, raise an exception
        if value is None:
            raise Exception(f"Environment variable {self.name} is not set")

        return value

    def get(self) -> str:
        """
        Get the environment variable
        :return: The environment variable
        """
        value = self.get_or_none()
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
# Log queries
DB_LOG_QUERIES = Environment('DB_LOG_QUERIES', default_value='False')

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
# Reset can change region. Default: Every sunday at midnight
CRON_RESET_CAN_CHANGE_REGION = Environment('CRON_RESET_CAN_CHANGE_REGION', default_value='0 0 * * Sun')
# Increment bounty for users in region. Default: Every day at 00:10
CRON_ADD_REGION_BOUNTY = Environment('CRON_INCREMENT_BOUNTY_FOR_REGION', default_value='10 0 * * *')

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
# Multiplier percentage for location level. Default 10
BELLY_LOCATION_LEVEL_MULTIPLIER = Environment('BELLY_LOCATION_LEVEL_MULTIPLIER', default_value='10')

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
DOC_Q_GAME_SHOW_CORRECT_OPTION = Environment('DOC_Q_GAME_SHOW_CORRECT_OPTION', default_value='False')

# LOCATION
# Percentage that bounty is incremented by on timer for Paradise. Default: 0
LOCATION_PARADISE_BOUNTY_INCREMENT = Environment('LOCATION_PARADISE_BOUNTY_INCREMENT', default_value='0')
# Percentage that bounty is incremented by on timer for New World. Default: 1
LOCATION_NEW_WORLD_BOUNTY_INCREMENT = Environment('LOCATION_NEW_WORLD_BOUNTY_INCREMENT', default_value='1')

LOCATION_PARADISE_IMAGE_URL = Environment('LOCATION_PARADISE_IMAGE_URL',
                                          default_value='https://i.imgur.com/omBDMbu.jpg')
LOCATION_NEW_WORLD_IMAGE_URL = Environment('LOCATION_NEW_WORLD_IMAGE_URL',
                                           default_value='https://i.imgur.com/J5EWet5.jpg')
LOCATION_FOOSHA_VILLAGE_IMAGE_URL = Environment('LOCATION_FOOSHA_VILLAGE_IMAGE_URL',
                                                default_value='https://i.imgur.com/v8W3lHy.png')
LOCATION_SHELLS_TOWN_IMAGE_URL = Environment('LOCATION_SHELLS_TOWN_IMAGE_URL',
                                             default_value='https://i.imgur.com/638z7dA.png')
LOCATION_ORANGE_TOWN_IMAGE_URL = Environment('LOCATION_ORANGE_TOWN_IMAGE_URL',
                                             default_value='https://i.imgur.com/2v2UAHc.png')
LOCATION_ISLAND_OF_RARE_ANIMALS_IMAGE_URL = Environment('LOCATION_ISLAND_OF_RARE_ANIMALS_IMAGE_URL',
                                                        default_value='https://i.imgur.com/S8ejYiJ.png')
LOCATION_SYRUP_VILLAGE_IMAGE_URL = Environment('LOCATION_SYRUP_VILLAGE_IMAGE_URL',
                                               default_value='https://imgur.com/klCUJHq.jpg')
LOCATION_BARATIE_IMAGE_URL = Environment('LOCATION_BARATIE_IMAGE_URL',
                                         default_value='https://i.imgur.com/41PA2tE.jpg')
LOCATION_ARLONG_PARK_IMAGE_URL = Environment('LOCATION_ARLONG_PARK_IMAGE_URL',
                                             default_value='https://i.imgur.com/6uAZaqn.jpg')
LOCATION_LOUGETOWN_IMAGE_URL = Environment('LOCATION_LOUGETOWN_IMAGE_URL',
                                           default_value='https://i.imgur.com/NfwXoAI.jpg')
LOCATION_REVERSE_MOUNTAIN_IMAGE_URL = Environment('LOCATION_REVERSE_MOUNTAIN_IMAGE_URL',
                                                  default_value='https://i.imgur.com/iamqwq8.png')
LOCATION_WHISKEY_PEAK_IMAGE_URL = Environment('LOCATION_WHISKEY_PEAK_IMAGE_URL',
                                              default_value='https://i.imgur.com/c5gfVLe.jpg')
LOCATION_LITTLE_GARDEN_IMAGE_URL = Environment('LOCATION_LITTLE_GARDEN_IMAGE_URL',
                                               default_value='https://i.imgur.com/ns5U5S6.png')
LOCATION_DRUM_ISLAND_IMAGE_URL = Environment('LOCATION_DRUM_ISLAND_IMAGE_URL',
                                             default_value='https://i.imgur.com/8lvNZbu.png')
LOCATION_ARABASTA_KINGDOM_IMAGE_URL = Environment('LOCATION_ARABASTA_KINGDOM_IMAGE_URL',
                                                  default_value='https://i.imgur.com/Cw9jqsJ.jpg')
LOCATION_JAYA_IMAGE_URL = Environment('LOCATION_JAYA_IMAGE_URL',
                                      default_value='https://i.imgur.com/e1NLOjT.png')
LOCATION_SKYPIEA_IMAGE_URL = Environment('LOCATION_SKYPIEA_IMAGE_URL',
                                         default_value='https://i.imgur.com/cfJ4o0Z.jpg')
LOCATION_LONG_RING_LONG_LAND_IMAGE_URL = Environment('LOCATION_LONG_RING_LONG_LAND_IMAGE_URL',
                                                     default_value='https://i.imgur.com/M1UZrls.png')
LOCATION_WATER_7_IMAGE_URL = Environment('LOCATION_WATER_7_IMAGE_URL',
                                         default_value='https://i.imgur.com/IqbkOAP.png')
LOCATION_ENIES_LOBBY_IMAGE_URL = Environment('LOCATION_ENIES_LOBBY_IMAGE_URL',
                                             default_value='https://i.imgur.com/56LeSDp.png')
LOCATION_THRILLER_BARK_IMAGE_URL = Environment('LOCATION_THRILLER_BARK_IMAGE_URL',
                                               default_value='https://i.imgur.com/vZpyTyU.png')
LOCATION_SABAODY_ARCHIPELAGO_IMAGE_URL = Environment('LOCATION_SABAODY_ARCHIPELAGO_IMAGE_URL',
                                                     default_value='https://i.imgur.com/DYssFxB.jpg')
LOCATION_FISHMAN_ISLAND_IMAGE_URL = Environment('LOCATION_FISHMAN_ISLAND_IMAGE_URL',
                                                default_value='https://i.imgur.com/kt7zEpu.jpg')
LOCATION_PUNK_HAZARD_IMAGE_URL = Environment('LOCATION_PUNK_HAZARD_IMAGE_URL',
                                             default_value='https://i.imgur.com/H5AszLU.png')
LOCATION_DRESSROSA_IMAGE_URL = Environment('LOCATION_DRESSROSA_IMAGE_URL',
                                           default_value='https://i.imgur.com/sGLRtpO.jpg')
LOCATION_ZOU_IMAGE_URL = Environment('LOCATION_ZOU_IMAGE_URL',
                                     default_value='https://i.imgur.com/UD2YCV4.jpg')
LOCATION_WHOLE_CAKE_ISLAND_IMAGE_URL = Environment('LOCATION_WHOLE_CAKE_ISLAND',
                                                   default_value='https://i.imgur.com/fEAM6eN.jpg')
LOCATION_WANO_COUNTRY_IMAGE_URL = Environment('LOCATION_WANO_COUNTRY_IMAGE_URL',
                                              default_value='https://i.imgur.com/vznQ3W2.jpg')

# How long fight immunity lasts. Default: 24 hours
FIGHT_IMMUNITY_DURATION = Environment('FIGHT_IMMUNITY_DURATION', default_value='24')
# Maximum win probability for Pirate King. Default: 99%
FIGHT_MAX_WIN_PROBABILITY_PIRATE_KING = Environment('FIGHT_MAX_WIN_PROBABILITY_PIRATE_KING', default_value='99')
# Maximum win probability for Emperor. Default: 95%
FIGHT_MAX_WIN_PROBABILITY_EMPEROR = Environment('FIGHT_MAX_WIN_PROBABILITY_EMPEROR', default_value='95')
# Maximum win probability for First Mate. Default: 90%
FIGHT_MAX_WIN_PROBABILITY_FIRST_MATE = Environment('FIGHT_MAX_WIN_PROBABILITY_FIRST_MATE', default_value='90')
# Maximum win probability for Supernova. Default: 85%
FIGHT_MAX_WIN_PROBABILITY_SUPERNOVA = Environment('FIGHT_MAX_WIN_PROBABILITY_SUPERNOVA', default_value='85')
# Maximum win probability for Rookie. Default: 80%
FIGHT_MAX_WIN_PROBABILITY_ROOKIE = Environment('FIGHT_MAX_WIN_PROBABILITY_ROOKIE', default_value='80')
# Minimum win probability for Pirate King. Default: 1%
FIGHT_MIN_WIN_PROBABILITY_PIRATE_KING = Environment('FIGHT_MIN_WIN_PROBABILITY_PIRATE_KING', default_value='1')
# Minimum win probability for Emperor. Default: 1%
FIGHT_MIN_WIN_PROBABILITY_EMPEROR = Environment('FIGHT_MIN_WIN_PROBABILITY_EMPEROR', default_value='1')
# Minimum win probability for First Mate. Default: 1%
FIGHT_MIN_WIN_PROBABILITY_FIRST_MATE = Environment('FIGHT_MIN_WIN_PROBABILITY_FIRST_MATE', default_value='1')
# Minimum win probability for Supernova. Default: 1%
FIGHT_MIN_WIN_PROBABILITY_SUPERNOVA = Environment('FIGHT_MIN_WIN_PROBABILITY_SUPERNOVA', default_value='1')
# Minimum win probability for Rookie. Default: 1%
FIGHT_MIN_WIN_PROBABILITY_ROOKIE = Environment('FIGHT_MIN_WIN_PROBABILITY_ROOKIE', default_value='1')
