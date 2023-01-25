import os
from distutils.util import strtobool

import sys
from dotenv import load_dotenv

import constants as c


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
        return True if strtobool(self.get()) else False

    def get_list(self) -> list[str]:
        """
        Get the environment variable as a list
        :return: The environment variable as a list
        """
        return self.get().split(c.STANDARD_SPLIT_CHAR)


load_dotenv(sys.argv[1])

# Bot
BOT_TOKEN = Environment('BOT_TOKEN')
BOT_DROP_PENDING_UPDATES = Environment('BOT_DROP_PENDING_UPDATES', default_value='False')
BOT_ID = Environment('BOT_ID')
BOT_USERNAME = Environment('BOT_USERNAME')

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
# Limit interaction to authorized users
LIMIT_TO_AUTHORIZED_USERS = Environment('LIMIT_TO_AUTHORIZED_USERS', default_value='False')
# List of authorized users
AUTHORIZED_USERS = Environment('AUTHORIZED_USERS', default_value='')
# Group chat id
OPD_GROUP_ID = Environment('OPD_GROUP_ID')
# Group chat username
OPD_GROUP_USERNAME = Environment('OPD_GROUP_USERNAME')
# Main channel id
OPD_CHANNEL_ID = Environment('OPD_CHANNEL_ID')
# ChatID for admin commands
ADMIN_GROUP_ID = Environment('ADMIN_GROUP_ID')
# OPMA bot id
OPMA_BOT_ID = Environment('OPMA_BOT_ID', default_value='921260484')

# TgRest Channel ID
TG_REST_CHANNEL_ID = Environment('TG_REST_CHANNEL_ID')

# REDDIT
# Reddit client id
REDDIT_CLIENT_ID = Environment('REDDIT_CLIENT_ID')
# Reddit client secret
REDDIT_CLIENT_SECRET = Environment('REDDIT_CLIENT_SECRET')
# Reddit username
REDDIT_USER_AGENT = Environment('REDDIT_USER_AGENT')
# Reddit One Piece Subreddit
REDDIT_ONE_PIECE_SUBREDDIT = Environment('REDDIT_ONE_PIECE_SUBREDDIT', default_value='onepiece')
# Reddit Meme Piece Subreddit
REDDIT_MEME_PIECE_SUBREDDIT = Environment('REDDIT_MEME_PIECE_SUBREDDIT', default_value='memepiece')

# TIMERS
# Check for files to clean up. Default: 12 hours
CRON_TEMP_DIR_CLEANUP = Environment('CRON_TEMP_DIR_CLEANUP', default_value='0 */12 * * *')
ENABLE_TIMER_TEMP_DIR_CLEANUP = Environment('ENABLE_TIMER_TEMP_DIR_CLEANUP', default_value='True')
SHOULD_LOG_TIMER_TEMP_DIR_CLEANUP = Environment('SHOULD_LOG_TIMER_TEMP_DIR_CLEANUP', default_value='False')
SHOULD_RUN_ON_STARTUP_TEMP_DIR_CLEANUP = Environment('SHOULD_RUN_ON_STARTUP_TEMP_DIR_CLEANUP', default_value='False')

# Create and send the leaderboard. Default: Every sunday at midnight
CRON_SEND_LEADERBOARD = Environment('CRON_SEND_LEADERBOARD', default_value='0 0 * * Sun')
ENABLE_TIMER_SEND_LEADERBOARD = Environment('ENABLE_TIMER_SEND_LEADERBOARD', default_value='True')
SHOULD_LOG_TIMER_SEND_LEADERBOARD = Environment('SHOULD_LOG_TIMER_SEND_LEADERBOARD', default_value='False')
SHOULD_RUN_ON_STARTUP_SEND_LEADERBOARD = Environment('SHOULD_RUN_ON_STARTUP_SEND_LEADERBOARD', default_value='False')

