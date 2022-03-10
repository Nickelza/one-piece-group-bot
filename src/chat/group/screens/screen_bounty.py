from telegram import Update
from telegram.ext import CallbackContext

import resources.Environment as Env
import resources.phrases as phrases
import src.service.bounty_service as bounty_service
from src.model.SavedMedia import SavedMedia
from src.model.User import User
from src.model.enums.LeaderboardTitle import get_title_by_leaderboard_user
from src.model.enums.SavedMediaType import SavedMediaType
from src.model.error.GroupChatError import GroupChatError
from src.service.bounty_poster_service import get_bounty_poster
from src.service.cron_service import cron_datetime_difference
from src.service.leaderboard_service import get_current_leaderboard_user
from src.service.message_service import full_message_send, full_media_send, mention_markdown_v2


def reset_bounty(context: CallbackContext) -> None:
    """
    Resets the bounty to 0 for all users
    :return: None
    """
    User.update(bounty=0).execute()

    ot_text = phrases.BOUNTY_RESET
    full_message_send(context, ot_text, chat_id=Env.OPD_GROUP_ID.get_int()).pin(disable_notification=True)


def reset_bounty_alert(context: CallbackContext) -> None:
    """
    Sends a message to the group chat to alert that bounties will be reset
    :param context: Telegram context
    :return: None
    """

    ot_text = phrases.BOUNTY_RESET_ALERT.format(cron_datetime_difference(Env.CRON_RESET_BOUNTY.get()))

    full_message_send(context, ot_text, chat_id=Env.OPD_GROUP_ID.get_int()).pin(disable_notification=True)


def manage(update: Update, context: CallbackContext) -> None:
    """
    Displays a user's bounty
    :param update: Telegram update
    :param context: Telegram context
    :return: None
    """

    # If used in reply to a message, get the user from the message
    if update.effective_message.reply_to_message is not None:
        # Used in reply to a bot
        if update.effective_message.reply_to_message.from_user.is_bot:
            full_message_send(context, phrases.COMMAND_IN_REPLY_TO_BOT_ERROR, update=update)
            return

        user = User.get_or_none(User.tg_user_id == update.effective_message.reply_to_message.from_user.id)
    else:
        user = User.get_or_none(User.tg_user_id == update.effective_user.id)

    # If the user is not in the database, error
    if user is None:
        full_message_send(context, GroupChatError.USER_NOT_IN_DB.build(), update)
        return

    # If used in reply to a message, verify that requesting user ranks above the user being replied to
    if update.effective_message.reply_to_message is not None:
        requesting_user = User.get_or_none(User.tg_user_id == update.effective_user.id)
        if requesting_user is None:
            full_message_send(context, GroupChatError.USER_NOT_IN_DB.build(), update)
            return

        leaderboard_user = get_current_leaderboard_user(user)
        requesting_user_leaderboard_user = get_current_leaderboard_user(requesting_user)

        if requesting_user_leaderboard_user is None or (
                leaderboard_user is not None
                and requesting_user_leaderboard_user.position >= leaderboard_user.position):
            leaderboard_user_title = get_title_by_leaderboard_user(leaderboard_user)
            requesting_user_leaderboard_user_title = get_title_by_leaderboard_user(requesting_user_leaderboard_user)

            ot_text = phrases.NOT_ALLOWED_TO_VIEW_REPLIED_BOUNTY.format(
                mention_markdown_v2(requesting_user.tg_user_id, 'Your'),
                leaderboard_user_title.get_emoji_and_title_message(),
                mention_markdown_v2(user.tg_user_id, user.tg_first_name),
                requesting_user_leaderboard_user_title.get_emoji_and_title_message())

            full_message_send(context, ot_text, update)
            return

    message_text = phrases.SHOW_USER_BOUNTY.format(mention_markdown_v2(user.tg_user_id, user.tg_first_name),
                                                   bounty_service.get_bounty_formatted(user.bounty))

    # If used in reply to a message, reply to original message
    reply_to_message_id = None
    if update.effective_message.reply_to_message is not None:
        message_text += "\n\n" + phrases \
            .SHOW_USER_BOUNTY_ADD_REPLY.format(mention_markdown_v2(update.effective_user.id,
                                                                   update.effective_user.first_name))
        reply_to_message_id = update.effective_message.reply_to_message.message_id

    # Send bounty poster if bounty_poster_limit is None or higher than 0
    if user.bounty_poster_limit == -1 or user.bounty_poster_limit > 0:
        poster_path = get_bounty_poster(update, user)
        poster: SavedMedia = SavedMedia()
        poster.media_id = open(poster_path, 'rb')
        poster.type = SavedMediaType.PHOTO.value
        full_media_send(context, saved_media=poster, update=update, caption=message_text,
                        reply_to_message_id=reply_to_message_id)

        # Reduce bounty poster limit by 1 if it is not None
        if user.bounty_poster_limit != -1:
            user.bounty_poster_limit -= 1
            user.save()
    else:  # Send regular message
        full_message_send(context, message_text, update, reply_to_message_id=reply_to_message_id)
