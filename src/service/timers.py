import os

from apscheduler.triggers.cron import CronTrigger
from telegram.ext import CallbackContext, Dispatcher
from peewee import MySQLDatabase

import constants as const
from src.chat.group.screens.screen_send_reddit_post import manage as send_reddit_post
from src.service.dowload_service import cleanup_temp_dir
from resources.Database import Database


def init() -> MySQLDatabase:
    """
    Initializes the group chat manager
    :return: Database connection
    :rtype: MySQLDatabase
    """
    db_obj = Database()
    db = db_obj.get_db()

    return db


def end(db: MySQLDatabase) -> None:
    """
    Ends the group chat manager
    :param db: Database connection
    :type db: MySQLDatabase
    :return: None
    :rtype: None
    """
    db.close()


def set_timers(dispatcher: Dispatcher) -> None:
    """
    Set the timers
    :param dispatcher: The dispatcher
    :type dispatcher: Dispatcher
    :return: None
    :rtype: None
    """

    context = CallbackContext(dispatcher)

    # Reddit post timer
    for reddit_post_timer in const.REDDIT_POST_TIMERS:
        context.job_queue.run_custom(
            callback=run_timers,
            job_kwargs={"trigger": CronTrigger.from_crontab(reddit_post_timer['cron'])},
            name=reddit_post_timer['name'],
            context=reddit_post_timer['subreddit']
        )

    # Temp folder cleanup timer
    context.job_queue.run_custom(
        callback=run_timers,
        job_kwargs={"trigger": CronTrigger.from_crontab(os.environ[const.ENV_CRON_TEMP_DIR_CLEANUP])},
        name='cleanup_temp_folder'
    )


def run_timers(context: CallbackContext) -> None:
    """
    Run the timers
    :param context: The context
    :type context: CallbackContext
    :return: None
    :rtype: None
    """

    db = init()

    job = context.job

    # Reddit post timer
    if job.name == const.TIMER_REDDIT_POST_ONEPIECE_NAME or job.name == const.TIMER_REDDIT_POST_MEMEPIECE_NAME:
        send_reddit_post(context)
        end(db)
        return

    # Temp folder cleanup timer
    if job.name == const.TIMER_TEMP_DIR_CLEANUP_NAME:
        cleanup_temp_dir()
        end(db)
        return

