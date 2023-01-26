from telegram import Update

import resources.Environment as Env


def is_main_group(update: Update) -> bool:
    """
    Checks if the update is from the main group
    :param update: The update
    :return: True if the update is from the main group, False otherwise
    """

    return update.effective_chat.id == Env.OPD_GROUP_ID.get_int()
