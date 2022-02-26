import os

from telegram import Update
from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_markdown

import constants as c
import resources.phrases as phrases
import src.service.bounty_service as bounty_service
from src.model.User import User
from src.model.error.GroupChatError import GroupChatError
from src.service.cron_service import cron_datetime_difference
from src.service.message_service import full_message_send


def reset_bounty(context: CallbackContext) -> None:
    """
    Resets the bounty to 0 for all users
    :return: None
    """
    User.update(bounty=0).execute()

    ot_text = phrases.BOUNTY_RESET
    full_message_send(context, ot_text, chat_id=int(os.environ[c.ENV_OPD_GROUP_ID])).pin(disable_notification=True)


def reset_bounty_alert(context: CallbackContext) -> None:
    """
    Sends a message to the group chat to alert that bounties will be reset
    :param context: Telegram context
    :return: None
    """

    ot_text = phrases.BOUNTY_RESET_ALERT.format(cron_datetime_difference(os.environ.get(c.ENV_CRON_RESET_BOUNTY,
                                                                                        c.DEFAULT_CRON_RESET_BOUNTY)))

    full_message_send(context, ot_text, chat_id=int(os.environ[c.ENV_OPD_GROUP_ID])).pin(disable_notification=True)


def manage(update: Update, context: CallbackContext) -> None:
    """
    Displays a user's bounty
    :param update: Telegram update
    :param context: Telegram context
    :return: None
    """

    # If used in reply to a message, get the user from the message
    if update.effective_message.reply_to_message is not None:
        user = User.get_or_none(User.tg_user_id == update.effective_message.reply_to_message.from_user.id)
    else:
        user = User.get_or_none(User.tg_user_id == update.effective_user.id)

    # If the user is not in the database, error
    if user is None:
        full_message_send(context, GroupChatError.USER_NOT_IN_DB.build(), update)
        return

    message_text = phrases.SHOW_USER_BOUNTY.format(mention_markdown(user.tg_user_id, user.tg_first_name),
                                                   bounty_service.get_bounty_formatted(user.bounty))

    # If used in reply to a message, reply to that message
    if update.effective_message.reply_to_message is not None:
        message_text += "\n\n" + phrases \
            .SHOW_USER_BOUNTY_ADD_REPLY.format(mention_markdown(update.effective_user.id,
                                                                update.effective_user.first_name))

        full_message_send(context, message_text, update, quote=True)
    else:
        full_message_send(context, message_text, update)
