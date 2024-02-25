from telegram import Update, Message
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.chat.group.screens.screen_daily_reward_prize import send_prize_request
from src.model.DailyReward import DailyReward
from src.model.DevilFruit import DevilFruit
from src.model.DevilFruitTrade import DevilFruitTrade
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.Screen import Screen
from src.model.enums.daily_reward.DailyRewardBonus import DailyRewardBonus
from src.model.enums.daily_reward.DailyRewardLimitation import DailyRewardLimitation
from src.model.enums.devil_fruit.DevilFruitSource import DevilFruitSource
from src.service.bounty_service import add_or_remove_bounty
from src.service.daily_reward_service import get_text
from src.service.date_service import is_same_day, get_next_run
from src.service.message_service import (
    full_message_send,
    get_deeplink,
    get_message_url,
    full_media_send,
)
from src.utils.english_phrase_utils import day_or_days
from src.utils.string_utils import object_to_json_string, get_belly_formatted


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    group_chat: GroupChat,
) -> None:
    """
    Displays a user's status
    :param update: Telegram update
    :param context: Telegram context
    :param user: User
    :param group_chat: Group chat
    :return: None
    """

    # Devil Fruit Shop items
    df_trade_shop_items = DevilFruitTrade.get_all_selling_in_shop_or_group(
        group_chat=group_chat, user=user
    )
    extra_text = ""
    df_items_text = ""
    if len(df_trade_shop_items) > 0:
        for df_trade in df_trade_shop_items:
            df: DevilFruit = df_trade.devil_fruit

            # Add deeplink
            if df_trade.get_source() is DevilFruitSource.USER:  # Group message url
                url = get_message_url(df_trade.message_id, group_chat=df_trade.group_chat)
            else:
                url = get_deeplink(
                    info={ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY: df_trade.id},
                    screen=Screen.PVT_DEVIL_FRUIT_SHOP_DETAIL,
                    previous_screens=[Screen.PVT_DEVIL_FRUIT_SHOP],
                )

            df_items_text += phrases.DAILY_REWARD_DEVIL_FRUIT_SHOP_ITEM.format(
                df.get_full_name(), get_belly_formatted(df_trade.price), url
            )
        extra_text += phrases.DAILY_REWARD_DEVIL_FRUIT_SHOP.format(df_items_text)

    # Already used
    if not user.can_collect_daily_reward:
        ot_text = phrases.DAILY_REWARD_ALREADY_COLLECTED.format(
            DailyReward.get_remaining_time_to_next_reward(), extra_text
        )
        await full_message_send(context, ot_text, update=update, add_delete_button=True)
        return

    reward_parts: int = DailyReward.get_daily_reward_reset_times()
    base_amount: int = int(Env.DAILY_REWARD_BONUS_BASE_AMOUNT.get_int() / reward_parts)
    # Get all bonus_list

    reward: DailyReward = DailyReward()
    reward.user = user
    reward.base_amount = base_amount
    bonus_list: list[DailyRewardBonus] = []

    # Setting limitations or bonuses.
    # User has limitations (they will get only the base amount) if:
    # - They are in Paradise and have enough bounty to go to New World
    # - They are in the final New World location and have the bounty required to be there
    # - They are temporarily arrested
    if user.has_bounty_gain_limitations():
        reward.limitation = (
            DailyRewardLimitation.LOCATION_PARADISE
            if user.is_in_paradise()
            else DailyRewardLimitation.LOCATION_NEW_WORLD
        )
    elif user.is_arrested_temporary():
        reward.limitation = DailyRewardLimitation.ARRESTED
    else:
        bonus_list = DailyReward.get_bonuses_for_user(user, base_amount)

    reward.bonus_list = object_to_json_string(bonus_list)
    reward.total_amount = base_amount + sum([bonus.amount for bonus in bonus_list])
    reward.streak_count = DailyReward.get_user_streak_count(user)
    reward.group_chat = group_chat
    reward.save()

    # Add to user bounty
    await add_or_remove_bounty(
        user,
        reward.total_amount,
        should_tax=False,
        update=update,
        context=context,
        should_update_location=True,
    )
    user.can_collect_daily_reward = False
    user.save()

    # Send message
    days_to_next_prize = reward.get_days_to_next_prize()
    ot_text = phrases.DAILY_REWARD_GROUP_MESSAGE.format(
        user.get_markdown_mention(),
        get_text(reward),
        reward.streak_count,
        day_or_days(reward.streak_count),
        days_to_next_prize,
        day_or_days(days_to_next_prize),
    )

    # Daily reward split message
    # Next run of cron is still today, show split message
    if is_same_day(get_next_run(Env.CRON_DAILY_REWARD.get())):
        ot_text += phrases.DAILY_REWARD_NEXT_SPLIT.format(
            reward_parts, DailyReward.get_remaining_time_to_next_reward()
        )
    else:
        ot_text += phrases.DAILY_REWARD_NEXT.format(
            DailyReward.get_remaining_time_to_next_reward()
        )

    ot_text += extra_text

    message: Message = await full_media_send(
        context,
        saved_media_name=SavedMediaName.DAILY_REWARD,
        update=update,
        caption=ot_text,
        add_delete_button=True,
    )

    reward.message_id = message.id
    reward.save()

    # Prize day
    if reward.should_award_prize():
        await send_prize_request(context, update, reward)
