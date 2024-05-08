import datetime
import random
from enum import StrEnum
from math import ceil

from peewee import fn
from telegram import Update, Message
from telegram.ext import ContextTypes

from resources import phrases, Environment as Env
from src.model.BountyLoan import BountyLoan
from src.model.Fight import Fight
from src.model.GroupChat import GroupChat
from src.model.Plunder import Plunder
from src.model.User import User
from src.model.enums.BountyLoanSource import BountyLoanSource
from src.model.enums.GameStatus import GameStatus
from src.model.enums.LeaderboardRank import get_rank_by_leaderboard_user
from src.model.enums.Notification import FightAttackNotification, PlunderAttackNotification
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.ScoutType import ScoutType
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.enums.impel_down.ImpelDownBountyAction import ImpelDownBountyAction
from src.model.enums.impel_down.ImpelDownSentenceType import ImpelDownSentenceType
from src.model.enums.impel_down.ImpelDownSource import ImpelDownSource
from src.model.enums.income_tax.IncomeTaxEventType import IncomeTaxEventType
from src.model.error.CustomException import OpponentValidationException
from src.model.error.GroupChatError import GroupChatException, GroupChatError
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_loan_service import add_loan
from src.service.bounty_service import add_or_remove_bounty
from src.service.date_service import (
    convert_hours_to_duration,
    convert_seconds_to_duration,
    datetime_is_after,
    get_elapsed_hours,
    get_datetime_in_future_hours,
)
from src.service.devil_fruit_service import get_ability_value, get_ability_adjusted_datetime
from src.service.impel_down_service import add_sentence
from src.service.leaderboard_service import get_current_leaderboard_user
from src.service.message_service import (
    get_yes_no_keyboard,
    full_media_send,
    delete_message,
    full_message_or_media_send_or_edit,
    full_message_send,
    mention_markdown_v2,
    mention_markdown_user,
)
from src.service.notification_service import send_notification
from src.utils.math_utils import add_percentage_to_value, get_value_from_percentage, get_random_win
from src.utils.string_utils import get_belly_formatted


class FightPlunderReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    ITEM_ID = ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY
    OPPONENT_ID = ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY
    USED_OPPONENTS_IDS = "c"


def get_scout_fee(user: User, is_group: bool, scout_type: ScoutType) -> int:
    """
    Get the scout price
    :param user: The user
    :param is_group: If the scout is for a group
    :param scout_type: The scout type
    :return: The scout price
    """

    price: int = Env.FIGHT_PLUNDER_SCOUT_BASE_PRICE.get_int()

    # Multiply the price by the user's location level
    price *= user.location_level

    # Add group multiplier
    if is_group:
        price *= Env.FIGHT_PLUNDER_SCOUT_FEE_MULTIPLIER_GROUP.get_float()

    # Add scout count multiplier
    if scout_type is ScoutType.FIGHT:
        if user.fight_scout_count > 0:
            price = int(add_percentage_to_value(price, user.fight_scout_count - 1))
        price = int(add_percentage_to_value(price, user.fight_scout_count))
    else:
        if user.fight_scout_count > 0:
            price = int(add_percentage_to_value(price, user.fight_scout_count - 1))
        price = int(add_percentage_to_value(price, user.plunder_scout_count))

    # Adjust by Devil Fruit ability
    price = int(get_ability_value(user, DevilFruitAbilityType.FIGHT_PLUNDER_SCOUT_FEE, price))

    return price


async def group_send_scout_request(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, scout_type: ScoutType
) -> None:
    """
    Send request to confirm fight
    :param update: The update
    :param context: The context
    :param user: The user
    :param scout_type: The scout type
    :return: None
    """

    opponent: User = get_opponent(update)
    caption = phrases.FIGHT_PLUNDER_SCOUT_USER_GROUP.format(
        opponent.get_markdown_mention(),
        get_belly_formatted(get_scout_fee(user, False, scout_type)),
    )

    # Keyboard
    inline_keyboard: list[list[Keyboard]] = [
        get_yes_no_keyboard(
            user,
            screen=Screen.GRP_FIGHT if scout_type is ScoutType.FIGHT else Screen.GRP_PLUNDER,
            yes_text=phrases.KEYBOARD_OPTION_SCOUT,
            no_text=phrases.KEYBOARD_OPTION_RETREAT,
            no_is_delete_button=True,
            yes_extra_keys={FightPlunderReservedKeys.OPPONENT_ID: opponent.id},
        )
    ]

    await full_media_send(
        context,
        saved_media_name=SavedMediaName.FIGHT_PLUNDER_SCOUT,
        update=update,
        caption=caption,
        keyboard=inline_keyboard,
        add_delete_button=True,
    )


