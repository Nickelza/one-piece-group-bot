import logging
import os
import sys
import time
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    Defaults,
    CallbackQueryHandler,
    ContextTypes,
    AIORateLimiter,
    InlineQueryHandler,
)

import constants as c
import resources.Environment as Env
from src.chat.manage_message import (
    manage_regular as manage_regular_message,
    manage_callback as manage_callback_message,
)
from src.service.message_service import full_message_send
from src.service.timer_service import set_timers


async def chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send chat id of current chat
    :param update: Telegram update
    :param context: Telegram context
    :return: None
    """
    await full_message_send(context, str(update.effective_chat.id), update)


def pre_init():
    """
    Pre init checks
    :return: None, raises Exception if something is wrong
    """

    # Check that all the required environment variables are set
    for env in Env.Environment.instances:
        env.get()


async def post_init(application: Application) -> None:
    """
    Post init
    :param application: the application
    :return: None
    """
    await application.job_queue.start()
    await set_timers(application)


def main() -> None:
    """
    Main function. Starts the bot
    :return: None
    """
    # Set timezone: Only on linux
    os.environ["TZ"] = Env.TZ.get()
    try:
        time.tzset()
    except AttributeError:
        pass

    # Pre init checks
    pre_init()

    if Env.DB_LOG_QUERIES.get_bool():
        # Set Peewee logger
        logger = logging.getLogger("peewee")
        logger.addHandler(logging.StreamHandler())
        logger.setLevel(logging.DEBUG)

    # Disable httpx logging info
    logging.getLogger("httpx").setLevel(logging.WARNING)

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.getLevelName(Env.LOG_LEVEL.get()),
        stream=sys.stdout,
    )

    # Sentry
    if Env.SENTRY_ENABLED.get_bool():
        import sentry_sdk
        from sentry_sdk.integrations.logging import LoggingIntegration

        sentry_sdk.init(
            dsn=Env.SENTRY_DSN.get(),
            environment=Env.SENTRY_ENVIRONMENT.get(),
            enable_tracing=Env.SENTRY_ENABLE_TRACING.get_bool(),
            traces_sample_rate=Env.SENTRY_TRACES_SAMPLE_RATE.get_float(),
            profiles_sample_rate=Env.SENTRY_PROFILES_SAMPLE_RATE.get_float(),
            integrations=[
                LoggingIntegration(
                    level=logging.getLevelName(Env.SENTRY_LOG_LEVEL.get()),
                    event_level=logging.getLevelName(Env.SENTRY_LOG_EVENT_LEVEL.get()),
                ),
            ],
        )

    defaults = Defaults(parse_mode=c.TG_DEFAULT_PARSE_MODE, tzinfo=ZoneInfo(Env.TZ.get()))

    application = (
        Application.builder()
        .token(Env.BOT_TOKEN.get())
        .post_init(post_init)
        .defaults(defaults)
        .rate_limiter(AIORateLimiter())
        .build()
    )

    # Chat id handler
    application.add_handler(CommandHandler("chatid", chat_id))

    # Regular message handler
    application.add_handler(MessageHandler(filters.ALL, manage_regular_message))

    # Callback query handler
    application.add_handler(CallbackQueryHandler(manage_callback_message))

    # Inline query handler
    application.add_handler(InlineQueryHandler(manage_regular_message))

    # Activate timers
    logging.getLogger("apscheduler.executors.default").propagate = False

    application.run_polling(drop_pending_updates=Env.BOT_DROP_PENDING_UPDATES.get_bool())


if __name__ == "__main__":
    main()
