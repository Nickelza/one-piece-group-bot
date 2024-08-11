import datetime

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
import src.model.enums.Command as Command
import src.model.enums.LeaderboardRank as LeaderboardRank
from src.model.Crew import Crew
from src.model.DevilFruit import DevilFruit
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.Warlord import Warlord
from src.model.enums import Location
from src.model.enums.BossType import BossType
from src.model.enums.Emoji import Emoji
from src.model.enums.LeaderboardRank import LeaderboardRank
from src.model.enums.MessageSource import MessageSource
from src.model.enums.SavedMedia import SavedMedia
from src.model.enums.SavedMediaType import SavedMediaType
from src.model.error.GroupChatError import GroupChatError, GroupChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_poster_service import get_bounty_poster
from src.service.crew_service import get_crew_abilities_text, get_crew_name_with_deeplink
from src.service.date_service import get_remaining_duration
from src.service.devil_fruit_service import get_devil_fruit_abilities_text
from src.service.impel_down_service import get_post_bail_deeplink_button
from src.service.income_tax_service import user_has_complete_tax_deduction
from src.service.leaderboard_service import get_current_leaderboard_user, get_highest_active_rank
from src.service.message_service import (
    full_message_send,
    full_media_send,
    mention_markdown_v2,
    get_start_with_command_url,
    escape_valid_markdown_chars,
)
from src.service.user_service import user_is_boss, get_boss_type
from src.utils.string_utils import get_belly_formatted


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    command: Command.Command,
    user: User,
    inbound_keyboard: Keyboard = None,
    group_chat: GroupChat = None,
    target_user: User = None,
) -> None:
    """
    Displays a user's status
    :param update: Telegram update
    :param context: Telegram context
    :param command: Command
    :param user: The original user
    :param inbound_keyboard: Inbound keyboard
    :param group_chat: Group chat
    :param target_user: Target user
    :return: None
    """

    can_delete_users: list[User] = []
    inline_keyboard: list[list[Keyboard]] = []

    self_status = True if target_user is None else False
    target_user = target_user if target_user is not None else user

    # If the user is not in the database, error
    if target_user is None:
        raise GroupChatException(GroupChatError.USER_NOT_IN_DB)

    leaderboard_target_user_rank = get_highest_active_rank(target_user, group_chat=group_chat)

    # If used in reply to a message, verify that requesting user ranks above the user being replied
    # to
    if not self_status and not target_user.is_arrested():  # Arrested users are always viewable
        # Add the requested user to the list of users that can delete the message
        can_delete_users.append(target_user)

        requesting_user_leaderboard_user_rank = get_highest_active_rank(
            user, group_chat=group_chat
        )

        if not requesting_user_leaderboard_user_rank.is_higher(leaderboard_target_user_rank):
            ot_text = phrases.NOT_ALLOWED_TO_VIEW_REPLIED_STATUS.format(
                mention_markdown_v2(user.tg_user_id, "Your"),
                requesting_user_leaderboard_user_rank.get_emoji_and_rank_message(),
                mention_markdown_v2(target_user.tg_user_id, target_user.tg_first_name),
                leaderboard_target_user_rank.get_emoji_and_rank_message(),
            )

            await full_message_send(
                context, ot_text, update, add_delete_button=True, authorized_users=can_delete_users
            )
            return

    # Allowed only in private chat (Rookie or Prisoner)
    if not Env.ROOKIES_OR_ARRESTED_CAN_VIEW_STATUS_IN_GROUP.get_bool():
        if user == target_user:
            leaderboard_user_rank = leaderboard_target_user_rank
        else:
            leaderboard_user_rank = LeaderboardRank.get_rank_by_leaderboard_user(
                get_current_leaderboard_user(user, group_chat=group_chat)
            )
        if command.message_source is not MessageSource.PRIVATE and (
            (
                leaderboard_user_rank is LeaderboardRank.ROOKIE
                and not user_is_boss(user, group_chat=group_chat)
            )
            or user.is_arrested()
        ):
            outbound_keyboard: list[list[Keyboard]] = [
                [
                    Keyboard(
                        phrases.STATUS_PRIVATE_CHAT_KEY,
                        url=get_start_with_command_url(Command.GRP_USER_STATUS.name),
                    )
                ]
            ]

            ot_text = (
                phrases.PRISONER_STATUS_PRIVATE_CHAT_ONLY
                if user.is_arrested()
                else phrases.ROOKIE_STATUS_PRIVATE_CHAT_ONLY
            )
            await full_message_send(
                context, ot_text, update=update, keyboard=outbound_keyboard, add_delete_button=True
            )
            return

    pending_bounty_addendum = (
        ""
        if target_user.pending_bounty == 0
        else phrases.SHOW_USER_STATUS_PENDING_BOUNTY.format(
            get_belly_formatted(target_user.pending_bounty)
        )
    )

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
        escape_valid_markdown_chars(location_name),
    )

    # Add Crew if in one
    if target_user.is_crew_member():
        message_text += phrases.SHOW_USER_STATUS_CREW.format(
            get_crew_name_with_deeplink(target_user.crew)
        )

    # Extra info visible only if checking own status or being checked by a boss
    if self_status or user_is_boss(user, group_chat=group_chat):
        # Remaining sentence if arrested
        if target_user.is_arrested():
            if not user.impel_down_is_permanent:
                remaining_time = get_remaining_duration(target_user.impel_down_release_date)
            else:
                remaining_time = phrases.SHOW_USER_STATUS_PERMANENT_IMPEL_DOWN
            message_text += phrases.SHOW_USER_STATUS_REMAINING_SENTENCE.format(remaining_time)

            message_text += phrases.SHOW_USER_STATUS_RESTRICTIONS.format(
                phrases.IMPEL_DOWN_RESTRICTIONS
            )
            if not user.impel_down_is_permanent:
                message_text += phrases.IMPEL_DOWN_RESTRICTION_BAIL_GUIDE

                inline_keyboard.append(
                    [get_post_bail_deeplink_button(target_user.get_current_impel_down_log())]
                )

        if not target_user.is_arrested():
            # Add fight immunity if active
            if (
                target_user.fight_immunity_end_date is not None
                and target_user.fight_immunity_end_date > datetime.datetime.now()
            ):
                # Get remaining time
                remaining_time = get_remaining_duration(target_user.fight_immunity_end_date)
                message_text += phrases.SHOW_USER_STATUS_FIGHT_IMMUNITY.format(remaining_time)

            # Add fight cooldown if active
            if (
                target_user.fight_cooldown_end_date is not None
                and target_user.fight_cooldown_end_date > datetime.datetime.now()
            ):
                # Get remaining time
                remaining_time = get_remaining_duration(target_user.fight_cooldown_end_date)
                message_text += phrases.SHOW_USER_STATUS_FIGHT_COOLDOWN.format(remaining_time)

            # Add plunder immunity if active
            if (
                target_user.plunder_immunity_end_date is not None
                and target_user.plunder_immunity_end_date > datetime.datetime.now()
            ):
                # Get remaining time
                remaining_time = get_remaining_duration(target_user.plunder_immunity_end_date)
                message_text += phrases.SHOW_USER_STATUS_PLUNDER_IMMUNITY.format(remaining_time)

            # Add plunder cooldown if active
            if (
                target_user.plunder_cooldown_end_date is not None
                and target_user.plunder_cooldown_end_date > datetime.datetime.now()
            ):
                # Get remaining time
                remaining_time = get_remaining_duration(target_user.plunder_cooldown_end_date)
                message_text += phrases.SHOW_USER_STATUS_PLUNDER_COOLDOWN.format(remaining_time)

            # Add warlord remaining time if available
            if target_user.is_warlord():
                remaining_time = get_remaining_duration(
                    Warlord.get_latest_active_by_user(target_user).end_date
                )
                message_text += phrases.SHOW_USER_STATUS_WARLORD_REMAINING_TIME.format(
                    remaining_time
                )

            # BOUNTY DEDUCTIONS
            has_bounty_deduction = False
            bounty_deduction_text = phrases.SHOW_USER_STATUS_BOUNTY_DEDUCTIONS_TITLE

            # Expired loan
            if target_user.has_expired_bounty_loans():
                bounty_deduction_text += phrases.SHOW_USER_STATUS_BOUNTY_DEDUCTIONS_TEXT.format(
                    Emoji.LOG_NEGATIVE,
                    phrases.SHOW_USER_STATUS_EXPIRED_LOAN,
                    (-1 * target_user.get_expired_bounty_loans_cumulative_percentage()),
                )
                has_bounty_deduction = True

            # Income tax
            if target_user.has_income_tax() and not user_has_complete_tax_deduction(target_user):
                bounty_deduction_text += phrases.SHOW_USER_STATUS_BOUNTY_DEDUCTIONS_TEXT.format(
                    Emoji.LOG_NEGATIVE,
                    phrases.SHOW_USER_STATUS_INCOME_TAX,
                    (-1 * target_user.get_income_tax_percentage()),
                )
                has_bounty_deduction = True

            if has_bounty_deduction:
                message_text += bounty_deduction_text

            # Abilities visible only if checking own status
            if self_status:
                # Devil Fruit
                eaten_devil_fruit = DevilFruit.get_by_owner_if_eaten(target_user)
                if eaten_devil_fruit is not None:
                    message_text += phrases.SHOW_USER_STATUS_DEVIL_FRUIT.format(
                        eaten_devil_fruit.get_full_name(),
                        get_devil_fruit_abilities_text(eaten_devil_fruit, add_header=False),
                    )

                # Crew abilities
                if target_user.is_crew_member():
                    crew: Crew = target_user.crew
                    crew_active_abilities = crew.get_active_abilities()
                    if len(crew_active_abilities) > 0:
                        message_text += phrases.SHOW_USER_STATUS_CREW_ABILITIES.format(
                            get_crew_abilities_text(
                                active_abilities=crew_active_abilities, add_emoji=True
                            )
                        )

        if self_status:
            if target_user.can_collect_daily_reward:
                message_text += phrases.SHOW_USER_STATUS_DAILY_REWARD

    # If used in reply to a message, reply to original message
    reply_to_message_id = None
    if not self_status:
        message_text += "\n\n" + phrases.SHOW_USER_STATUS_ADD_REPLY.format(
            user.get_markdown_mention()
        )
        reply_to_message_id = update.effective_message.reply_to_message.message_id

    # Send bounty poster if not in reply to a message bounty_poster_limit is -1 or higher than 0
    # and user is not jailed

    if should_send_poster(target_user, group_chat, self_status):
        await send_bounty_poster(context, update, target_user, message_text, reply_to_message_id)

        # Reduce bounty poster limit by 1 if it is not None
        if not user_is_boss(target_user, group_chat=group_chat):
            target_user.bounty_poster_limit -= 1
            target_user.save()
            user.should_update_model = False

    else:  # Send regular message
        await full_message_send(
            context,
            message_text,
            update,
            reply_to_message_id=reply_to_message_id,
            add_delete_button=(inbound_keyboard is None),
            authorized_users=can_delete_users,
            inbound_keyboard=inbound_keyboard,
            keyboard=inline_keyboard,
        )