# Reset bounty poster limit. Default: Every day at 00:10
CRON_RESET_BOUNTY_POSTER_LIMIT = Environment('CRON_RESET_BOUNTY_POSTER_LIMIT', default_value='10 0 * * *')
ENABLE_TIMER_RESET_BOUNTY_POSTER_LIMIT = Environment('ENABLE_TIMER_RESET_BOUNTY_POSTER_LIMIT', default_value='True')
SHOULD_LOG_TIMER_RESET_BOUNTY_POSTER_LIMIT = Environment('SHOULD_LOG_TIMER_RESET_BOUNTY_POSTER_LIMIT',
                                                         default_value='False')
SHOULD_RUN_ON_STARTUP_RESET_BOUNTY_POSTER_LIMIT = Environment('SHOULD_RUN_ON_STARTUP_RESET_BOUNTY_POSTER_LIMIT',
                                                              default_value='False')

# Reset can change region. Default: Every sunday at midnight
CRON_RESET_CAN_CHANGE_REGION = Environment('CRON_RESET_CAN_CHANGE_REGION', default_value='0 0 * * Sun')
ENABLE_TIMER_RESET_CAN_CHANGE_REGION = Environment('ENABLE_TIMER_RESET_CAN_CHANGE_REGION', default_value='True')
SHOULD_LOG_TIMER_RESET_CAN_CHANGE_REGION = Environment('SHOULD_LOG_TIMER_RESET_CAN_CHANGE_REGION',
                                                       default_value='False')
SHOULD_RUN_ON_STARTUP_RESET_CAN_CHANGE_REGION = Environment('SHOULD_RUN_ON_STARTUP_RESET_CAN_CHANGE_REGION',
                                                            default_value='False')

# Bounty bonus for users in region. Default: Every day at 00:10
CRON_ADD_REGION_BOUNTY_BONUS = Environment('CRON_ADD_REGION_BOUNTY_BONUS', default_value='10 0 * * *')
ENABLE_TIMER_ADD_REGION_BOUNTY_BONUS = Environment('ENABLE_TIMER_ADD_REGION_BOUNTY_BONUS', default_value='True')
SHOULD_LOG_TIMER_ADD_REGION_BOUNTY_BONUS = Environment('SHOULD_LOG_TIMER_ADD_REGION_BOUNTY_BONUS',
                                                       default_value='False')
SHOULD_RUN_ON_STARTUP_ADD_REGION_BOUNTY_BONUS = Environment('SHOULD_RUN_ON_STARTUP_ADD_REGION_BOUNTY_BONUS',
                                                            default_value='False')
# Bounty bonus for Crew members. Default: Every day at 00:10
CRON_ADD_CREW_BOUNTY_BONUS = Environment('CRON_ADD_CREW_BOUNTY_BONUS', default_value='10 0 * * *')
ENABLE_TIMER_ADD_CREW_BOUNTY_BONUS = Environment('ENABLE_TIMER_ADD_CREW_BOUNTY_BONUS', default_value='True')
SHOULD_LOG_TIMER_ADD_CREW_BOUNTY_BONUS = Environment('SHOULD_LOG_TIMER_ADD_CREW_BOUNTY_BONUS', default_value='False')
SHOULD_RUN_ON_STARTUP_ADD_CREW_BOUNTY_BONUS = Environment('SHOULD_RUN_ON_STARTUP_ADD_CREW_BOUNTY_BONUS',
                                                          default_value='False')
# Bounty bonus for Crew members with bounty higher than crew average. Default: Every day at 00:10
CRON_ADD_CREW_MVP_BOUNTY_BONUS = Environment('CRON_ADD_CREW_MVP_BOUNTY_BONUS', default_value='10 0 * * *')
ENABLE_TIMER_ADD_CREW_MVP_BOUNTY_BONUS = Environment('ENABLE_TIMER_ADD_CREW_MVP_BOUNTY_BONUS', default_value='True')
SHOULD_LOG_TIMER_ADD_CREW_MVP_BOUNTY_BONUS = Environment('SHOULD_LOG_TIMER_ADD_CREW_MVP_BOUNTY_BONUS',
                                                         default_value='False')
SHOULD_RUN_ON_STARTUP_ADD_CREW_MVP_BOUNTY_BONUS = Environment('SHOULD_RUN_ON_STARTUP_ADD_CREW_MVP_BOUNTY_BONUS',
                                                              default_value='False')

