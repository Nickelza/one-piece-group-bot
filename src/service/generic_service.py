from telegram.ext import ContextTypes

from src.model.DavyBackFight import DavyBackFight
from src.service.davy_back_fight_service import start_all as start_dbf, end_all as end_dbf


async def run_generic_minute_tasks(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Run the generic minute tasks
    :param context: The context
    :return: None
    """

    # Delete expired Davy Back Fight Requests
    context.application.create_task(DavyBackFight.delete_expired_requests())

    # Start Davy Back Fight
    context.application.create_task(start_dbf(context))

    # End Davy Back Fight
    context.application.create_task(end_dbf(context))