async def send_bounty_poster(
    context: ContextTypes.DEFAULT_TYPE,
    update: Update,
    user: User,
    caption: str = None,
    reply_to_message_id: int = None,
    send_in_private_chat=False,
) -> None:
    poster_path = await get_bounty_poster(update, user)
    poster: SavedMedia = SavedMedia(media_type=SavedMediaType.PHOTO)
    with open(poster_path, "rb") as media_id:
        poster.media_id = media_id.read()

    await full_media_send(
        context,
        saved_media=poster,
        update=update,
        caption=caption,
        reply_to_message_id=reply_to_message_id,
        new_message=True,
        add_delete_button=True,
        send_in_private_chat=send_in_private_chat,
    )


def should_send_poster(user: User, group_chat: GroupChat, is_own_status: bool) -> bool:
    """
    Returns True if the user should send a bounty poster
    :param user: The user
    :param group_chat: The group chat
    :param is_own_status: True if the status is the user's own status
    :return: True if the user should send a bounty poster
    """

    if not is_own_status:
        return False

    if user.is_arrested():
        return False

    boss_type = get_boss_type(user, group_chat=group_chat)
    if boss_type in (BossType.ADMIN, BossType.PIRATE_KING, BossType.LEGENDARY_PIRATE):
        return True

    if user.bounty_poster_limit == 0:
        return False

    return True
