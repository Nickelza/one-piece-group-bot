import datetime

from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
import src.service.bounty_service as bounty_service
from src.model.SavedMedia import SavedMedia
from src.model.User import User
from src.model.enums import Location
from src.model.enums.LeaderboardRank import get_rank_by_leaderboard_user
from src.model.enums.SavedMediaType import SavedMediaType
from src.model.error.GroupChatError import GroupChatError
from src.service.bounty_poster_service import get_bounty_poster
from src.service.cron_service import convert_seconds_to_time
from src.service.leaderboard_service import get_current_leaderboard_user
from src.service.message_service import full_message_send, full_media_send, mention_markdown_v2


def manage(update: Update, context: CallbackContext) -> None:
    """
    Displays a user's status
    :param update: Telegram update
    :param context: Telegram context
    :return: None
    """

    in_reply_to_message = update.message.reply_to_message is not None
    can_delete_users: list = []

    # If used in reply to a message, get the user from the message
    if in_reply_to_message:
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

    leaderboard_user = get_current_leaderboard_user(user)
    leaderboard_user_rank = get_rank_by_leaderboard_user(leaderboard_user)

    # If used in reply to a message, verify that requesting user ranks above the user being replied to
    if in_reply_to_message:
        requesting_user = User.get_or_none(User.tg_user_id == update.effective_user.id)
        if requesting_user is None:
            full_message_send(context, GroupChatError.USER_NOT_IN_DB.build(), update)
            return

        requesting_user_leaderboard_user = get_current_leaderboard_user(requesting_user)

        if requesting_user_leaderboard_user is None or (
                leaderboard_user is not None
                and requesting_user_leaderboard_user.position >= leaderboard_user.position):
            requesting_user_leaderboard_user_rank = get_rank_by_leaderboard_user(requesting_user_leaderboard_user)

            ot_text = phrases.NOT_ALLOWED_TO_VIEW_REPLIED_STATUS.format(
                mention_markdown_v2(requesting_user.tg_user_id, 'Your'),
                requesting_user_leaderboard_user_rank.get_emoji_and_rank_message(),
                mention_markdown_v2(user.tg_user_id, user.tg_first_name),
                leaderboard_user_rank.get_emoji_and_rank_message())

            full_message_send(context, ot_text, update)
            return

        # Add the requested user to the list of users that can delete the message
        can_delete_users.append(user.tg_user_id)

    # Get location
    location: Location = Location.get_by_level(user.location_level)

    message_text = phrases.SHOW_USER_STATUS.format(mention_markdown_v2(user.tg_user_id, user.tg_first_name),
                                                   bounty_service.get_bounty_formatted(user.bounty),
                                                   leaderboard_user_rank.get_emoji_and_rank_message(),
                                                   location.name)

    # Add fight immunity if active
    if user.fight_immunity_end_date is not None and user.fight_immunity_end_date > datetime.datetime.now():
        # Get remaining time
        remaining_time = convert_seconds_to_time((user.fight_immunity_end_date - datetime.datetime.now())
                                                 .total_seconds())
        message_text += phrases.SHOW_USER_STATUS_FIGHT_IMMUNITY.format(remaining_time)

    # If used in reply to a message, reply to original message
    reply_to_message_id = None
    if in_reply_to_message:
        message_text += "\n\n" + phrases.SHOW_USER_STATUS_ADD_REPLY.format(
            mention_markdown_v2(update.effective_user.id,
                                update.effective_user.first_name))
        reply_to_message_id = update.effective_message.reply_to_message.message_id

    # Send bounty poster if not in reply to a message bounty_poster_limit is -1 or higher than 0
    if not in_reply_to_message and (user.bounty_poster_limit == -1 or user.bounty_poster_limit > 0):
        send_bounty_poster(context, update, user, message_text, reply_to_message_id)

        # Reduce bounty poster limit by 1 if it is not None
        if user.bounty_poster_limit != -1:
            user.bounty_poster_limit -= 1
            user.save()
    else:  # Send regular message
        full_message_send(context, message_text, update, reply_to_message_id=reply_to_message_id,
                          add_delete_button=True, authorized_users=can_delete_users)


def send_bounty_poster(context: CallbackContext, update: Update, user: User, caption: str = None,
                       reply_to_message_id: int = None) -> None:
    poster_path = get_bounty_poster(update, user)
    poster: SavedMedia = SavedMedia()
    poster.media_id = open(poster_path, 'rb')
    poster.type = SavedMediaType.PHOTO.value

    full_media_send(context, saved_media=poster, update=update, caption=caption,
                    reply_to_message_id=reply_to_message_id, new_message=True)
