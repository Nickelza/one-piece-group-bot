import datetime

from telegram import Update, TelegramError, Message
from telegram.ext import CallbackContext

import constants as c
import resources.Environment as Env
import resources.phrases as phrases
from src.model.Fight import Fight
from src.model.SavedMedia import SavedMedia
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.LeaderboardRank import get_rank_by_leaderboard_user
from src.model.enums.Screen import Screen
from src.model.error.CustomException import OpponentValidationException
from src.model.error.GroupChatError import GroupChatError
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_belly_formatted, add_bounty
from src.service.cron_service import convert_seconds_to_time
from src.service.leaderboard_service import get_current_leaderboard_user
from src.service.math_service import get_random_win, get_value_from_percentage
from src.service.message_service import full_message_send, mention_markdown_user, get_yes_no_keyboard, \
    mention_markdown_v2, full_media_send, full_message_or_media_edit


def get_opponent(update: Update = None, keyboard: Keyboard = None) -> User | None:
    """
    Get opponent from update or keyboard
    :param update: The update object. If None, the opponent is taken from the keyboard
    :param keyboard: The keyboard object. If None, the opponent is taken from the update
    :return: The opponent object
    """

    if update.callback_query is None:
        return User.get_or_none(User.tg_user_id == update.message.reply_to_message.from_user.id)

    fight: Fight = Fight.get_or_none(Fight.id == int(keyboard.info['a']))
    if fight is None:
        return None
    return fight.opponent


def validate(update: Update, context: CallbackContext, user: User, keyboard: Keyboard = None) -> bool:
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
        fight: Fight = Fight.get_or_none(Fight.id == int(keyboard.info['a']))
        if fight is None:
            full_message_or_media_edit(context, GroupChatError.FIGHT_NOT_FOUND.build(), update=update)
            return False

    # Opponent validation
    try:
        # Get opponent
        opponent: User = get_opponent(update, keyboard)

        # If opponent is not found, send error
        if opponent is None:
            raise OpponentValidationException(GroupChatError.FIGHT_OPPONENT_NOT_FOUND.build())

        # Opponent is not in the minimum required location
        if not opponent.location_level >= Env.REQUIRED_LOCATION_LEVEL_FIGHT.get_int():
            raise OpponentValidationException()

        # Opponent has fight immunity
        now = datetime.datetime.now()
        if opponent.fight_immunity_end_date is not None and opponent.fight_immunity_end_date > now:
            raise OpponentValidationException()

        # Opponent is arrested
        if opponent.is_arrested():
            raise OpponentValidationException()

    except OpponentValidationException as ove:
        if ove.message is not None:
            full_message_or_media_edit(context, ove.message, update)
        else:
            full_message_or_media_edit(context, phrases.FIGHT_CANNOT_FIGHT_USER, update=update, add_delete_button=True)
        return False

    # User is in fight cooldown
    if user.fight_cooldown_end_date is not None and user.fight_cooldown_end_date > now:
        # Get remaining time
        remaining_time = convert_seconds_to_time((user.fight_cooldown_end_date - datetime.datetime.now())
                                                 .total_seconds())
        ot_text = phrases.FIGHT_USER_IN_COOLDOWN.format(remaining_time)
        full_message_or_media_edit(context, ot_text, update, add_delete_button=True)
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
    win_probability = (challenger.bounty / opponent.bounty) * 50

    # Cap probability
    leaderboard_user = get_current_leaderboard_user(challenger)
    leaderboard_rank = get_rank_by_leaderboard_user(leaderboard_user)
    # Use minimum probability if the probability is too low
    win_probability = round(max(win_probability, leaderboard_rank.min_win_probability), 2)
    # Use maximum probability if the probability is too high
    win_probability = round(min(win_probability, leaderboard_rank.max_win_probability), 2)
    lose_probability = 100 - win_probability

    # Win amount is the amount from opponent bounty corresponding to lose probability
    win_amount = int(get_value_from_percentage(opponent.bounty, lose_probability))
    # Lose amount is the amount from challenger bounty corresponding to maximum between win and lose probability
    lose_amount = int(get_value_from_percentage(challenger.bounty, max(win_probability, lose_probability)))

    final_bounty_if_won = challenger.bounty + win_amount
    final_bounty_if_lose = challenger.bounty - lose_amount

    return win_probability, win_amount, lose_amount, final_bounty_if_won, final_bounty_if_lose


def delete_fight(update: Update, context: CallbackContext, fight: Fight) -> None:
    """
    Delete game
    :param update: The update
    :param context: The context
    :param fight: The fight
    :return: None
    """
    # Try to delete message
    try:
        context.bot.delete_message(update.effective_chat.id, fight.message_id)
    except TelegramError:
        pass

    # Delete fight
    fight.delete_instance()


