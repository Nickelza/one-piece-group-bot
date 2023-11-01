import datetime
from enum import StrEnum

from telegram import Update, Message
from telegram.ext import ContextTypes

import resources.Environment as Env
from resources import phrases
from src.model.Fight import Fight
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.LeaderboardRank import get_rank_by_leaderboard_user
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.enums.income_tax.IncomeTaxEventType import IncomeTaxEventType
from src.model.error.CustomException import OpponentValidationException
from src.model.error.GroupChatError import GroupChatError, GroupChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_belly_formatted, add_or_remove_bounty
from src.service.date_service import convert_seconds_to_duration
from src.service.devil_fruit_service import get_ability_adjusted_datetime
from src.service.devil_fruit_service import get_ability_value
from src.service.leaderboard_service import get_current_leaderboard_user
from src.service.math_service import get_random_win, get_value_from_percentage
from src.service.message_service import full_message_send, mention_markdown_user, get_yes_no_keyboard, \
    mention_markdown_v2, full_media_send, full_message_or_media_send_or_edit, delete_message


class FightReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    FIGHT_ID = 'a'


def get_opponent(update: Update = None, keyboard: Keyboard = None) -> User | None:
    """
    Get opponent from update or keyboard
    :param update: The update object. If None, the opponent is taken from the keyboard
    :param keyboard: The keyboard object. If None, the opponent is taken from the update
    :return: The opponent object
    """

    if update.callback_query is None:
        return User.get_or_none(User.tg_user_id == update.message.reply_to_message.from_user.id)

    fight: Fight = Fight.get_or_none(Fight.id == int(keyboard.info[FightReservedKeys.FIGHT_ID]))
    if fight is None:
        return None
    return fight.opponent


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, keyboard: Keyboard = None) -> bool:
    """
    Validate the fight request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param keyboard: The keyboard object
    :return: True if the request is valid, False otherwise
    """
    # If not query callback
    if update.callback_query is not None:
        # Get opponent from fight id
        fight: Fight = Fight.get_or_none(Fight.id == int(keyboard.info[FightReservedKeys.FIGHT_ID]))
        if fight is None:
            raise GroupChatException(GroupChatError.FIGHT_NOT_FOUND)

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
        now = datetime.datetime.now()
        if opponent.fight_immunity_end_date is not None and opponent.fight_immunity_end_date > now:
            raise OpponentValidationException()

        # Opponent is arrested
        if opponent.is_arrested():
            raise OpponentValidationException()

        # Opponent in your same crew
        if user.is_crew_member() and user.crew == opponent.crew:
            raise OpponentValidationException(phrases.FIGHT_CANNOT_FIGHT_CREW_MEMBER)

    except OpponentValidationException as ove:
        if ove.message is not None:
            await full_message_or_media_send_or_edit(context, ove.message, update)
        else:
            await full_message_or_media_send_or_edit(context, phrases.FIGHT_CANNOT_FIGHT_USER, update=update,
                                                     add_delete_button=True)
        return False

    # User is in fight cooldown
    if user.fight_cooldown_end_date is not None and user.fight_cooldown_end_date > now:
        # Get remaining time
        remaining_time = convert_seconds_to_duration((user.fight_cooldown_end_date - datetime.datetime.now())
                                                     .total_seconds())
        ot_text = phrases.FIGHT_USER_IN_COOLDOWN.format(remaining_time)
        await full_message_or_media_send_or_edit(context, ot_text, update, add_delete_button=True)
        return False

    return True


def get_fight_odds(challenger: User, opponent: User) -> tuple[float, int, int, int, int]:
    """
    Get the win probability
    :param challenger: The challenger object
    :param opponent: The opponent object
    :return: list -  [0] - Win probability, [1] - Win amount, [2] - Lose amount
            [3] - Final bounty if user win, [4] - Final bounty if user lose
    """
    # Probability of winning - How much percent more is the challenger bounty compared to the opponent
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
        win_probability = min(win_probability, Env.FIGHT_MAX_WIN_PROBABILITY_FINAL_LOCATION.get_float())

    lose_probability = 100 - win_probability

    # Recalculate opponent win probability with Devil Fruit ability
    opponent_win_probability = get_ability_value(
        opponent, DevilFruitAbilityType.FIGHT_DEFENSE_BOOST, lose_probability, add_to_value=True)
    # Cap opponent win probability to max allowed for Devil Fruit boost
    opponent_win_probability = round(
        min(opponent_win_probability, Env.FIGHT_MAX_WIN_PROBABILITY_DEVIL_FRUIT_DEFENSE_BOOST.get_float()), 2)
    win_probability, lose_probability = 100 - opponent_win_probability, opponent_win_probability

    # Win amount is the amount from opponent bounty corresponding to lose probability
    win_amount = int(get_value_from_percentage(opponent.bounty, lose_probability))
    # Lose amount is the amount from challenger bounty corresponding to maximum between win and lose probability
    lose_amount = int(get_value_from_percentage(challenger.bounty, max(win_probability, lose_probability)))

    final_bounty_if_won = challenger.bounty + win_amount
    final_bounty_if_lose = challenger.bounty - lose_amount

    return win_probability, win_amount, lose_amount, final_bounty_if_won, final_bounty_if_lose


async def delete_fight(context: ContextTypes.DEFAULT_TYPE, fight: Fight, group_chat: GroupChat) -> None:
    """
    Delete fight
    :param context: The context
    :param fight: The fight
    :param group_chat: The group chat
    :return: None
    """
    # Try to delete message
    await delete_message(context=context, group_chat=group_chat, message_id=fight.message_id)

    # Delete fight
    fight.delete_instance()


