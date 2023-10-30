import datetime

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
import src.model.enums.Command as Command
import src.model.enums.LeaderboardRank as LeaderboardRank
import src.service.bounty_service as bounty_service
from src.model.DevilFruit import DevilFruit
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums import Location
from src.model.enums.Emoji import Emoji
from src.model.enums.MessageSource import MessageSource
from src.model.enums.SavedMedia import SavedMedia
from src.model.enums.SavedMediaType import SavedMediaType
from src.model.error.GroupChatError import GroupChatError, GroupChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_poster_service import get_bounty_poster
from src.service.date_service import get_remaining_duration
from src.service.devil_fruit_service import get_devil_fruit_abilities_text
from src.service.income_tax_service import user_has_complete_tax_deduction
from src.service.leaderboard_service import get_current_leaderboard_user
from src.service.message_service import full_message_send, full_media_send, mention_markdown_v2, \
    get_start_with_command_url, escape_valid_markdown_chars, message_is_reply
from src.service.user_service import user_is_boss


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, command: Command.Command, original_user: User,
                 inbound_keyboard: Keyboard = None, group_chat: GroupChat = None) -> None:
    """
    Displays a user's status
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command
    :param original_user: The original user
    :param inbound_keyboard: Inbound keyboard
    :param group_chat: Group chat
    :return: None
    """

    try:
        in_reply_to_message = message_is_reply(update)  # REPLY_TO_MESSAGE_BUG_FIX
    except AttributeError:  # In case of a callback in private chat
        in_reply_to_message = False

    can_delete_users: list = []
    user = User.get_or_none(User.tg_user_id == update.effective_user.id)

    # If used in reply to a message, get the user from the message
    if in_reply_to_message:
        # Used in reply to a bot
        if update.effective_message.reply_to_message.from_user.is_bot:
            await full_message_send(context, phrases.COMMAND_IN_REPLY_TO_BOT_ERROR, update=update,
                                    add_delete_button=True)
            return

        target_user: User = User.get_or_none(User.tg_user_id == update.effective_message.reply_to_message.from_user.id)
    else:
        target_user: User = user

    # If the user is not in the database, error
    if target_user is None:
        raise GroupChatException(GroupChatError.USER_NOT_IN_DB)

    leaderboard_target_user = get_current_leaderboard_user(target_user, group_chat=group_chat)
    leaderboard_target_user_rank = LeaderboardRank.get_rank_by_leaderboard_user(leaderboard_target_user)

    # If used in reply to a message, verify that requesting user ranks above the user being replied to
    if in_reply_to_message and not target_user.is_arrested():  # Arrested users are always viewable
        # Add the requested user to the list of users that can delete the message
        can_delete_users.append(target_user.tg_user_id)

        requesting_user_leaderboard_user = get_current_leaderboard_user(user, group_chat=group_chat)

        if not user_is_boss(user, group_chat=group_chat) and (requesting_user_leaderboard_user is None or (
                leaderboard_target_user is not None
                and requesting_user_leaderboard_user.position >= leaderboard_target_user.position)):
            requesting_user_leaderboard_user_rank = LeaderboardRank.get_rank_by_leaderboard_user(
                requesting_user_leaderboard_user)

            ot_text = phrases.NOT_ALLOWED_TO_VIEW_REPLIED_STATUS.format(
                mention_markdown_v2(user.tg_user_id, 'Your'),
                requesting_user_leaderboard_user_rank.get_emoji_and_rank_message(),
                mention_markdown_v2(target_user.tg_user_id, target_user.tg_first_name),
                leaderboard_target_user_rank.get_emoji_and_rank_message())

            await full_message_send(context, ot_text, update, add_delete_button=True, authorized_users=can_delete_users)
            return

    # Allowed only in private chat (Rookie or Prisoner)
    if not Env.ROOKIES_OR_ARRESTED_CAN_VIEW_STATUS_IN_GROUP.get_bool():
        if user == target_user:
            leaderboard_user_rank = leaderboard_target_user_rank
        else:
            leaderboard_user_rank = LeaderboardRank.get_rank_by_leaderboard_user(
                get_current_leaderboard_user(user, group_chat=group_chat))
        if (command.message_source is not MessageSource.PRIVATE
                and ((leaderboard_user_rank is LeaderboardRank.ROOKIE and not user_is_boss(user, group_chat=group_chat))
                     or user.is_arrested())):
            outbound_keyboard: list[list[Keyboard]] = [[
                Keyboard(phrases.STATUS_PRIVATE_CHAT_KEY,
                         url=get_start_with_command_url(Command.GRP_USER_STATUS.name))]]

            ot_text = (phrases.PRISONER_STATUS_PRIVATE_CHAT_ONLY if user.is_arrested()
                       else phrases.ROOKIE_STATUS_PRIVATE_CHAT_ONLY)
            await full_message_send(context, ot_text, update=update, keyboard=outbound_keyboard, add_delete_button=True)
            return

    pending_bounty_addendum = '' if target_user.pending_bounty == 0 else phrases.SHOW_USER_STATUS_PENDING_BOUNTY.format(
        bounty_service.get_belly_formatted(target_user.pending_bounty))

    bounty_string = target_user.get_bounty_formatted()
    if target_user.is_arrested():
        bounty_string += phrases.SHOW_USER_STATUS_FROZEN_BOUNTY
        location_name = phrases.SHOW_USER_STATUS_IMPEL_DOWN
        target_user_rank = phrases.SHOW_USER_STATUS_RANK_PRISONER
    else:
        location_name = Location.get_by_level(target_user.location_level).name
        target_user_rank = leaderboard_target_user_rank.get_emoji_and_rank_message()

    message_text = phrases.SHOW_USER_STATUS.format(
        mention_markdown_v2(target_user.tg_user_id, target_user.tg_first_name),
        bounty_string,
        pending_bounty_addendum,
        target_user_rank,
        escape_valid_markdown_chars(location_name))

    # Add Crew if in one
    if target_user.is_crew_member():
        crew = target_user.crew
        message_text += phrases.SHOW_USER_STATUS_CREW.format(escape_valid_markdown_chars(crew.name))

    # Remaining sentence if arrested
    if target_user.is_arrested():
        if not user.impel_down_is_permanent:
            remaining_time = get_remaining_duration(target_user.impel_down_release_date)
        else:
            remaining_time = phrases.SHOW_USER_STATUS_PERMANENT_IMPEL_DOWN
        message_text += phrases.SHOW_USER_STATUS_REMAINING_SENTENCE.format(remaining_time)

    # Add fight immunity if active
    if target_user.fight_immunity_end_date is not None and \
            target_user.fight_immunity_end_date > datetime.datetime.now():
        # Get remaining time
        remaining_time = get_remaining_duration(target_user.fight_immunity_end_date)
        message_text += phrases.SHOW_USER_STATUS_FIGHT_IMMUNITY.format(remaining_time)

    # Add fight cooldown if active
    if target_user.fight_cooldown_end_date is not None and \
            target_user.fight_cooldown_end_date > datetime.datetime.now():
        # Get remaining time
        remaining_time = get_remaining_duration(target_user.fight_cooldown_end_date)
        message_text += phrases.SHOW_USER_STATUS_FIGHT_COOLDOWN.format(remaining_time)

    # BOUNTY BONUSES
    has_bounty_bonus = False
    bounty_bonus_text = phrases.SHOW_USER_STATUS_BOUNTY_DAILY_BONUSES_TITLE

    # Crew Bounty Bonus
    if target_user.has_crew_bonus():
        bounty_bonus_text += phrases.SHOW_USER_STATUS_BOUNTY_BONUSES_TEXT.format(
            Emoji.LOG_POSITIVE if Env.CREW_BOUNTY_BONUS.get_int() > 0 else Emoji.LOG_NEGATIVE,
            phrases.SHOW_USER_STATUS_BOUNTY_BONUS_CREW,
            Env.CREW_BOUNTY_BONUS.get_int())
        has_bounty_bonus = True

    # Crew MVP Bounty Bonus
    if target_user.has_crew_mvp_bonus():
        bounty_bonus_text += phrases.SHOW_USER_STATUS_BOUNTY_BONUSES_TEXT.format(
            Emoji.LOG_POSITIVE if Env.CREW_MVP_BOUNTY_BONUS.get_int() > 0 else Emoji.LOG_NEGATIVE,
            phrases.SHOW_USER_STATUS_BOUNTY_BONUS_CREW_MVP,
            Env.CREW_MVP_BOUNTY_BONUS.get_int())
        has_bounty_bonus = True

    # New World Bounty Bonus
    if target_user.has_new_world_bonus():
        bounty_bonus_text += phrases.SHOW_USER_STATUS_BOUNTY_BONUSES_TEXT.format(
            Emoji.LOG_POSITIVE if Env.NEW_WORLD_BOUNTY_BONUS.get_int() > 0 else Emoji.LOG_NEGATIVE,
            phrases.SHOW_USER_STATUS_BOUNTY_BONUS_NEW_WORLD,
            Env.NEW_WORLD_BOUNTY_BONUS.get_int())
        has_bounty_bonus = True

    if has_bounty_bonus:
        message_text += bounty_bonus_text

    # BOUNTY DEDUCTIONS
    has_bounty_deduction = False
    bounty_deduction_text = phrases.SHOW_USER_STATUS_BOUNTY_DEDUCTIONS_TITLE

    # Expired loan
    if target_user.has_expired_bounty_loans():
        bounty_deduction_text += phrases.SHOW_USER_STATUS_BOUNTY_BONUSES_TEXT.format(
            Emoji.LOG_NEGATIVE,
            phrases.SHOW_USER_STATUS_EXPIRED_LOAN,
            (-1 * Env.BOUNTY_LOAN_GARNISH_PERCENTAGE.get_float()))
        has_bounty_deduction = True

    # Income tax
    if target_user.has_income_tax() and not user_has_complete_tax_deduction(user):
        bounty_deduction_text += phrases.SHOW_USER_STATUS_BOUNTY_BONUSES_TEXT.format(
            Emoji.LOG_NEGATIVE,
            phrases.SHOW_USER_STATUS_INCOME_TAX,
            (-1 * target_user.get_income_tax_percentage()))
        has_bounty_deduction = True

    if has_bounty_deduction:
        message_text += bounty_deduction_text

    # Devil Fruit
    eaten_devil_fruit = DevilFruit.get_by_owner_if_eaten(target_user)
    if eaten_devil_fruit is not None:
        message_text += phrases.SHOW_USER_STATUS_DEVIL_FRUIT.format(
            eaten_devil_fruit.get_full_name(),
            get_devil_fruit_abilities_text(eaten_devil_fruit, add_header=False))

    # If used in reply to a message, reply to original message
    reply_to_message_id = None
    if in_reply_to_message:
        message_text += "\n\n" + phrases.SHOW_USER_STATUS_ADD_REPLY.format(
            mention_markdown_v2(update.effective_user.id,
                                update.effective_user.first_name))
        reply_to_message_id = update.effective_message.reply_to_message.message_id

    # Send bounty poster if not in reply to a message bounty_poster_limit is -1 or higher than 0 and user is not jailed
    if (not in_reply_to_message
            and (user_is_boss(target_user, group_chat=group_chat) or target_user.bounty_poster_limit > 0)
            and not target_user.is_arrested()):
        await send_bounty_poster(context, update, target_user, message_text, reply_to_message_id)

        # Reduce bounty poster limit by 1 if it is not None
        if not user_is_boss(target_user, group_chat=group_chat):
            target_user.bounty_poster_limit -= 1
            target_user.save()
            original_user.should_update_model = False

    else:  # Send regular message
        await full_message_send(context, message_text, update, reply_to_message_id=reply_to_message_id,
                                add_delete_button=(inbound_keyboard is None), authorized_users=can_delete_users,
                                inbound_keyboard=inbound_keyboard)


async def send_bounty_poster(context: ContextTypes.DEFAULT_TYPE, update: Update, user: User, caption: str = None,
                             reply_to_message_id: int = None, send_in_private_chat=False) -> None:
    poster_path = await get_bounty_poster(update, user)
    poster: SavedMedia = SavedMedia(media_type=SavedMediaType.PHOTO)
    poster.media_id = open(poster_path, 'rb')

    await full_media_send(context, saved_media=poster, update=update, caption=caption,
                          reply_to_message_id=reply_to_message_id, new_message=True, add_delete_button=True,
                          send_in_private_chat=send_in_private_chat)