# Reddit post One Piece. Default: Every day at 00:00 and 12:00
CRON_REDDIT_POST_ONE_PIECE = Environment('CRON_REDDIT_POST_ONE_PIECE', default_value='0 0,12 * * *')
ENABLE_TIMER_REDDIT_POST_ONE_PIECE = Environment('ENABLE_TIMER_REDDIT_POST_ONE_PIECE', default_value='True')
SHOULD_LOG_TIMER_REDDIT_POST_ONE_PIECE = Environment('SHOULD_LOG_TIMER_REDDIT_POST_ONE_PIECE', default_value='False')
SHOULD_RUN_ON_STARTUP_REDDIT_POST_ONE_PIECE = Environment('SHOULD_RUN_ON_STARTUP_REDDIT_POST_ONE_PIECE',
                                                          default_value='False')
# Reddit Meme post Piece. Default: Every day at 06:00 and 18:00
CRON_REDDIT_POST_MEME_PIECE = Environment('CRON_REDDIT_POST_MEME_PIECE', default_value='0 6,18 * * *')
ENABLE_TIMER_REDDIT_POST_MEME_PIECE = Environment('ENABLE_TIMER_REDDIT_POST_MEME_PIECE', default_value='True')
SHOULD_LOG_TIMER_REDDIT_POST_MEME_PIECE = Environment('SHOULD_LOG_TIMER_REDDIT_POST_MEME_PIECE', default_value='False')
SHOULD_RUN_ON_STARTUP_REDDIT_POST_MEME_PIECE = Environment('SHOULD_RUN_ON_STARTUP_REDDIT_POST_MEME_PIECE',
                                                           default_value='False')

# Send scheduled predictions. Default: Every 1 minute
CRON_SEND_SCHEDULED_PREDICTIONS = Environment('CRON_SEND_SCHEDULED_PREDICTIONS', default_value='*/1 * * * *')
ENABLE_TIMER_SEND_SCHEDULED_PREDICTIONS = Environment('ENABLE_TIMER_SEND_SCHEDULED_PREDICTIONS', default_value='True')
SHOULD_LOG_TIMER_SEND_SCHEDULED_PREDICTIONS = Environment('SHOULD_LOG_TIMER_SEND_SCHEDULED_PREDICTIONS',
                                                          default_value='False')
SHOULD_RUN_ON_STARTUP_SEND_SCHEDULED_PREDICTIONS = Environment('SHOULD_RUN_ON_STARTUP_SEND_SCHEDULED_PREDICTIONS',
                                                               default_value='False')

# Close scheduled predictions. Default: Every 1 minute
CRON_CLOSE_SCHEDULED_PREDICTIONS = Environment('CRON_CLOSE_SCHEDULED_PREDICTIONS', default_value='*/1 * * * *')
ENABLE_TIMER_CLOSE_SCHEDULED_PREDICTIONS = Environment('ENABLE_TIMER_CLOSE_SCHEDULED_PREDICTIONS', default_value='True')
SHOULD_LOG_TIMER_CLOSE_SCHEDULED_PREDICTIONS = Environment('SHOULD_LOG_TIMER_CLOSE_SCHEDULED_PREDICTIONS',
                                                           default_value='False')
SHOULD_RUN_ON_STARTUP_CLOSE_SCHEDULED_PREDICTIONS = Environment('SHOULD_RUN_ON_STARTUP_CLOSE_SCHEDULED_PREDICTIONS',
                                                                default_value='False')

# Schedule Devil Fruit release. Default: Every sunday at midnight
CRON_SCHEDULE_DEVIL_FRUIT_RELEASE = Environment('CRON_SCHEDULE_DEVIL_FRUIT_RELEASE', default_value='0 0 * * Sun')
ENABLE_TIMER_SCHEDULE_DEVIL_FRUIT_RELEASE = Environment('ENABLE_TIMER_SCHEDULE_DEVIL_FRUIT_RELEASE',
                                                        default_value='True')
SHOULD_LOG_TIMER_SCHEDULE_DEVIL_FRUIT_RELEASE = Environment('SHOULD_LOG_TIMER_SCHEDULE_DEVIL_FRUIT_RELEASE',
                                                            default_value='False')
