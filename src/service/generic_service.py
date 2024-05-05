from telegram.ext import ContextTypes

from src.model.DavyBackFight import DavyBackFight
from src.service.crew_service import end_all_conscription
from src.service.davy_back_fight_service import start_all as start_dbf, end_all as end_dbf
from src.service.group_service import auto_delete


async def run_minute_tasks(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Run the minute tasks
    :param context: The context
    :return: None
    """

    # Delete expired Davy Back Fight Requests
    context.application.create_task(DavyBackFight.delete_expired_requests())

    # Start Davy Back Fight
    context.application.create_task(start_dbf(context))

    # End Davy Back Fight
    context.application.create_task(end_dbf(context))

    # End all Crew conscription
    context.application.create_task(end_all_conscription(context))

    # Auto delete messages
    context.application.create_task(auto_delete(context))
