from enum import Enum


class Timer(Enum):
    TEMP_DIR_CLEANUP = 'cleanup_temp_folder'
    REDDIT_POST_ONEPIECE = 'reddit_post_onepiece'
    REDDIT_POST_MEMEPIECE = 'reddit_post_memepiece'
    TIMER_SEND_LEADERBOARD = 'send_leaderboard'
    RESET_BOUNTY = 'reset_bounty'
    RESET_BOUNTY_ALERT = 'reset_bounty_alert'
    RESET_DOC_Q_GAME = 'reset_doc_q_game'
    RESET_BOUNTY_POSTER_LIMIT = 'reset_bounty_poster_limit'
    RESET_CAN_CHANGE_REGION = 'reset_can_change_region'
    ADD_REGION_BOUNTY = 'add_region_bounty'


REDDIT_POST_TIMERS = [
    {
        'name': Timer.REDDIT_POST_ONEPIECE,
        'cron': '0 0,12 * * *',  # every day at 00:00 and 12:00
        'subreddit': 'onepiece'
    },
    {
        'name': Timer.REDDIT_POST_MEMEPIECE,
        'cron': '0 6,18 * * *',  # every day at 06:00 and 18:00
        'subreddit': 'memepiece'
    },
]