SHOULD_RUN_ON_STARTUP_SCHEDULE_DEVIL_FRUIT_RELEASE = Environment('SHOULD_RUN_ON_STARTUP_SCHEDULE_DEVIL_FRUIT_RELEASE',
                                                                 default_value='False')

# Release scheduled Devil Fruit. Default: Every 1 minute
CRON_RELEASE_SCHEDULED_DEVIL_FRUIT = Environment('CRON_RELEASE_SCHEDULED_DEVIL_FRUIT', default_value='*/1 * * * *')
ENABLE_TIMER_RELEASE_SCHEDULED_DEVIL_FRUIT = Environment('ENABLE_TIMER_RELEASE_SCHEDULED_DEVIL_FRUIT',
                                                         default_value='True')
SHOULD_LOG_TIMER_RELEASE_SCHEDULED_DEVIL_FRUIT = Environment('SHOULD_LOG_TIMER_RELEASE_SCHEDULED_DEVIL_FRUIT',
                                                             default_value='False')
SHOULD_RUN_ON_STARTUP_RELEASE_SCHEDULED_DEVIL_FRUIT = Environment('SHOULD_RUN_ON_STARTUP_RELEASE_SCHEDULED_DEVIL_FRUIT',
                                                                  default_value='False')

# Respawn Devil Fruit. Default: Every 1 minute
CRON_RESPAWN_DEVIL_FRUIT = Environment('CRON_RESPAWN_DEVIL_FRUIT', default_value='*/1 * * * *')
ENABLE_TIMER_RESPAWN_DEVIL_FRUIT = Environment('ENABLE_TIMER_RESPAWN_DEVIL_FRUIT', default_value='True')
SHOULD_LOG_TIMER_RESPAWN_DEVIL_FRUIT = Environment('SHOULD_LOG_TIMER_RESPAWN_DEVIL_FRUIT', default_value='False')
SHOULD_RUN_ON_STARTUP_RESPAWN_DEVIL_FRUIT = Environment('SHOULD_RUN_ON_STARTUP_RESPAWN_DEVIL_FRUIT',
                                                        default_value='False')

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
# How much should belly be upper rounded. Default: 1000
BELLY_UPPER_ROUND_AMOUNT = Environment('BELLY_UPPER_ROUND_AMOUNT', default_value='1000')

# BOUNTY BONUS
# LOCATION
# Percentage that bounty is incremented by on timer for Paradise. Default: 0
PARADISE_BOUNTY_BONUS = Environment('PARADISE_BOUNTY_BONUS', default_value='0')
# Percentage that bounty is incremented by on timer for New World. Default: -3
NEW_WORLD_BOUNTY_BONUS = Environment('NEW_WORLD_BOUNTY_BONUS', default_value='-3')
# Percentage that bounty is incremented by on timer for Crew members. Default: 2
CREW_BOUNTY_BONUS = Environment('CREW_BOUNTY_BONUS', default_value='2')
# Percentage that bounty is incremented by on timer for Crew members with bounty higher than crew average. Default: 1
CREW_MVP_BOUNTY_BONUS = Environment('CREW_MVP_BOUNTY_BONUS', default_value='1')

# BOUNTY POSTER
# How many times Pirate King can display bounty poster before it is reset. Default: 0 (is boss)
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
# How many options should be shown in the Doc Q game if on final location. Default: 10
DOC_Q_GAME_OPTIONS_COUNT_FINAL_LOCATION = Environment('DOC_Q_GAME_OPTIONS_COUNT_FINAL_LOCATION', default_value='10')
# Chance of winning the game if on final location. Default: 0.1
DOC_Q_GAME_WIN_ODD_FINAL_LOCATION = Environment('DOC_Q_GAME_WIN_ODD_FINAL_LOCATION', default_value='0.1')
# Show correct option. Default: False
DOC_Q_GAME_SHOW_CORRECT_OPTION = Environment('DOC_Q_GAME_SHOW_CORRECT_OPTION', default_value='False')
# How long a user has to wait before playing the game again in hours. Default: 24
DOC_Q_GAME_COOLDOWN_DURATION = Environment('DOC_Q_GAME_COOLDOWN_DURATION', default_value='24')

