from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
import src.service.bounty_service as bounty_service
from src.model.SavedMedia import SavedMedia
from src.model.User import User
from src.model.enums.LeaderboardRank import get_rank_by_leaderboard_user
from src.model.enums.SavedMediaType import SavedMediaType
from src.model.error.GroupChatError import GroupChatError
from src.service.bounty_poster_service import get_bounty_poster
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

    message_text = phrases.SHOW_USER_STATUS.format(mention_markdown_v2(user.tg_user_id, user.tg_first_name),
                                                   bounty_service.get_bounty_formatted(user.bounty),
                                                   leaderboard_user_rank.get_emoji_and_rank_message())

    # If used in reply to a message, reply to original message
    reply_to_message_id = None
    if in_reply_to_message:
        message_text += "\n\n" + phrases \
            .SHOW_USER_STATUS_ADD_REPLY.format(mention_markdown_v2(update.effective_user.id,
                                                                   update.effective_user.first_name))
        reply_to_message_id = update.effective_message.reply_to_message.message_id

    # Send bounty poster if not in reply to a message bounty_poster_limit is -1 or higher than 0
    if not in_reply_to_message and (user.bounty_poster_limit == -1 or user.bounty_poster_limit > 0):
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
