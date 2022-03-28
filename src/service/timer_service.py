import logging

from apscheduler.triggers.cron import CronTrigger
from peewee import MySQLDatabase
from telegram.ext import CallbackContext, Dispatcher, Job

import resources.Environment as Env
from resources.Database import Database
from src.chat.group.screens.screen_doc_q_game import reset_playability as reset_doc_q_game
from src.chat.group.screens.screen_leaderboard import manage as send_leaderboard
from src.chat.group.screens.screen_reddit_post import manage as send_reddit_post
from src.model.enums.Timer import Timer, REDDIT_POST_TIMERS
from src.service.bounty_poster_service import reset_bounty_poster_limit
from src.service.bounty_service import add_region_bounty
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


def add_to_context(context: CallbackContext, timer: Timer, cron: str, job_context: str = None) -> Job:
    """
    Add a job to the context
    :param context: The context
    :param timer: The timer
    :param cron: The cron expression
    :param job_context: The job context
    :rtype: Job
    """
    job = context.job_queue.run_custom(
        callback=run_timers,
        job_kwargs={"trigger": CronTrigger.from_crontab(cron)},
        name=timer.value,
        context=job_context
    )
    logging.info(f'Next run of "{timer.value}" is {job.next_run_time}')
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
    for reddit_post_timer in REDDIT_POST_TIMERS:
        add_to_context(context, reddit_post_timer['name'], reddit_post_timer['cron'],
                       reddit_post_timer['subreddit'])

    # Temp folder cleanup timer
    add_to_context(context, Timer.TEMP_DIR_CLEANUP, Env.CRON_TEMP_DIR_CLEANUP.get())

    # Leaderboard timer
    add_to_context(context, Timer.TIMER_SEND_LEADERBOARD, Env.CRON_SEND_LEADERBOARD.get())

    # Reset Doc Q Game timer
    add_to_context(context, Timer.RESET_DOC_Q_GAME, Env.CRON_RESET_DOC_Q_GAME.get())

    # Reset bounty poster limit
    add_to_context(context, Timer.RESET_BOUNTY_POSTER_LIMIT, Env.CRON_RESET_BOUNTY_POSTER_LIMIT.get())

    # Reset can change region
    add_to_context(context, Timer.RESET_CAN_CHANGE_REGION, Env.CRON_RESET_CAN_CHANGE_REGION.get())

    # Increment bounty by region
    add_to_context(context, Timer.ADD_REGION_BOUNTY, Env.CRON_ADD_REGION_BOUNTY.get())


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
    timer: Timer = Timer(job.name)

    match timer:
        case Timer.REDDIT_POST_ONEPIECE | Timer.REDDIT_POST_MEMEPIECE:
            send_reddit_post(context)
        case Timer.TEMP_DIR_CLEANUP:
            cleanup_temp_dir()
        case Timer.TIMER_SEND_LEADERBOARD:
            send_leaderboard(context)
        case Timer.RESET_DOC_Q_GAME:
            reset_doc_q_game(context)
        case Timer.RESET_BOUNTY_POSTER_LIMIT:
            reset_bounty_poster_limit(context)
        case Timer.RESET_CAN_CHANGE_REGION:
            reset_can_change_region(context)
        case Timer.ADD_REGION_BOUNTY:
            add_region_bounty(context)
        case _:
            logging.error(f'Unknown timer {job.name}')

    return