# Minimum wager for games. Default: 10 million
GAME_MIN_WAGER = Environment('GAME_MIN_WAGER', default_value='10000000')
# After how much time in seconds without action should a user be notified about their turn. Default: 60 seconds
GAME_TURN_NOTIFICATION_TIME = Environment('GAME_TURN_NOTIFICATION_TIME', default_value='60')
# Game cooldown duration in hours. Default: 8
GAME_COOLDOWN_DURATION = Environment('GAME_COOLDOWN_DURATION', default_value='8')
# Show bullet location. Default: False
RUSSIAN_ROULETTE_SHOW_BULLET_LOCATION = Environment('RUSSIAN_ROULETTE_SHOW_BULLET_LOCATION', default_value='False')

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
LOCATION_EGGHEAD_IMAGE_URL = Environment('LOCATION_EGGHEAD_IMAGE_URL',
                                         default_value='https://i.imgur.com/mPsUp7x.jpeg')

# How long fight immunity lasts in hours. Default: 24 hours
FIGHT_IMMUNITY_DURATION = Environment('FIGHT_IMMUNITY_DURATION', default_value='24')
# How long a user has to wait before fighting another user in hours. Default: 1 hour
FIGHT_COOLDOWN_DURATION = Environment('FIGHT_COOLDOWN_DURATION', default_value='1')
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
# Maximum win probability when on final location. Default: 50%
FIGHT_MAX_WIN_PROBABILITY_FINAL_LOCATION = Environment('FIGHT_MAX_WIN_PROBABILITY_FINAL_LOCATION', default_value='50')
# Maximum win probability when on Devil Fruit defense boost. Default: 99%
FIGHT_MAX_WIN_PROBABILITY_DEVIL_FRUIT_DEFENSE_BOOST = Environment('FIGHT_MAX_WIN_PROBABILITY_DEVIL_FRUIT_DEFENSE_BOOST',
                                                                  default_value='99')
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

# Minimum wager for prediction bets. Default: 10 million
PREDICTION_BET_MIN_WAGER = Environment('PREDICTION_BET_MIN_WAGER', default_value='10000000')

# Send leaderboard message. Default: True
SEND_MESSAGE_LEADERBOARD = Environment('SEND_MESSAGE_LEADERBOARD', default_value='True')
# Send location update message. Default: True
SEND_MESSAGE_LOCATION_UPDATE = Environment('SEND_MESSAGE_LOCATION_UPDATE', default_value='True')
# Send move to new world proposal message. Default: True
SEND_MESSAGE_MOVE_TO_NEW_WORLD_PROPOSAL = Environment('SEND_MESSAGE_MOVE_TO_NEW_WORLD_PROPOSAL', default_value='True')
# Send bounty reset message. Default: True
SEND_MESSAGE_BOUNTY_RESET = Environment('SEND_MESSAGE_BOUNTY_RESET', default_value='True')