def send_request(update: Update, context: CallbackContext, user: User) -> None:
    """
    Send request to confirm fight
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :return: None
    """

    # Delete all previous pending fights
    previous_fights: list[Fight] = Fight.select().where((Fight.challenger == user) &
                                                        (Fight.status == GameStatus.IN_PROGRESS.value))
    for previous_fight in previous_fights:
        delete_fight(update, context, previous_fight)

    # Get opponent
    opponent: User = get_opponent(update)
    win_probability, win_amount, lose_amount, final_bounty_if_win, final_bounty_if_lose = get_fight_odds(user, opponent)

    # Create fight
    fight: Fight = Fight()
    fight.challenger = user
    fight.opponent = opponent
    fight.win_probability = win_probability
    fight.belly = win_amount
    fight.save()

    if win_probability > 50:
        outcome = phrases.FIGHT_CONFIRMATION_OUTCOME_VICTORY
        outcome_probability = win_probability
    else:
        outcome = phrases.FIGHT_CONFIRMATION_OUTCOME_DEFEAT
        outcome_probability = 100 - win_probability

    # Get SavedMedia
    fight_media: SavedMedia = SavedMedia.get_or_none(SavedMedia.name == c.SAVED_MEDIA_NAME_FIGHT)

    # SavedMedia is not found
    if fight_media is None:
        full_message_send(context, GroupChatError.SAVED_MEDIA_NOT_FOUND.build(), update)
        return

    caption = phrases.FIGHT_CONFIRMATION_REQUEST.format(mention_markdown_user(user), mention_markdown_user(opponent),
                                                        outcome_probability, outcome, user.get_bounty_formatted(),
                                                        get_belly_formatted(final_bounty_if_win),
                                                        get_belly_formatted(final_bounty_if_lose))

    # Keyboard
    inline_keyboard: list[list[Keyboard]] = [get_yes_no_keyboard(user, fight.id, phrases.KEYBOARD_OPTION_FIGHT,
                                                                 phrases.KEYBOARD_OPTION_RETREAT,
                                                                 Screen.GRP_FIGHT)]

    message: Message = full_media_send(context, fight_media, update=update, caption=caption, keyboard=inline_keyboard)
    fight.message_id = message.message_id
    fight.save()


def keyboard_interaction(update: Update, context: CallbackContext, user: User, keyboard: Keyboard) -> None:
    """
    Keyboard interaction
    :param update: The update
    :param context: The context
    :param user: The user
    :param keyboard: The keyboard
    :return: None
    """

    # Get fight
    fight: Fight = Fight.get_or_none(Fight.id == keyboard.info['a'])

    # User clicked on retreat button
    if not keyboard.info['b']:
        # Answer callback with retreat message
        full_message_send(context, phrases.FIGHT_CONFIRMATION_RETREAT, update, answer_callback=True)
        delete_fight(update, context, fight)
        return

    opponent: User = fight.opponent
    # Get fight odds
    win_probability, win_amount, lose_amount, final_bounty_if_win, final_bounty_if_lose = get_fight_odds(
        user, opponent)
    fight.win_probability = win_probability
    fight.date = datetime.datetime.now()

    if get_random_win(win_probability):  # Challenger won
        fight.status = GameStatus.WON.value
        fight.belly = win_amount
        # Add bounty to challenger
        user = add_bounty(user, win_amount)
        # Remove bounty from opponent
        opponent.bounty -= win_amount
        caption = phrases.FIGHT_WIN.format(mention_markdown_v2(user.tg_user_id, 'you'),
                                           mention_markdown_user(opponent), get_belly_formatted(win_amount),
                                           user.get_bounty_formatted())
    else:  # Challenger lost
        fight.status = GameStatus.LOST.value
        fight.belly = lose_amount
        # Remove bounty from challenger
        user.bounty -= lose_amount
        # Add bounty to opponent
        opponent = add_bounty(opponent, lose_amount)
        caption = phrases.FIGHT_LOSE.format(mention_markdown_v2(user.tg_user_id, 'you'),
                                            mention_markdown_user(opponent), get_belly_formatted(lose_amount),
                                            user.get_bounty_formatted())

    # Add fight immunity to opponent
    opponent.fight_immunity_end_date = datetime.datetime.now() + datetime.timedelta(
        hours=Env.FIGHT_IMMUNITY_DURATION.get_int())
    # Remove fight immunity from user
    user.fight_immunity_end_date = None

    # Add fight cooldown to user
    user.fight_cooldown_end_date = datetime.datetime.now() + datetime.timedelta(
        hours=Env.FIGHT_COOLDOWN_DURATION.get_int())
    # Remove fight cooldown from opponent
    opponent.fight_cooldown_end_date = None

    # Send message
    full_media_send(context, caption=caption, update=update, add_delete_button=True,
                    edit_only_caption_and_keyboard=True)

    # Save info
    user.save()
    opponent.save()
    fight.save()


def manage(update: Update, context: CallbackContext, user: User, keyboard: Keyboard = None) -> None:
    """
    Manage the change region request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param keyboard: The keyboard object
    :return: None
    """

    # Validate the request
    if not validate(update, context, user, keyboard):
        return

    # Request to fight
    if keyboard is None:
        send_request(update, context, user)
        return

    keyboard_interaction(update, context, user, keyboard)
