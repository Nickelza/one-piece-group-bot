from src.model.DavyBackFight import DavyBackFight


async def run_generic_minute_tasks() -> None:
    """
    Run the generic minute tasks
    :return: None
    """

    # Delete expired Davy Back Fight Requests
    DavyBackFight.delete_expired_requests()