# Required location to use DocQ. Default: 14 (Jaya)
REQUIRED_LOCATION_LEVEL_DOC_Q_GAME = Environment('REQUIRED_LOCATION_LEVEL_DOC_Q_GAME', default_value='14')
# Required location to send stickers. Default: 10 (Whiskey Peak)
REQUIRED_LOCATION_LEVEL_SEND_STICKER = Environment('REQUIRED_LOCATION_LEVEL_SEND_STICKER', default_value='10')
# Required location to send animations. Default: 10 (Whiskey Peak)
REQUIRED_LOCATION_LEVEL_SEND_ANIMATION = Environment('REQUIRED_LOCATION_LEVEL_SEND_ANIMATION', default_value='10')
# Required location to forward messages. Default: 10 (Whiskey Peak)
REQUIRED_LOCATION_LEVEL_FORWARD_MESSAGE = Environment('REQUIRED_LOCATION_LEVEL_FORWARD_MESSAGE', default_value='10')
# Required location to send dice emoji. Default: 21 (Fishman Island)
REQUIRED_LOCATION_LEVEL_SEND_DICE_EMOJI = Environment('REQUIRED_LOCATION_LEVEL_SEND_DICE_EMOJI', default_value='21')
# Required location to use inline bots. Default: 21 (Fishman Island)
REQUIRED_LOCATION_LEVEL_USE_INLINE_BOTS = Environment('REQUIRED_LOCATION_LEVEL_USE_INLINE_BOTS', default_value='21')
# Required location to fight. Default: 21 (Fishman Island)
REQUIRED_LOCATION_LEVEL_FIGHT = Environment('REQUIRED_LOCATION_LEVEL_FIGHT', default_value='21')
# Required location to play games. Default: 21 (Fishman Island)
REQUIRED_LOCATION_LEVEL_GAME = Environment('REQUIRED_LOCATION_LEVEL_GAME', default_value='21')
# Required location to bet on predictions. Default: 21 (Fishman Island)
REQUIRED_LOCATION_LEVEL_PREDICTION_BET = Environment('REQUIRED_LOCATION_LEVEL_PREDICTION_BET', default_value='21')
# Required location to collect Devil Fruit. Default: 10 (Whiskey Peak)
REQUIRED_LOCATION_LEVEL_DEVIL_FRUIT_COLLECT = Environment('REQUIRED_LOCATION_LEVEL_DEVIL_FRUIT_COLLECT',
                                                          default_value='10')

# Whitelist of chat ids from which to forward messages. Default: Main Channel, Self Bot, OPMA Bot
WHITELIST_FORWARD_MESSAGE = Environment('WHITELIST_FORWARD_MESSAGE', default_value=(
        OPD_CHANNEL_ID.get() + c.STANDARD_SPLIT_CHAR
        + BOT_ID.get() + c.STANDARD_SPLIT_CHAR
        + OPMA_BOT_ID.get()
))
# Whitelist of bot ids which users can use inline mode. Default: Empty
WHITELIST_INLINE_BOTS = Environment('WHITELIST_INLINE_BOTS', default_value='')

# How many latest leaderboard user has to be in to be able to create a Crew. Default: 4
CREW_CREATE_MIN_LATEST_LEADERBOARD_APPEARANCE = Environment('CREW_CREATE_MIN_LATEST_LEADERBOARD_APPEARANCE',
                                                            default_value='4')
# Which rank user must have attained in the latest leaderboards to be able to create a Crew. Default: 2 (Emperor)
CREW_CREATE_MIN_LATEST_LEADERBOARD_RANK = Environment('CREW_CREATE_MIN_LATEST_LEADERBOARD_RANK', default_value='2')
# Which rank user must have attained in at least one of the latest leaderboards to be able to maintain a Crew.
# Default: 3 (First Mate)
CREW_MAINTAIN_MIN_LATEST_LEADERBOARD_RANK = Environment('CREW_MAINTAIN_MIN_LATEST_LEADERBOARD_RANK', default_value='3')
# Maximum length of Crew name. Default: 50
CREW_NAME_MAX_LENGTH = Environment('CREW_MAX_NAME_LENGTH', default_value='50')
# Maximum number of Crew members. Default: 10
CREW_MAX_MEMBERS = Environment('CREW_MAX_MEMBERS', default_value='10')

# Minimum amount for Bounty Gift. Default: 10.000.000
BOUNTY_GIFT_MIN_AMOUNT = Environment('BOUNTY_GIFT_MIN_AMOUNT', default_value='10000000')
# Tax percentage increase after each Bounty Gift. Default: 1%
BOUNTY_GIFT_TAX_INCREASE = Environment('BOUNTY_GIFT_TAX_INCREASE', default_value='1')

# How many days a user can hold a devil fruit before it expires. Default: 7
DEVIL_FRUIT_EXPIRATION_DAYS = Environment('DEVIL_FRUIT_EXPIRATION_DAYS', default_value='7')
# After how many hours does a Devil Fruit respawn. Default: 24
DEVIL_FRUIT_RESPAWN_HOURS = Environment('DEVIL_FRUIT_RESPAWN_HOURS', default_value='24')
