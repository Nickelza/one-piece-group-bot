import os

from apscheduler.triggers.cron import CronTrigger
from telegram.ext import CallbackContext, Dispatcher

import constants as const
from src.chat.group.screens.screen_send_reddit_post import manage as send_reddit_post
from src.service.dowload_service import cleanup_temp_dir


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
            callback=send_reddit_post,
            job_kwargs={"trigger": CronTrigger.from_crontab(reddit_post_timer['cron'])},
            name=reddit_post_timer['name'],
            context=reddit_post_timer['subreddit']
        )

    # Temp folder cleanup timer
    job = context.job_queue.run_custom(
        callback=cleanup_temp_dir,
        job_kwargs={"trigger": CronTrigger.from_crontab(os.environ[const.ENV_CRON_TEMP_DIR_CLEANUP])},
        name='cleanup_temp_folder'
    )
