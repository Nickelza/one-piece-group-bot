import logging

from apscheduler.triggers.cron import CronTrigger
from telegram.ext import ContextTypes, Application, Job

import src.model.enums.Timer as Timer
from src.chat.group.screens.screen_doc_q_game import reset_playability as reset_doc_q_game
from src.chat.group.screens.screen_leaderboard import manage as send_leaderboard
from src.chat.group.screens.screen_reddit_post import manage as send_reddit_post
from src.chat.manage_message import init, end
from src.service.bounty_poster_service import reset_bounty_poster_limit
from src.service.bounty_service import add_region_bounty_bonus, add_crew_bounty_bonus, add_crew_mvp_bounty_bonus
from src.service.download_service import cleanup_temp_dir
from src.service.game_service import reset_can_initiate_game
from src.service.location_service import reset_can_change_region
from src.service.prediction_service import send_scheduled_predictions, close_scheduled_predictions


def add_to_queue(application: Application, timer: Timer.Timer) -> Job:
    """
    Add a job to the context
    :param application: The application
    :param timer: The timer
    :rtype: Job
    """
    job = application.job_queue.run_custom(
        callback=run,
        job_kwargs={"trigger": CronTrigger.from_crontab(timer.cron_expression)},
        name=timer.name,
        data=timer
    )
    logging.info(f'Added timer "{timer.name}"')
    # logging.info(f'Next run of "{timer.name}" is {job.next_t}')  # FIXME Show next run time once it works
    return job


def set_timers(application: Application) -> None:
    """
    Set the timers
    :param application: The application
    :type application: Dispatcher
    :return: None
    :rtype: None
    """

    for timer in Timer.TIMERS:
        if timer.is_enabled:
            add_to_queue(application, timer)
        else:
            logging.info(f'Timer {timer.name} is disabled')


async def run(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Run the timers
    :param context: The context
    :return: None
    """

    job = context.job
    if not isinstance(job.data, Timer.Timer):
        logging.error(f'Job {job.name} context is not a Timer')
        return

    timer: Timer.Timer = job.data

    db = init()

    if timer.should_log:
        logging.info(f'Running timer {job.name}')

    match timer:
        case Timer.REDDIT_POST_ONE_PIECE | Timer.REDDIT_POST_MEME_PIECE:
            await send_reddit_post(context, timer.info)
        case Timer.TEMP_DIR_CLEANUP:
            cleanup_temp_dir()
        case Timer.TIMER_SEND_LEADERBOARD:
            await send_leaderboard(context)
        case Timer.RESET_DOC_Q_GAME:
            reset_doc_q_game()
        case Timer.RESET_BOUNTY_POSTER_LIMIT:
            reset_bounty_poster_limit()
        case Timer.RESET_CAN_CHANGE_REGION:
            reset_can_change_region()
        case Timer.ADD_REGION_BOUNTY_BONUS:
            add_region_bounty_bonus()
        case Timer.ADD_CREW_BOUNTY_BONUS:
            add_crew_bounty_bonus()
        case Timer.ADD_CREW_MVP_BOUNTY_BONUS:
            add_crew_mvp_bounty_bonus()
        case Timer.RESET_CAN_INITIATE_GAME:
            reset_can_initiate_game()
        case Timer.SEND_SCHEDULED_PREDICTIONS:
            await send_scheduled_predictions(context)
        case Timer.CLOSE_SCHEDULED_PREDICTIONS:
            await close_scheduled_predictions(context)
        case _:
            logging.error(f'Unknown timer {job.name}')

    if timer.should_log:
        logging.info(f'Finished timer {context.job.name}')
    end(db)

    return