async def private_send_scout_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    scout_type: ScoutType,
    is_new_scout: bool,
    inbound_keyboard: Keyboard,
    opponent: User = None,
) -> None:
    """
    Send request to confirm fight
    :param update: The update
    :param context: The context
    :param user: The user
    :param scout_type: The scout type
    :param is_new_scout: If the scout is new, so add scout count and deduct fee
    :param inbound_keyboard: The inbound keyboard
    :param opponent: The opponent
    :return: None
    """

    scout_fee = get_scout_fee(user, False, scout_type)
    # Keyboard
    inline_keyboard: list[list[Keyboard]] = []

    # First scout
    if opponent is None:
        caption = phrases.FIGHT_PLUNDER_SCOUT_SEARCH.format(
            get_belly_formatted(scout_fee), user.get_bounty_formatted()
        )

        inline_keyboard.append(
            get_yes_no_keyboard(
                user,
                screen=Screen.PVT_FIGHT if scout_type is ScoutType.FIGHT else Screen.PVT_PLUNDER,
                yes_text=phrases.KEYBOARD_OPTION_SCOUT,
                exclude_no_button=True,
            )
        )
    else:  # Scout opponent
        potential_jail_time_text = ""
        if scout_type is ScoutType.FIGHT:
            win_probability, win_amount, lose_amount, final_bounty_if_win, final_bounty_if_lose = (
                fight_get_odds(user, opponent)
            )
            if is_new_scout:
                user.fight_scout_count += 1
        else:
            pass
            (
                win_probability,
                win_amount,
                lose_amount,
                win_percentage,
                final_bounty_if_win,
                final_bounty_if_lose,
                sentence,
            ) = plunder_get_odds(user, opponent)
            potential_jail_time_text = phrases.FIGHT_PLUNDER_SCOUT_USER_JAIL_TIME.format(
                convert_hours_to_duration(sentence)
            )
            if is_new_scout:
                user.plunder_scout_count += 1

        if is_new_scout:
            await add_or_remove_bounty(user, scout_fee, add=False)
            # Delete all previous private chat fights
            Fight.delete().where(
                (Fight.challenger == user)
                & (Fight.status == GameStatus.IN_PROGRESS)
                & (Fight.group_chat.is_null())
            ).execute()

        # Set list of used ids
        used_opponent_ids = [opponent.id]
        if inbound_keyboard.has_key(FightPlunderReservedKeys.USED_OPPONENTS_IDS):
            used_opponent_ids.extend(
                inbound_keyboard.get(FightPlunderReservedKeys.USED_OPPONENTS_IDS)
            )
            # Remove duplicates
            used_opponent_ids = list(set(used_opponent_ids))

        next_scout_fee = get_scout_fee(user, False, scout_type)
        caption = phrases.FIGHT_PLUNDER_SCOUT_SEARCH_USER.format(
            opponent.get_markdown_name(),
            win_probability,
            get_belly_formatted(win_amount),
            get_belly_formatted(lose_amount),
            potential_jail_time_text,
            get_belly_formatted(next_scout_fee),
            user.get_bounty_formatted(),
        )

        inline_keyboard.append(
            get_yes_no_keyboard(
                user,
                screen=Screen.PVT_FIGHT if scout_type is ScoutType.FIGHT else Screen.PVT_PLUNDER,
                yes_text=phrases.KEYBOARD_OPTION_CHOOSE,
                exclude_no_button=True,
                extra_keys={
                    FightPlunderReservedKeys.OPPONENT_ID: opponent.id,
                    FightPlunderReservedKeys.USED_OPPONENTS_IDS: used_opponent_ids,
                },
            )
        )

        # Next scout keyboard
        inline_keyboard.append([
            Keyboard(
                phrases.KEYBOARD_OPTION_NEW_SCOUT,
                screen=Screen.PVT_FIGHT if scout_type is ScoutType.FIGHT else Screen.PVT_PLUNDER,
                inbound_info=inbound_keyboard.info,
                info={FightPlunderReservedKeys.USED_OPPONENTS_IDS: used_opponent_ids},
                exclude_key_from_inbound_info=[
                    FightPlunderReservedKeys.ITEM_ID,
                    FightPlunderReservedKeys.OPPONENT_ID,
                ],
            )
        ])

    if is_new_scout and opponent is not None:
        caption = phrases.FIGHT_PLUNDER_SCOUT_SEARCH_USER_NEW + caption

    await full_media_send(
        context,
        saved_media_name=SavedMediaName.FIGHT_PLUNDER_SCOUT,
        update=update,
        caption=caption,
        keyboard=inline_keyboard,
        add_delete_button=True,
        delete_button_text=phrases.KEYBOARD_OPTION_CANCEL,
        new_message=(opponent is None),
    )


