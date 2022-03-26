import logging

from apscheduler.triggers.cron import CronTrigger
from peewee import MySQLDatabase
from telegram.ext import CallbackContext, Dispatcher, Job

import constants as c
import resources.Environment as Env
from resources.Database import Database
from src.chat.group.screens.screen_doc_q_game import reset_playability as reset_doc_q_game
from src.chat.group.screens.screen_leaderboard import manage as send_leaderboard
from src.chat.group.screens.screen_reddit_post import manage as send_reddit_post
from src.service.bounty_poster_service import reset_bounty_poster_limit
from src.service.bounty_service import reset_bounty, reset_bounty_alert, add_region_bounty
from src.service.download_service import cleanup_temp_dir
from src.service.location_service import reset_can_change_region


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


def add_to_context(context: CallbackContext, name: str, cron: str, job_context: str = None) -> Job:
    """
    Add a job to the context
    :param context: The context
    :param name: The name of the job
    :param cron: The cron expression
    :param job_context: The job context
    :rtype: Job
    """
    job = context.job_queue.run_custom(
        callback=run_timers,
        job_kwargs={"trigger": CronTrigger.from_crontab(cron)},
        name=name,
        context=job_context
    )
    logging.info(f'Next run of "{name}" is {job.next_run_time}')
    return job


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
    for reddit_post_timer in c.REDDIT_POST_TIMERS:
        add_to_context(context, reddit_post_timer['name'], reddit_post_timer['cron'], reddit_post_timer['subreddit'])

    # Temp folder cleanup timer
    add_to_context(context, c.TIMER_TEMP_DIR_CLEANUP_NAME, Env.CRON_TEMP_DIR_CLEANUP.get())

    # Leaderboard timer
    add_to_context(context, c.TIMER_SEND_LEADERBOARD_NAME, Env.CRON_SEND_LEADERBOARD.get())

    # Reset bounty timer
    add_to_context(context, c.TIMER_RESET_BOUNTY_NAME, Env.CRON_RESET_BOUNTY.get())

    # Reset bounty alert timer
    add_to_context(context, c.TIMER_RESET_BOUNTY_ALERT_NAME, Env.CRON_RESET_BOUNTY_ALERT.get())

    # Reset Doc Q Game timer
    add_to_context(context, c.TIMER_RESET_DOC_Q_GAME_NAME, Env.CRON_RESET_DOC_Q_GAME.get())

    # Reset bounty poster limit
    add_to_context(context, c.TIMER_RESET_BOUNTY_POSTER_LIMIT_NAME, Env.CRON_RESET_BOUNTY_POSTER_LIMIT.get())

    # Reset can change region
    add_to_context(context, c.TIMER_RESET_CAN_CHANGE_REGION_NAME, Env.CRON_RESET_CAN_CHANGE_REGION.get())

    # Increment bounty by region
    add_to_context(context, c.TIMER_ADD_REGION_BOUNTY_NAME, Env.CRON_ADD_REGION_BOUNTY.get()).run(dispatcher)


def run_timers(context: CallbackContext) -> None:
    """
    Run the timers
    :param context: The context
    :return: None
    """

    db = init()
    logging.info(f'Running timer {context.job.name}')
    execute(context)
    logging.info(f'Finished timer {context.job.name}')
    end(db)


def execute(context: CallbackContext) -> None:
    """
    Run the timers
    :param context: The context
    :return: None
    """

    job = context.job

    # Reddit post timer
    if job.name == c.TIMER_REDDIT_POST_ONEPIECE_NAME or job.name == c.TIMER_REDDIT_POST_MEMEPIECE_NAME:
        send_reddit_post(context)
        return

    # Temp folder cleanup timer
    if job.name == c.TIMER_TEMP_DIR_CLEANUP_NAME:
        cleanup_temp_dir()
        return

    # Leaderboard timer
    if job.name == c.TIMER_SEND_LEADERBOARD_NAME:
        send_leaderboard(context)
        return

    # Reset bounty timer
    if job.name == c.TIMER_RESET_BOUNTY_NAME:
        reset_bounty(context)
        return

    # Reset bounty alert timer
    if job.name == c.TIMER_RESET_BOUNTY_ALERT_NAME:
        reset_bounty_alert(context)
        return

    # Reset Doc Q Game timer
    if job.name == c.TIMER_RESET_DOC_Q_GAME_NAME:
        reset_doc_q_game(context)
        return

    # Reset bounty poster limit
    if job.name == c.TIMER_RESET_BOUNTY_POSTER_LIMIT_NAME:
        reset_bounty_poster_limit(context)
        return

    # Reset can change region
    if job.name == c.TIMER_RESET_CAN_CHANGE_REGION_NAME:
        reset_can_change_region(context)
        return

    # Add region bounty
    if job.name == c.TIMER_ADD_REGION_BOUNTY_NAME:
        add_region_bounty(context)
        return