async def send_request(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, group_chat: GroupChat) -> None:
    """
    Send request to confirm fight
    :param update: The update
    :param context: The context
    :param user: The user
    :param group_chat: The group chat
    :return: None
    """

    # Delete all previous pending fights
    previous_fights: list[Fight] = Fight.select().where((Fight.challenger == user) &
                                                        (Fight.status == GameStatus.IN_PROGRESS))
    for previous_fight in previous_fights:
        await delete_fight(context, previous_fight, group_chat)

    # Get opponent
    opponent: User = get_opponent(update)
    win_probability, win_amount, lose_amount, final_bounty_if_win, final_bounty_if_lose = get_fight_odds(user, opponent)

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

    odds_recalculated_text = (phrases.FIGHT_CONFIRMATION_ODDS_RECALCULATED
                              if opponent.is_crew_member() and not opponent.has_higher_bounty_than_crew_average()
                              else "")

    caption = phrases.FIGHT_CONFIRMATION_REQUEST.format(mention_markdown_user(user), mention_markdown_user(opponent),
                                                        outcome_probability, outcome, odds_recalculated_text,
                                                        user.get_bounty_formatted(),
                                                        get_belly_formatted(final_bounty_if_win),
                                                        get_belly_formatted(final_bounty_if_lose))

    # Keyboard
    inline_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(user, screen=Screen.GRP_FIGHT,
                                                                 yes_text=phrases.KEYBOARD_OPTION_FIGHT,
                                                                 no_text=phrases.KEYBOARD_OPTION_RETREAT,
                                                                 primary_key=fight.id)]

    message: Message = await full_media_send(context, saved_media_name=SavedMediaName.FIGHT, update=update,
                                             caption=caption, keyboard=inline_keyboard)

    fight.message_id = message.message_id
    fight.save()


async def keyboard_interaction(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, keyboard: Keyboard,
                               group_chat: GroupChat) -> None:
    """
    Keyboard interaction
    :param update: The update
    :param context: The context
    :param user: The user
    :param keyboard: The keyboard
    :param group_chat: The group chat
    :return: None
    """

    # Get fight
    fight: Fight = Fight.get_or_none(Fight.id == keyboard.info[FightReservedKeys.FIGHT_ID])

    # User clicked on retreat button
    if not keyboard.info[ReservedKeyboardKeys.CONFIRM]:
        # Answer callback with retreat message
        await full_message_send(context, phrases.FIGHT_CONFIRMATION_RETREAT, update, answer_callback=True)
        await delete_fight(context, fight, group_chat)
        return

    opponent: User = fight.opponent
    # Get fight odds
    win_probability, win_amount, lose_amount, final_bounty_if_win, final_bounty_if_lose = get_fight_odds(
        user, opponent)
    fight.win_probability = win_probability
    fight.date = datetime.datetime.now()

    if get_random_win(win_probability):  # Challenger won
        fight.status = GameStatus.WON
        fight.belly = win_amount
        # Add bounty to challenger
        await add_or_remove_bounty(user, win_amount, update=update, tax_event_type=IncomeTaxEventType.FIGHT,
                                   event_id=fight.id)
        # Remove bounty from opponent
        await add_or_remove_bounty(opponent, win_amount, add=False, update=update)
        caption = phrases.FIGHT_WIN.format(mention_markdown_v2(user.tg_user_id, 'you'),
                                           mention_markdown_user(opponent), get_belly_formatted(win_amount),
                                           user.get_bounty_formatted())
    else:  # Challenger lost
        fight.status = GameStatus.LOST
        fight.belly = lose_amount
        # Remove bounty from challenger
        await add_or_remove_bounty(user, lose_amount, add=False, update=update)
        # Add bounty to opponent
        await add_or_remove_bounty(opponent, lose_amount, update=update, tax_event_type=IncomeTaxEventType.FIGHT,
                                   event_id=fight.id)
        caption = phrases.FIGHT_LOSE.format(mention_markdown_v2(user.tg_user_id, 'you'),
                                            mention_markdown_user(opponent), get_belly_formatted(lose_amount),
                                            user.get_bounty_formatted())

    # Add fight immunity to opponent
    opponent.fight_immunity_end_date = get_ability_adjusted_datetime(
        opponent, DevilFruitAbilityType.FIGHT_IMMUNITY_DURATION, Env.FIGHT_IMMUNITY_DURATION.get_int())
    # Remove fight immunity from user
    user.fight_immunity_end_date = None

    # Add fight cooldown to user
    user.fight_cooldown_end_date = get_ability_adjusted_datetime(
        user, DevilFruitAbilityType.FIGHT_COOLDOWN_DURATION, Env.FIGHT_COOLDOWN_DURATION.get_int())
    # Remove fight cooldown from opponent
    opponent.fight_cooldown_end_date = None

    # Send message
    await full_media_send(context, caption=caption, update=update, add_delete_button=True,
                          edit_only_caption_and_keyboard=True)

    # Save info
    opponent.save()
    fight.save()


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, keyboard: Keyboard,
                 group_chat: GroupChat) -> None:
    """
    Manage the fight request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param keyboard: The keyboard object
    :param group_chat: The group chat
    :return: None
    """

    # Validate the request
    if not await validate(update, context, user, keyboard):
        return

    # Request to fight
    if keyboard is None:
        await send_request(update, context, user, group_chat)
        return

    await keyboard_interaction(update, context, user, keyboard, group_chat)
