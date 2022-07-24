import datetime

from telegram import Update
from telegram.ext import CallbackContext

import resources.phrases as phrases
import src.model.enums.Command as Command
import src.model.enums.LeaderboardRank as LeaderboardRank
import src.service.bounty_service as bounty_service
from src.model.SavedMedia import SavedMedia
from src.model.User import User
from src.model.enums import Location
from src.model.enums.MessageSource import MessageSource
from src.model.enums.SavedMediaType import SavedMediaType
from src.model.error.GroupChatError import GroupChatError
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_poster_service import get_bounty_poster
from src.service.cron_service import convert_seconds_to_time
from src.service.leaderboard_service import get_current_leaderboard_user
from src.service.message_service import full_message_send, full_media_send, mention_markdown_v2, \
    get_start_with_command_url


def manage(update: Update, context: CallbackContext, command: Command.Command, inbound_keyboard: Keyboard = None
           ) -> None:
    """
    Displays a user's status
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command
    :param inbound_keyboard: Inbound keyboard
    :return: None
    """

    try:
        in_reply_to_message = update.message.reply_to_message is not None
    except AttributeError:  # In case of a callback in private chat
        in_reply_to_message = False

    can_delete_users: list = []
    user = User.get_or_none(User.tg_user_id == update.effective_user.id)

    # If used in reply to a message, get the user from the message
    if in_reply_to_message:
        # Used in reply to a bot
        if update.effective_message.reply_to_message.from_user.is_bot:
            full_message_send(context, phrases.COMMAND_IN_REPLY_TO_BOT_ERROR, update=update, add_delete_button=True)
            return

        target_user = User.get_or_none(User.tg_user_id == update.effective_message.reply_to_message.from_user.id)
    else:
        target_user = user

    # If the user is not in the database, error
    if target_user is None:
        full_message_send(context, GroupChatError.USER_NOT_IN_DB.build(), update)
        return

    leaderboard_target_user = get_current_leaderboard_user(target_user)
    leaderboard_target_user_rank = LeaderboardRank.get_rank_by_leaderboard_user(leaderboard_target_user)

    if user == target_user:
        leaderboard_user_rank = leaderboard_target_user_rank
    else:
        leaderboard_user_rank = LeaderboardRank.get_rank_by_leaderboard_user(get_current_leaderboard_user(user))

    # If the user leaderboard rank is rookie, they can only request their status in private chat
    if command.message_source is not MessageSource.PRIVATE and leaderboard_user_rank is LeaderboardRank.ROOKIE:
        outbound_keyboard: list[list[Keyboard]] = [[
            Keyboard(phrases.STATUS_PRIVATE_CHAT_KEY, url=get_start_with_command_url(Command.GRP_USER_STATUS.name))]]
        full_message_send(context, phrases.ROOKIE_STATUS_PRIVATE_CHAT_ONLY, update=update, keyboard=outbound_keyboard,
                          add_delete_button=True)
        return

    # If used in reply to a message, verify that requesting user ranks above the user being replied to
    if in_reply_to_message:
        # Add the requested user to the list of users that can delete the message
        can_delete_users.append(target_user.tg_user_id)

        requesting_user = User.get_or_none(User.tg_user_id == update.effective_user.id)
        if requesting_user is None:
            full_message_send(context, GroupChatError.USER_NOT_IN_DB.build(), update, add_delete_button=True,
                              authorized_users=can_delete_users)
            return

        requesting_user_leaderboard_user = get_current_leaderboard_user(requesting_user)

        if requesting_user_leaderboard_user is None or (
                leaderboard_target_user is not None
                and requesting_user_leaderboard_user.position >= leaderboard_target_user.position):
            requesting_user_leaderboard_user_rank = LeaderboardRank.get_rank_by_leaderboard_user(
                requesting_user_leaderboard_user)

            ot_text = phrases.NOT_ALLOWED_TO_VIEW_REPLIED_STATUS.format(
                mention_markdown_v2(requesting_user.tg_user_id, 'Your'),
                requesting_user_leaderboard_user_rank.get_emoji_and_rank_message(),
                mention_markdown_v2(target_user.tg_user_id, target_user.tg_first_name),
                leaderboard_target_user_rank.get_emoji_and_rank_message())

            full_message_send(context, ot_text, update, add_delete_button=True, authorized_users=can_delete_users)
            return

    # Get location
    location: Location = Location.get_by_level(target_user.location_level)

    pending_bounty_addendum = '' if target_user.pending_bounty == 0 else phrases.SHOW_USER_STATUS_PENDING_BOUNTY.format(
        bounty_service.get_bounty_formatted(target_user.pending_bounty))

    message_text = phrases.SHOW_USER_STATUS.format(
        mention_markdown_v2(target_user.tg_user_id, target_user.tg_first_name),
        bounty_service.get_bounty_formatted(target_user.bounty),
        pending_bounty_addendum,
        leaderboard_target_user_rank.get_emoji_and_rank_message(),
        location.name)

    # Add fight immunity if active
    if target_user.fight_immunity_end_date is not None and \
            target_user.fight_immunity_end_date > datetime.datetime.now():
        # Get remaining time
        remaining_time = convert_seconds_to_time((target_user.fight_immunity_end_date - datetime.datetime.now())
                                                 .total_seconds())
        message_text += phrases.SHOW_USER_STATUS_FIGHT_IMMUNITY.format(remaining_time)

    # Add fight cooldown if active
    if target_user.fight_cooldown_end_date is not None and \
            target_user.fight_cooldown_end_date > datetime.datetime.now():
        # Get remaining time
        remaining_time = convert_seconds_to_time((target_user.fight_cooldown_end_date - datetime.datetime.now())
                                                 .total_seconds())
        message_text += phrases.SHOW_USER_STATUS_FIGHT_COOLDOWN.format(remaining_time)

    # If used in reply to a message, reply to original message
    reply_to_message_id = None
    if in_reply_to_message:
        message_text += "\n\n" + phrases.SHOW_USER_STATUS_ADD_REPLY.format(
            mention_markdown_v2(update.effective_user.id,
                                update.effective_user.first_name))
        reply_to_message_id = update.effective_message.reply_to_message.message_id

    # Send bounty poster if not in reply to a message bounty_poster_limit is -1 or higher than 0
    if not in_reply_to_message and (target_user.bounty_poster_limit == -1 or target_user.bounty_poster_limit > 0):
        send_bounty_poster(context, update, target_user, message_text, reply_to_message_id)

        # Reduce bounty poster limit by 1 if it is not None
        if target_user.bounty_poster_limit != -1:
            target_user.bounty_poster_limit -= 1
            target_user.save()
    else:  # Send regular message
        full_message_send(context, message_text, update, reply_to_message_id=reply_to_message_id,
                          add_delete_button=(inbound_keyboard is None), authorized_users=can_delete_users,
                          inbound_keyboard=inbound_keyboard)


def send_bounty_poster(context: CallbackContext, update: Update, user: User, caption: str = None,
                       reply_to_message_id: int = None, send_in_private_chat=False) -> None:
    poster_path = get_bounty_poster(update, user)
    poster: SavedMedia = SavedMedia()
    poster.media_id = open(poster_path, 'rb')
    poster.type = SavedMediaType.PHOTO.value

    full_media_send(context, saved_media=poster, update=update, caption=caption,
                    reply_to_message_id=reply_to_message_id, new_message=True, add_delete_button=True,
                    send_in_private_chat=send_in_private_chat)
