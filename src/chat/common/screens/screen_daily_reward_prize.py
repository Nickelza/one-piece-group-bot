from telegram import Update, Message
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.DailyReward import DailyReward
from src.model.DevilFruit import DevilFruit
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.enums.daily_reward.DailyRewardPrizeSource import DailyRewardPrizeSource
from src.model.enums.daily_reward.DailyRewardPrizeType import DailyRewardPrizeType
from src.model.enums.devil_fruit.DevilFruitSource import DevilFruitSource
from src.model.error.CommonChatError import CommonChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import add_or_remove_bounty
from src.service.devil_fruit_service import (
    give_devil_fruit_to_user,
    create_smile,
    get_recap_text,
    get_manage_deeplink_keyboard,
)
from src.service.message_service import (
    full_message_send,
)
from src.utils.math_utils import get_random_int
from src.utils.string_utils import get_belly_formatted


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
) -> None:
    """
    Displays a user's status
    :param update: Telegram update
    :param context: Telegram context
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    reward: DailyReward = DailyReward.get_by_id(
        inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY)
    )

    if reward.prize_type is not None:
        raise CommonChatException(phrases.ITEM_IN_WRONG_STATUS)

    prize_source: DailyRewardPrizeSource = DailyRewardPrizeSource(
        inbound_keyboard.get(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY)
    )

    prize_type, prize_value = get_prize(reward, prize_source)

    inline_keyboard: list[list[Keyboard]] = []
    if prize_type is DailyRewardPrizeType.BELLY:
        await add_or_remove_bounty(reward.user, prize_value, should_save=True, should_tax=False)
        prize_text = phrases.DAILY_REWARD_PRIZE_CONFIRM_BELLY.format(
            get_belly_formatted(int(prize_value))
        )
    else:  # SMILE
        devil_fruit: DevilFruit = DevilFruit.get_by_id(prize_value)
        give_devil_fruit_to_user(devil_fruit, reward.user, DevilFruitSource.DAILY_REWARD_PRIZE)
        prize_text = get_recap_text(devil_fruit, add_sell_command=True)

        # Add manage
        inline_keyboard.append([get_manage_deeplink_keyboard(devil_fruit)])

    reward.prize_type, reward.prize_value = prize_type, str(prize_value)
    reward.save()

    ot_text = phrases.DAILY_REWARD_PRIZE_CONFIRM.format(
        reward.user.get_markdown_mention(), prize_text
    )

    await full_message_send(
        context, ot_text, update=update, keyboard=inline_keyboard, add_delete_button=True
    )


async def send_prize_request(
    context: ContextTypes.DEFAULT_TYPE, update: Update, reward: DailyReward
):
    """
    Sends the prize request
    :param context: Telegram context
    :param update: Telegram update
    :param reward: The reward
    """

    prefix_text = (
        phrases.DAILY_REWARD_PRIZE_REQUEST_FIRST_TIME
        if DailyReward.get_reward_count_for_user(reward.user) == 1
        else phrases.DAILY_REWARD_PRIZE_REQUEST_FROM_STREAK
    )

    ot_text = phrases.DAILY_REWARD_PRIZE_REQUEST.format(
        prefix_text.format(reward.user.get_markdown_mention()),
        get_belly_formatted(reward.get_base_belly_prize_offer()),
        get_belly_formatted(reward.get_minimum_belly_prize()),
        get_belly_formatted(reward.get_maximum_belly_prize()),
    )

    # Accept offer and random prize keyboard
    screen = (
        Screen.GRP_DAILY_REWARD_PRIZE
        if reward.group_chat is not None
        else Screen.PVT_DAILY_REWARD_PRIZE
    )
    inline_keyboard: list[list[Keyboard]] = [
        [
            Keyboard(
                phrases.GRP_KEY_DAILY_REWARD_PRIZE_ACCEPT,
                info={
                    ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: reward.id,
                    ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY: DailyRewardPrizeSource.OFFER,
                },
                screen=screen,
            )
        ],
        [
            Keyboard(
                phrases.GRP_KEY_DAILY_REWARD_PRIZE_RANDOM,
                info={
                    ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: reward.id,
                    ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY: DailyRewardPrizeSource.RANDOM,
                },
                screen=screen,
            )
        ],
    ]

    message: Message = await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=inline_keyboard,
    )

    reward.message_id_prize = message.id
    reward.save()


def get_prize(
    reward: DailyReward, prize_source: DailyRewardPrizeSource
) -> tuple[DailyRewardPrizeType, any]:
    """
    Get the prize
    :param reward: The reward
    :param prize_source: The prize source
    :return: The prize type and value
    """

    if prize_source not in [DailyRewardPrizeSource.OFFER, DailyRewardPrizeSource.RANDOM]:
        raise ValueError(f"Invalid prize source {prize_source}")

    # Accepted offer
    if prize_source is DailyRewardPrizeSource.OFFER:
        return DailyRewardPrizeType.BELLY, reward.get_base_belly_prize_offer()

    # Random
    prize_type = DailyRewardPrizeType.get_random()

    if prize_type not in [DailyRewardPrizeType.BELLY, DailyRewardPrizeType.SMILE]:
        raise ValueError(f"Invalid prize type {prize_type}")

    # Belly
    if prize_type is DailyRewardPrizeType.BELLY:
        prize_value = get_random_int(
            reward.get_minimum_belly_prize(), reward.get_maximum_belly_prize()
        )
        return prize_type, prize_value

    # SMILE
    # Generate random SMILE and give to User
    devil_fruit: DevilFruit = create_smile()
    prize_value = devil_fruit.id

    return prize_type, prize_value