async def private_send_no_opponent_found(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Send no opponent found message
    :param update: The update
    :param context: The context
    :return: None
    """
    await full_media_send(
        context,
        saved_media_name=SavedMediaName.FIGHT_PLUNDER_SCOUT,
        update=update,
        caption=phrases.FIGHT_PLUNDER_SCOUT_NO_OPPONENT_FOUND,
        add_delete_button=True,
    )


async def private_manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    inbound_keyboard: Keyboard,
    scout_type: ScoutType,
) -> None:
    """
    Manage the fight request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :param scout_type: The scout type
    :return: None
    """

    # First scout, no confirm in the keyboard and no opponent
    if not inbound_keyboard.has_key(ReservedKeyboardKeys.CONFIRM) and not inbound_keyboard.has_key(
        FightPlunderReservedKeys.OPPONENT_ID
    ):
        await private_send_scout_request(update, context, user, scout_type, True, inbound_keyboard)
        return

    # Next scout, confirm in the keyboard and no opponent
    if inbound_keyboard.has_key(ReservedKeyboardKeys.CONFIRM) and not inbound_keyboard.has_key(
        FightPlunderReservedKeys.OPPONENT_ID
    ):
        # Find the opponent
        used_user_ids: list[int] = []
        if inbound_keyboard.has_key(FightPlunderReservedKeys.USED_OPPONENTS_IDS):
            used_user_ids = inbound_keyboard.get(FightPlunderReservedKeys.USED_OPPONENTS_IDS)

        opponent = find_random_opponent(user, used_user_ids, scout_type)
        if opponent is None:
            await private_send_no_opponent_found(update, context)
            return

        # Send the opponent with recap
        await private_send_scout_request(
            update, context, user, scout_type, True, inbound_keyboard, opponent
        )
        return

    # Opponent selection, confirm and opponent in keyboard, no fight
    if (
        inbound_keyboard.has_key(ReservedKeyboardKeys.CONFIRM)
        and inbound_keyboard.has_key(FightPlunderReservedKeys.OPPONENT_ID)
        and not inbound_keyboard.has_key(FightPlunderReservedKeys.ITEM_ID)
    ):
        if scout_type is scout_type.FIGHT:
            await fight_send_request(update, context, user, inbound_keyboard)
        else:
            await plunder_send_request(update, context, user, inbound_keyboard)
        return

    # Fight confirmation, confirm and fight in keyboard
    if inbound_keyboard.has_key(ReservedKeyboardKeys.CONFIRM) and inbound_keyboard.has_key(
        FightPlunderReservedKeys.ITEM_ID
    ):
        if scout_type is scout_type.FIGHT:
            await fight_confirm_request(update, context, user, inbound_keyboard)
        else:
            await plunder_confirm_request(update, context, user, inbound_keyboard)
        return

    raise ValueError("Invalid keyboard")


def get_opponent(update: Update = None, keyboard: Keyboard = None) -> User | None:
    """
    Get opponent from update or keyboard
    :param update: The update object. If None, the opponent is taken from the keyboard
    :param keyboard: The keyboard object. If None, the opponent is taken from the update
    :return: The opponent object
    """

    if update.callback_query is None:
        return User.get_or_none(User.tg_user_id == update.message.reply_to_message.from_user.id)

    return User.get_by_id(int(keyboard.get_int(FightPlunderReservedKeys.OPPONENT_ID)))


def decrease_scout_count():
    """
    Decrease the scout count
    :return: None
    """

    (
        User.update(fight_scout_count=User.fight_scout_count - 1)
        .where(User.fight_scout_count > 0)
        .execute()
    )

    (
        User.update(plunder_scout_count=User.plunder_scout_count - 1)
        .where(User.plunder_scout_count > 0)
        .execute()
    )


async def delete_item_in_group(
    context: ContextTypes.DEFAULT_TYPE, item: Plunder | Fight, group_chat: GroupChat
) -> None:
    """
    Delete plunder
    :param context: The context
    :param item: The item
    :param group_chat: The group chat
    :return: None
    """
    # Try to delete message
    await delete_message(context=context, group_chat=group_chat, message_id=item.message_id)

    # Delete plunder
    item.delete_instance()


def find_random_opponent(
    player: User, exclude_user_ids: list[int], scout_type: ScoutType
) -> User | None:
    """
    Find a fight opponent, a random player with the required conditions
    :param player: The user
    :param exclude_user_ids: The list of already used opponents
    :param scout_type: The scout type
    :return: The opponent
    """

    now = datetime.datetime.now()

    if scout_type is ScoutType.FIGHT:
        immunity_condition = (User.fight_immunity_end_date.is_null()) | (
            User.fight_immunity_end_date < now
        )
        # Order by difference in location level and difference in bounty
        order_by_condition = (
            fn.abs(User.location_level - player.location_level).asc(),
            fn.abs(User.bounty - player.bounty).asc(),
        )
    else:
        immunity_condition = (User.plunder_immunity_end_date.is_null()) | (
            User.plunder_immunity_end_date < now
        )
        # Order by difference in location level and last interaction
        order_by_condition = (
            fn.abs(User.location_level - player.location_level).asc(),
            User.last_system_interaction_date.asc(),
        )

    # Get random user in minimum required location, without immunity, not arrested, not admin
    # and bounty > 1000
    # Get first 10 in list and select one randomly, add selected to list of already used opponents
    eligible_users = list(
        User.select()
        .where(
            (User.location_level >= Env.REQUIRED_LOCATION_LEVEL_FIGHT.get_int())
            & immunity_condition
            & (User.get_is_not_arrested_statement_condition())
            & (User.is_admin == False)
            & (User.bounty > 1000)
            & (User.id.not_in(exclude_user_ids))
            & (User.id != player.id)
        )
        .order_by(*order_by_condition)
        .limit(10)
    )

    if len(eligible_users) == 0:
        return None

    # Return a random user
    return random.choice(eligible_users)


def fight_get_odds(challenger: User, opponent: User) -> tuple[float, int, int, int, int]:
    """
    Get the win probability
    :param challenger: The challenger object
    :param opponent: The opponent object
    :return: list -  [0] - Win probability, [1] - Win amount, [2] - Lose amount
            [3] - Final bounty if user win, [4] - Final bounty if user lose
    """
    # Probability of winning - How much percent more is the challenger bounty compared to the
    # opponent
    win_probability = (challenger.bounty / opponent.get_max_bounty()) * 50

    # Cap max probability
    leaderboard_user = get_current_leaderboard_user(challenger)
    leaderboard_rank = get_rank_by_leaderboard_user(leaderboard_user)
    # Use minimum probability if the probability is too low
    win_probability = max(win_probability, leaderboard_rank.min_win_probability)
    # Use maximum probability if the probability is too high
    win_probability = min(win_probability, leaderboard_rank.max_win_probability)
    # Final location cap
    if challenger.has_bounty_gain_limitations():
        win_probability = min(
            win_probability, Env.FIGHT_MAX_WIN_PROBABILITY_FINAL_LOCATION.get_float()
        )

    lose_probability = 100 - win_probability

    # Recalculate opponent win probability with Devil Fruit ability
    opponent_win_probability = get_ability_value(
        opponent, DevilFruitAbilityType.FIGHT_DEFENSE_BOOST, lose_probability, add_to_value=True
    )
    # Cap opponent win probability to max allowed for Devil Fruit boost
    opponent_win_probability = round(
        min(
            opponent_win_probability,
            Env.FIGHT_MAX_WIN_PROBABILITY_DEVIL_FRUIT_DEFENSE_BOOST.get_float(),
        ),
        2,
    )
    win_probability, lose_probability = 100 - opponent_win_probability, opponent_win_probability

    # Win amount is the amount from opponent bounty corresponding to lose probability
    win_amount = int(get_value_from_percentage(opponent.bounty, lose_probability))
    # Lose amount is the amount from challenger bounty corresponding to maximum between win and
    # lose probability
    lose_amount = int(
        get_value_from_percentage(challenger.bounty, max(win_probability, lose_probability))
    )

    final_bounty_if_won = challenger.bounty + win_amount
    final_bounty_if_lose = challenger.bounty - lose_amount

    return win_probability, win_amount, lose_amount, final_bounty_if_won, final_bounty_if_lose


# noinspection DuplicatedCode
# Duplicated by plunder validate
async def fight_validate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    is_group: bool,
    keyboard: Keyboard = None,
) -> bool:
    """
    Validate the fight request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param is_group: If the fight is for a group
    :param keyboard: The keyboard object
    :return: True if the request is valid, False otherwise
    """
    # If not query callback
    fight: Fight | None = None
    if update.callback_query is not None and keyboard.has_key(FightPlunderReservedKeys.ITEM_ID):
        fight: Fight = Fight.get_or_none(
            Fight.id == int(keyboard.info[FightPlunderReservedKeys.ITEM_ID])
        )
        if fight is None:
            raise GroupChatException(GroupChatError.ITEM_NOT_FOUND)

    now = datetime.datetime.now()

    # User is in fight cooldown
    if user.fight_cooldown_end_date is not None and user.fight_cooldown_end_date > now:
        # Get remaining time
        remaining_time = convert_seconds_to_duration(
            (user.fight_cooldown_end_date - datetime.datetime.now()).total_seconds()
        )
        ot_text = phrases.FIGHT_USER_IN_COOLDOWN.format(remaining_time)
        await full_message_or_media_send_or_edit(context, ot_text, update, add_delete_button=True)
        return False

    # User does not have enough amount to scout
    scout_fee = get_scout_fee(user, is_group, ScoutType.FIGHT)
    if user.bounty < scout_fee:
        ot_text = (
            phrases.FIGHT_PLUNDER_GROUP_INSUFFICIENT_SCOUT_BOUNTY
            if is_group
            else phrases.FIGHT_PLUNDER_PRIVATE_INSUFFICIENT_SCOUT_BOUNTY
        ).format(get_belly_formatted(scout_fee), user.get_bounty_formatted())
        await full_message_or_media_send_or_edit(context, ot_text, update, add_delete_button=True)
        return False

    # Wrong status
    if fight is not None and fight.get_status() is not GameStatus.IN_PROGRESS:
        raise GroupChatException(GroupChatError.ITEM_IN_WRONG_STATUS)

    # Opponent not yet available
    if not is_group and not keyboard.has_key(FightPlunderReservedKeys.OPPONENT_ID):
        return True

    # Opponent validation
    try:
        # Get opponent
        opponent: User = get_opponent(update, keyboard)

        # If opponent is not found, send error
        if opponent is None:
            raise OpponentValidationException(GroupChatError.FIGHT_OPPONENT_NOT_FOUND.build())

        # Opponent is not in the minimum required location
        if opponent.location_level < Env.REQUIRED_LOCATION_LEVEL_FIGHT.get_int():
            raise OpponentValidationException()

        # Opponent has fight immunity
        if datetime_is_after(opponent.fight_immunity_end_date):
            raise OpponentValidationException()

        # Opponent is arrested
        if opponent.is_arrested():
            raise OpponentValidationException()

    except OpponentValidationException as ove:
        if ove.message is not None:
            await full_message_or_media_send_or_edit(context, ove.message, update)
        else:
            await full_message_or_media_send_or_edit(
                context, phrases.FIGHT_CANNOT_FIGHT_USER, update=update, add_delete_button=True
            )
        return False

    return True


async def fight_send_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    keyboard: Keyboard,
    group_chat: GroupChat = None,
) -> None:
    """
    Send request to confirm fight
    :param update: The update
    :param context: The context
    :param user: The user
    :param keyboard: The keyboard
    :param group_chat: The group chat
    :return: None
    """
    if group_chat is not None:
        # Remove scouting fee, if not from private
        await add_or_remove_bounty(user, get_scout_fee(user, True, ScoutType.FIGHT), add=False)
        user.fight_scout_count += 1

        # Delete all previous pending fights
        previous_fights: list[Fight] = Fight.select().where(
            (Fight.challenger == user) & (Fight.status == GameStatus.IN_PROGRESS)
        )
        for previous_fight in previous_fights:
            await delete_item_in_group(context, previous_fight, group_chat)

    # Get opponent
    opponent: User = get_opponent(update, keyboard)
    win_probability, win_amount, lose_amount, final_bounty_if_win, final_bounty_if_lose = (
        fight_get_odds(user, opponent)
    )

    # Create fight
    fight: Fight = Fight()
    fight.challenger = user
    fight.opponent = opponent
    fight.win_probability = win_probability
    fight.belly = win_amount
    fight.group_chat = group_chat
    fight.save()

    if win_probability >= 50:
        outcome = phrases.FIGHT_CONFIRMATION_OUTCOME_VICTORY
        outcome_probability = win_probability
    else:
        outcome = phrases.FIGHT_CONFIRMATION_OUTCOME_DEFEAT
        outcome_probability = 100 - win_probability

    odds_recalculated_text = (
        phrases.FIGHT_CONFIRMATION_ODDS_RECALCULATED
        if opponent.is_crew_member() and not opponent.has_higher_bounty_than_crew_average()
        else ""
    )

    caption = phrases.FIGHT_CONFIRMATION_REQUEST.format(
        user.get_markdown_mention(),
        opponent.get_markdown_name(),
        outcome_probability,
        outcome,
        odds_recalculated_text,
        user.get_bounty_formatted(),
        get_belly_formatted(final_bounty_if_win),
        get_belly_formatted(final_bounty_if_lose),
    )

    # Keyboard
    # noinspection DuplicatedCode
    inline_keyboard: list[list[Keyboard]] = [
        get_yes_no_keyboard(
            user,
            screen=Screen.GRP_FIGHT if group_chat is not None else Screen.PVT_FIGHT,
            yes_text=phrases.KEYBOARD_OPTION_FIGHT,
            no_text=phrases.KEYBOARD_OPTION_RETREAT,
            primary_key=fight.id,
            inbound_keyboard=keyboard,
            add_inbound_key_info=True,
        )
    ]

    if group_chat is None:
        # Add new scout button
        inline_keyboard.append([
            Keyboard(
                phrases.KEYBOARD_OPTION_NEW_SCOUT,
                inbound_info=keyboard.info,
                exclude_key_from_inbound_info=[
                    FightPlunderReservedKeys.OPPONENT_ID,
                ],
                screen=Screen.PVT_FIGHT,
            )
        ])

        caption += phrases.FIGHT_PLUNDER_SCOUT_NEXT_FEE.format(
            get_belly_formatted(get_scout_fee(user, False, ScoutType.FIGHT))
        )

    message: Message = await full_media_send(
        context,
        saved_media_name=SavedMediaName.FIGHT,
        update=update,
        caption=caption,
        keyboard=inline_keyboard,
        add_delete_button=True,
        delete_button_text=phrases.KEYBOARD_OPTION_CANCEL,
    )

    fight.message_id = message.message_id
    fight.save()


async def fight_confirm_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    inbound_keyboard: Keyboard,
    group_chat: GroupChat = None,
) -> None:
    """
    Keyboard interaction
    :param update: The update
    :param context: The context
    :param user: The user
    :param inbound_keyboard: The keyboard
    :param group_chat: The group chat
    :return: None
    """

    # Get fight
    # noinspection DuplicatedCode
    # Duplicated by fight
    fight: Fight = Fight.get_or_none(
        Fight.id == inbound_keyboard.info[FightPlunderReservedKeys.ITEM_ID]
    )

    # User clicked on retreat button
    if not inbound_keyboard.info[ReservedKeyboardKeys.CONFIRM]:
        # In group, show retreat popup and exit
        if group_chat is not None:
            # Answer callback with retreat message
            await full_message_send(
                context, phrases.FIGHT_CONFIRMATION_RETREAT, update, answer_callback=True
            )
            return await delete_item_in_group(context, fight, group_chat)

        # In private chat, back to scouting
        opponent: User = fight.opponent
        fight.delete_instance()
        return await private_send_scout_request(
            update, context, user, ScoutType.FIGHT, False, inbound_keyboard, opponent
        )

    opponent: User = fight.opponent
    # Get fight odds
    win_probability, win_amount, lose_amount, final_bounty_if_win, final_bounty_if_lose = (
        fight_get_odds(user, opponent)
    )
    fight.win_probability = win_probability
    fight.date = datetime.datetime.now()

    if get_random_win(win_probability):  # Challenger won
        fight.status = GameStatus.WON
        fight.belly = win_amount
        # Add bounty to challenger
        await add_or_remove_bounty(
            user,
            win_amount,
            context=context,
            update=update,
            tax_event_type=IncomeTaxEventType.FIGHT,
            event_id=fight.id,
            should_save=True,
            opponent=user,
        )
        # Remove bounty from opponent
        await add_or_remove_bounty(
            opponent, win_amount, add=False, update=update, should_save=True
        )
        caption = phrases.FIGHT_WIN.format(
            mention_markdown_v2(user.tg_user_id, "you"),
            mention_markdown_user(opponent),
            get_belly_formatted(win_amount),
            user.get_bounty_formatted(),
        )
    else:  # Challenger lost
        fight.status = GameStatus.LOST
        fight.belly = lose_amount
        # Remove bounty from challenger
        await add_or_remove_bounty(user, lose_amount, add=False, update=update, should_save=True)
        # Add bounty to opponent
        await add_or_remove_bounty(
            opponent,
            lose_amount,
            context=context,
            update=update,
            tax_event_type=IncomeTaxEventType.FIGHT,
            event_id=fight.id,
            should_save=True,
            opponent=user,
        )
        caption = phrases.FIGHT_LOSE.format(
            mention_markdown_v2(user.tg_user_id, "you"),
            mention_markdown_user(opponent),
            get_belly_formatted(lose_amount),
            user.get_bounty_formatted(),
        )

    # Add fight immunity to opponent
    opponent.fight_immunity_end_date = get_ability_adjusted_datetime(
        opponent,
        DevilFruitAbilityType.FIGHT_IMMUNITY_DURATION,
        Env.FIGHT_IMMUNITY_DURATION.get_int(),
    )
    # Remove fight immunity from user
    user.fight_immunity_end_date = None

    # Add fight cooldown to user
    user.fight_cooldown_end_date = get_ability_adjusted_datetime(
        user, DevilFruitAbilityType.FIGHT_COOLDOWN_DURATION, Env.FIGHT_COOLDOWN_DURATION.get_int()
    )
    # Remove fight cooldown from opponent
    opponent.fight_cooldown_end_date = None

    inline_keyboard: list[list[Keyboard]] = []
    delete_button_text = None
    if group_chat is None:
        delete_button_text = phrases.KEYBOARD_OPTION_CLOSE
        caption += phrases.FIGHT_PLUNDER_SCOUT_NEXT_FEE.format(
            get_belly_formatted(get_scout_fee(user, False, ScoutType.FIGHT))
        )
        inline_keyboard.append([
            Keyboard(
                phrases.KEYBOARD_OPTION_NEW_SCOUT,
                screen=Screen.PVT_FIGHT,
                inbound_info=inbound_keyboard.info,
                exclude_key_from_inbound_info=[
                    FightPlunderReservedKeys.ITEM_ID,
                    FightPlunderReservedKeys.OPPONENT_ID,
                ],
            )
        ])

    # Send message
    await full_media_send(
        context,
        caption=caption,
        update=update,
        add_delete_button=True,
        edit_only_caption_and_keyboard=True,
        delete_button_text=delete_button_text,
        keyboard=inline_keyboard,
    )

    # Save info
    opponent.save()
    fight.save()

    # Send notification to opponent
    await send_notification(context, fight.opponent, FightAttackNotification(fight))


def plunder_get_odds(
    challenger: User, opponent: User
) -> tuple[int, int, int, float, int, int, int]:
    """
    Get the win probability
    :param challenger: The challenger object
    :param opponent: The opponent object
    :return: list -  [0] - Win probability, [1] - Win amount, [2] - Lose amount,
     [3] - Win percentage [4] - Final bounty if user win, [5] - Final bounty if user lose,
     [6] - Sentence duration in hours
    """
    # Probability of winning - How many hours the opponent has been inactive
    win_probability = get_elapsed_hours(opponent.last_system_interaction_date)
    # Cap value
    win_probability = min(
        max(win_probability, Env.PLUNDER_MIN_INACTIVE_HOURS.get_int()),
        Env.PLUNDER_MAX_INACTIVE_HOURS.get_int(),
    )

    # Win percentage is the half of the inverse of the win amount
    win_percentage = (100 - win_probability) / 2
    win_amount = int(get_value_from_percentage(opponent.bounty, win_percentage))
    sentence_duration = ceil(
        get_ability_value(
            challenger, DevilFruitAbilityType.PLUNDER_SENTENCE_DURATION, win_percentage
        )
    )
    lose_amount = int(win_amount * Env.PLUNDER_REPAY_MULTIPLIER.get_float())

    final_bounty_if_won = challenger.bounty + win_amount
    final_bounty_if_lose = challenger.bounty - lose_amount

    return (
        win_probability,
        win_amount,
        lose_amount,
        win_percentage,
        final_bounty_if_won,
        final_bounty_if_lose,
        sentence_duration,
    )


# noinspection DuplicatedCode
# Duplicated by plunder validate
async def plunder_validate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    is_group: bool,
    keyboard: Keyboard = None,
) -> bool:
    """
    Validate the plunder request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param is_group: If the plunder is for a group
    :param keyboard: The keyboard object
    :return: True if the request is valid, False otherwise
    """

    # If not query callback
    plunder: Plunder | None = None
    if update.callback_query is not None and keyboard.has_key(FightPlunderReservedKeys.ITEM_ID):
        plunder: Plunder = Plunder.get_or_none(
            Plunder.id == int(keyboard.info[FightPlunderReservedKeys.ITEM_ID])
        )
        if plunder is None:
            raise GroupChatException(GroupChatError.ITEM_NOT_FOUND)

    now = datetime.datetime.now()

    # User is in plunder cooldown
    if user.plunder_cooldown_end_date is not None and user.plunder_cooldown_end_date > now:
        # Get remaining time
        remaining_time = convert_seconds_to_duration(
            (user.plunder_cooldown_end_date - datetime.datetime.now()).total_seconds()
        )
        ot_text = phrases.PLUNDER_USER_IN_COOLDOWN.format(remaining_time)
        await full_message_or_media_send_or_edit(context, ot_text, update, add_delete_button=True)
        return False

    # User does not have enough amount to scout
    scout_fee = get_scout_fee(user, is_group, ScoutType.PLUNDER)
    if user.bounty < scout_fee:
        ot_text = (
            phrases.FIGHT_PLUNDER_GROUP_INSUFFICIENT_SCOUT_BOUNTY
            if is_group
            else phrases.FIGHT_PLUNDER_PRIVATE_INSUFFICIENT_SCOUT_BOUNTY
        ).format(get_belly_formatted(scout_fee), user.get_bounty_formatted())
        await full_message_or_media_send_or_edit(context, ot_text, update, add_delete_button=True)
        return False

    # Wrong status
    if plunder is not None and plunder.get_status() is not GameStatus.IN_PROGRESS:
        raise GroupChatException(GroupChatError.ITEM_IN_WRONG_STATUS)

    # Opponent not yet available
    if not is_group and not keyboard.has_key(FightPlunderReservedKeys.OPPONENT_ID):
        return True

    # Opponent validation
    try:
        # Get opponent
        opponent: User = get_opponent(update, keyboard)

        # If opponent is not found, send error
        if opponent is None:
            raise OpponentValidationException(GroupChatError.ITEM_NOT_FOUND.build())

        # Opponent is not in the minimum required location
        if opponent.location_level < Env.REQUIRED_LOCATION_LEVEL_PLUNDER.get_int():
            raise OpponentValidationException()

        # Opponent has plunder immunity
        if datetime_is_after(opponent.plunder_immunity_end_date):
            raise OpponentValidationException()

        # Opponent is arrested
        if opponent.is_arrested():
            raise OpponentValidationException()

    except OpponentValidationException as ove:
        if ove.message is not None:
            await full_message_or_media_send_or_edit(context, ove.message, update)
        else:
            await full_message_or_media_send_or_edit(
                context, phrases.PLUNDER_CANNOT_PLUNDER_USER, update=update, add_delete_button=True
            )
        return False

    return True


async def plunder_send_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    keyboard: Keyboard,
    group_chat: GroupChat = None,
) -> None:
    """
    Send request to confirm plunder
    :param update: The update
    :param context: The context
    :param user: The user
    :param keyboard: The keyboard
    :param group_chat: The group chat
    :return: None
    """
    if group_chat is not None:
        # Remove scouting fee, if not from private
        await add_or_remove_bounty(user, get_scout_fee(user, True, ScoutType.PLUNDER), add=False)
        user.plunder_scout_count += 1

        # Delete all previous pending plunders
        previous_plunders: list[Plunder] = Plunder.select().where(
            (Plunder.challenger == user) & (Plunder.status == GameStatus.IN_PROGRESS)
        )
        for previous_plunder in previous_plunders:
            await delete_item_in_group(context, previous_plunder, group_chat)

    # Get opponent
    opponent: User = get_opponent(update, keyboard)
    (
        win_probability,
        win_amount,
        lose_amount,
        win_percentage,
        final_bounty_if_win,
        final_bounty_if_lose,
        sentence,
    ) = plunder_get_odds(user, opponent)

    # Create plunder
    plunder: Plunder = Plunder()
    plunder.challenger = user
    plunder.opponent = opponent
    plunder.win_probability = win_probability
    plunder.belly = win_amount
    plunder.group_chat = group_chat
    plunder.sentence_duration = sentence
    plunder.save()

    caption = phrases.PLUNDER_CONFIRMATION_REQUEST.format(
        user.get_markdown_mention(),
        opponent.get_markdown_name(),
        get_belly_formatted(win_amount),
        get_belly_formatted(lose_amount),
        convert_hours_to_duration(sentence, show_full=True),
        plunder.win_probability,
        user.get_bounty_formatted(),
        get_belly_formatted(final_bounty_if_win),
        get_belly_formatted(final_bounty_if_lose),
    )

    # Keyboard
    # noinspection DuplicatedCode
    inline_keyboard: list[list[Keyboard]] = [
        get_yes_no_keyboard(
            user,
            screen=Screen.GRP_PLUNDER if group_chat is not None else Screen.PVT_PLUNDER,
            yes_text=phrases.KEYBOARD_OPTION_PLUNDER,
            no_text=phrases.KEYBOARD_OPTION_RETREAT,
            primary_key=plunder.id,
            inbound_keyboard=keyboard,
            add_inbound_key_info=True,
        )
    ]

    if group_chat is None:
        # Add new scout button
        inline_keyboard.append([
            Keyboard(
                phrases.KEYBOARD_OPTION_NEW_SCOUT,
                inbound_info=keyboard.info,
                exclude_key_from_inbound_info=[
                    FightPlunderReservedKeys.OPPONENT_ID,
                ],
                screen=Screen.PVT_PLUNDER,
            )
        ])

        caption += phrases.FIGHT_PLUNDER_SCOUT_NEXT_FEE.format(
            get_belly_formatted(get_scout_fee(user, False, ScoutType.PLUNDER))
        )

    message: Message = await full_media_send(
        context,
        saved_media_name=SavedMediaName.PLUNDER,
        update=update,
        caption=caption,
        keyboard=inline_keyboard,
        add_delete_button=True,
        delete_button_text=phrases.KEYBOARD_OPTION_CANCEL,
    )

    plunder.message_id = message.message_id
    plunder.save()


async def plunder_confirm_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    inbound_keyboard: Keyboard,
    group_chat: GroupChat = None,
) -> None:
    """
    Keyboard interaction
    :param update: The update
    :param context: The context
    :param user: The user
    :param inbound_keyboard: The keyboard
    :param group_chat: The group chat
    :return: None
    """

    # Get plunder
    # noinspection DuplicatedCode
    # Duplicated by fight
    plunder: Plunder = Plunder.get_or_none(
        Plunder.id == inbound_keyboard.info[FightPlunderReservedKeys.ITEM_ID]
    )

    # User clicked on retreat button
    if not inbound_keyboard.info[ReservedKeyboardKeys.CONFIRM]:
        # In group, show retreat popup and exit
        if group_chat is not None:
            # Answer callback with retreat message
            await full_message_send(
                context, phrases.FIGHT_CONFIRMATION_RETREAT, update, answer_callback=True
            )
            return await delete_item_in_group(context, plunder, group_chat)

        # In private chat, back to scouting
        opponent: User = plunder.opponent
        plunder.delete_instance()
        return await private_send_scout_request(
            update, context, user, ScoutType.PLUNDER, False, inbound_keyboard, opponent
        )

    opponent: User = plunder.opponent
    # Get plunder odds
    (
        win_probability,
        win_amount,
        lose_amount,
        win_percentage,
        final_bounty_if_win,
        final_bounty_if_lose,
        sentence,
    ) = plunder_get_odds(user, opponent)

    plunder.win_probability = win_probability
    plunder.date = datetime.datetime.now()

    plunder.belly = win_amount
    plunder.sentence_duration = sentence
    if get_random_win(win_probability):  # Challenger won
        plunder.status = GameStatus.WON
        # Add bounty to challenger
        await add_or_remove_bounty(
            user,
            win_amount,
            context=context,
            update=update,
            tax_event_type=IncomeTaxEventType.PLUNDER,
            event_id=plunder.id,
            should_save=True,
            opponent=opponent,
        )
        # Remove bounty from opponent
        await add_or_remove_bounty(
            opponent, win_amount, add=False, update=update, should_save=True
        )
        caption = phrases.PLUNDER_WIN.format(
            user.get_you_markdown_mention(),
            opponent.get_markdown_mention(),
            get_belly_formatted(win_amount),
            user.get_bounty_formatted(),
        )
        saved_media_name: SavedMediaName = SavedMediaName.PLUNDER_SUCCESS
    else:  # Challenger lost
        plunder.status = GameStatus.LOST

        # Create loan for the lost amount
        loan: BountyLoan = add_loan(
            opponent,
            user,
            lose_amount,
            group_chat,
            BountyLoanSource.PLUNDER,
            message_id=plunder.message_id,
            external_id=plunder.id,
        )

        caption = phrases.PLUNDER_LOSE.format(
            user.get_you_markdown_mention(),
            mention_markdown_user(opponent),
            convert_hours_to_duration(plunder.sentence_duration, show_full=True),
            get_belly_formatted(lose_amount),
            loan.get_deeplink(),
            opponent.get_markdown_name(),
        )

        # Add Impel down sentence
        await add_sentence(
            context,
            user,
            ImpelDownSentenceType.TEMPORARY,
            ImpelDownBountyAction.NONE,
            get_datetime_in_future_hours(plunder.sentence_duration),
            phrases.PLUNDER_LOSE_SENTENCE_REASON.format(opponent.tg_first_name),
            ImpelDownSource.PLUNDER,
            external_id=plunder.id,
        )

        saved_media_name: SavedMediaName = SavedMediaName.PLUNDER_FAIL

    # Add plunder immunity to opponent
    opponent.plunder_immunity_end_date = get_ability_adjusted_datetime(
        opponent,
        DevilFruitAbilityType.PLUNDER_IMMUNITY_DURATION,
        Env.PLUNDER_IMMUNITY_DURATION.get_int(),
    )
    # Remove plunder immunity from user
    user.plunder_immunity_end_date = None

    # Add plunder cooldown to user
    user.plunder_cooldown_end_date = get_ability_adjusted_datetime(
        user,
        DevilFruitAbilityType.PLUNDER_COOLDOWN_DURATION,
        Env.PLUNDER_COOLDOWN_DURATION.get_int(),
    )
    # Remove plunder cooldown from opponent
    opponent.plunder_cooldown_end_date = None

    inline_keyboard: list[list[Keyboard]] = []
    delete_button_text = None
    if group_chat is None:
        delete_button_text = phrases.KEYBOARD_OPTION_CLOSE
        caption += phrases.FIGHT_PLUNDER_SCOUT_NEXT_FEE.format(
            get_belly_formatted(get_scout_fee(user, False, ScoutType.PLUNDER))
        )
        inline_keyboard.append([
            Keyboard(
                phrases.KEYBOARD_OPTION_NEW_SCOUT,
                screen=Screen.PVT_PLUNDER,
                inbound_info=inbound_keyboard.info,
                exclude_key_from_inbound_info=[
                    FightPlunderReservedKeys.ITEM_ID,
                    FightPlunderReservedKeys.OPPONENT_ID,
                ],
            )
        ])

    # Send message
    await full_media_send(
        context,
        saved_media_name=saved_media_name,
        caption=caption,
        update=update,
        add_delete_button=True,
        delete_button_text=delete_button_text,
        keyboard=inline_keyboard,
    )

    # Save info
    opponent.save()
    plunder.save()

    # Send notification to opponent
    await send_notification(context, plunder.opponent, PlunderAttackNotification(plunder))
