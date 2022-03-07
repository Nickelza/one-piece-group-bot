from telegram import Message
from telegram.ext import CallbackContext

import resources.Environment as Env
import resources.phrases as phrases
import src.service.bounty_service as bounty_service
from src.model.Leaderboard import Leaderboard
from src.model.User import User
from src.service.leaderboard_service import create_leaderboard
from src.service.message_service import full_message_send, mention_markdown_v2


def get_leaderboard_message(leaderboard: Leaderboard) -> str:
    """
    Gets the leaderboard message
    :param leaderboard: The leaderboard
    :return: The leaderboard message
    """
    ot_text = phrases.LEADERBOARD_HEADER.format(leaderboard.week, leaderboard.year,
                                                leaderboard.leaderboard_users.count())

    for leaderboard_user in leaderboard.leaderboard_users:
        user: User = User.get_by_id(leaderboard_user.user.id)

        ot_text += phrases.LEADERBOARD_ROW.format(leaderboard_user.position,
                                                  mention_markdown_v2(user.tg_user_id, user.tg_first_name),
                                                  bounty_service.get_bounty_formatted(user.bounty))

    return ot_text


def manage(context: CallbackContext) -> None:
    """
    Sends the weekly leaderboard to the group
    :param context: Context of callback
    """

    leaderboard = create_leaderboard()

    # Send the leaderboard to the group
    ot_text = get_leaderboard_message(leaderboard)
    message: Message = full_message_send(context, ot_text, chat_id=Env.OPD_GROUP_ID.get())
    message.pin(disable_notification=False)

    # Save the message id
    leaderboard.message_id = message.message_id
    leaderboard.save()
