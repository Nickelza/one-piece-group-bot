import random

from telegram import Update, Message, TelegramError
from telegram.ext import CallbackContext

import constants as c
import resources.Environment as Env
import resources.phrases as phrases
from src.model.DocQGame import DocQGame
from src.model.SavedMedia import SavedMedia
from src.model.User import User
from src.model.enums.Command import Command
from src.model.enums.Emoji import Emoji
from src.model.enums.GameStatus import GameStatus
from src.model.enums.GroupScreen import GroupScreen
from src.model.error.GroupChatError import GroupChatError
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_bounty_formatted
from src.service.cron_service import cron_datetime_difference
from src.service.message_service import full_message_send, full_media_send, mention_markdown_v2


def get_play_amounts(current_bounty: int, win_odds) -> list:
    """
    Get play amounts
    :param current_bounty: The current bounty
    :param win_odds: The win odds
    :return: list -  [0] - Win amount, [1] - Lose amount, [2] - Final bounty if won, [3] - Final bounty if lost
    """

    final_bounty_if_win = int(current_bounty / win_odds)
    final_bounty_if_lose = int(current_bounty * win_odds)
    return [final_bounty_if_win - current_bounty, current_bounty - final_bounty_if_lose, final_bounty_if_win,
            final_bounty_if_lose]


def validate_play(update: Update, context: CallbackContext, user: User, doc_q_game: DocQGame = None) -> bool:
    """
    Validate play request
    :param update: The update
    :param context: The context
    :param user: The user
    :param doc_q_game: The doc q game
    :return: None
    """

    # User is owner of the game
    if doc_q_game is not None and doc_q_game.user != user:
        full_message_send(context, phrases.DOC_Q_GAME_NOT_OWNER.format(Command.GRP_DOC_Q_GAME.value), update,
                          answer_callback=True, show_alert=True)
        return False

    if user.bounty < Env.DOC_Q_GAME_REQUIRED_BOUNTY.get_float():
        ot_text = phrases.DOC_Q_GAME_NOT_ENOUGH_BOUNTY.format(get_bounty_formatted(
            Env.DOC_Q_GAME_REQUIRED_BOUNTY.get_int()), get_bounty_formatted(user.bounty))
        full_message_send(context, ot_text, update)
        return False

    if not user.can_play_doc_q:
        ot_text = phrases.DOC_Q_GAME_LIMIT_REACHED.format(
            cron_datetime_difference(Env.CRON_RESET_DOC_Q_GAME.get()))
        full_message_send(context, ot_text, update)
        return False

    # Delete all previous pending games
    previous_games: list[DocQGame] = DocQGame.select().where(DocQGame.user == user &
                                                             DocQGame.status == GameStatus.IN_PROGRESS.value)
    for previous_game in previous_games:
        if previous_game != doc_q_game:
            delete_game(update, context, previous_game)

    return True


def delete_game(update: Update, context: CallbackContext, doc_q_game: DocQGame) -> None:
    """
    Delete game
    :param update: The update
    :param context: The context
    :param doc_q_game: The doc q game
    :return: None
    """
    # Try to delete message
    try:
        context.bot.delete_message(update.effective_chat.id, doc_q_game.message_id)
    except TelegramError:
        pass

    # Delete game
    doc_q_game.delete_instance()


def play_request(update: Update, context: CallbackContext, user: User) -> None:
    """
    User request to play Doc Q Game
    :param update: The update
    :param context: The context
    :param user: The user
    :return: None
    """
    if validate_play(update, context, user):
        doc_q_game = DocQGame()
        doc_q_game.user = user
        doc_q_game.save()

        # Number of possible correct choices is determined by number of options * success rate
        possible_correct_choices = int(Env.DOC_Q_GAME_OPTIONS_COUNT.get_int() * Env.DOC_Q_GAME_WIN_ODD.get_float())

        correct_choices_index = []
        # Generate correct choices
        for i in range(possible_correct_choices):
            index = random.randint(0, Env.DOC_Q_GAME_OPTIONS_COUNT.get_int() - 1)
            while index in correct_choices_index:
                index = random.randint(0, Env.DOC_Q_GAME_OPTIONS_COUNT.get_int() - 1)
            correct_choices_index.append(index)

        # Create Keyboard with 5 apple buttons
        keyboard_data: dict = {'a': doc_q_game.id}
        inline_keyboard = []
        apples_keyboard: list[Keyboard] = []
        for i in range(Env.DOC_Q_GAME_OPTIONS_COUNT.get_int()):
            keyboard_data['b'] = int(i in correct_choices_index)

            option_emoji = Emoji.DOC_Q_GAME_OPTION.value

            # should show correct answer
            if Env.DOC_Q_GAME_SHOW_CORRECT_OPTION.get_bool() and i in correct_choices_index:
                option_emoji = Emoji.DOC_Q_GAME_CORRECT_OPTION.value

            apples_keyboard.append(Keyboard(option_emoji, keyboard_data, GroupScreen.DOC_Q_GAME))

        inline_keyboard.append(apples_keyboard)
        # Add cancel button
        inline_keyboard.append([Keyboard(phrases.KEYBOARD_OPTION_CANCEL, {'a': doc_q_game.id, 'x': 1},
                                         GroupScreen.DOC_Q_GAME)])

        # Get SavedMedia
        doc_q_media: SavedMedia = SavedMedia.get_or_none(SavedMedia.name == c.SAVED_MEDIA_NAME_DOC_Q)

        # SavedMedia is not found
        if doc_q_media is None:
            full_message_send(context, GroupChatError.DOC_Q_MEDIA_NOT_FOUND.build(), update)
            return

        play_amounts = get_play_amounts(user.bounty, Env.DOC_Q_GAME_WIN_ODD.get_float())
        # Send media
        caption = phrases.DOC_Q_GAME_START.format(mention_markdown_v2(user.tg_user_id, user.tg_first_name),
                                                  get_bounty_formatted(play_amounts[0]),
                                                  get_bounty_formatted(play_amounts[1]),
                                                  get_bounty_formatted(user.bounty),
                                                  get_bounty_formatted(play_amounts[2]),
                                                  get_bounty_formatted(play_amounts[3]))

        message: Message = full_media_send(context, doc_q_media, update, caption=caption, keyboard=inline_keyboard)
        doc_q_game.message_id = message.message_id
        doc_q_game.save()


def keyboard_interaction(update: Update, context: CallbackContext, user: User, keyboard: Keyboard = None) -> None:
    """
    Keyboard interaction
    :param update: The update
    :param context: The context
    :param user: The user
    :param keyboard: The keyboard
    :return: None
    """

    doc_q_game: DocQGame = DocQGame.get_or_none(DocQGame.id == keyboard.info['a'])

    if doc_q_game is None:
        full_message_send(context, GroupChatError.DOC_Q_GAME_NOT_FOUND.build(), update)
        return

    if validate_play(update, context, user, doc_q_game):
        # User clicked on cancel button
        if 'x' in keyboard.info:
            # Answer callback with goodbye message
            full_message_send(context, phrases.DOC_Q_GAME_CANCEL, update, answer_callback=True)
            delete_game(update, context, doc_q_game)
            return

        play_amounts = get_play_amounts(user.bounty, Env.DOC_Q_GAME_WIN_ODD.get_float())
        # User chose correct option
        if keyboard.info['b']:
            # Increase user's bounty
            user.bounty += play_amounts[0]

            # Update game status
            doc_q_game.status = GameStatus.WON.value
            doc_q_game.berry = play_amounts[0]

            ot_text = phrases.DOC_Q_GAME_WIN.format(mention_markdown_v2(user.tg_user_id, user.tg_first_name),
                                                    Emoji.DOC_Q_GAME_WIN.value,
                                                    get_bounty_formatted(play_amounts[0]),
                                                    get_bounty_formatted(user.bounty))
        else:  # User chose wrong option
            # Decrease user's bounty
            user.bounty -= play_amounts[1]

            # Update game status
            doc_q_game.status = GameStatus.LOST.value
            doc_q_game.berry = play_amounts[1]

            ot_text = phrases.DOC_Q_GAME_LOSE.format(mention_markdown_v2(user.tg_user_id, user.tg_first_name),
                                                     Emoji.DOC_Q_GAME_LOSE.value,
                                                     get_bounty_formatted(play_amounts[1]),
                                                     get_bounty_formatted(user.bounty))
        # Save updates
        user.can_play_doc_q = False
        user.save()
        doc_q_game.save()

        # Send outcome text
        full_media_send(context, update=update, caption=ot_text, edit_only_caption_and_keyboard=True,
                        add_delete_button=True)


def reset_playability(context: CallbackContext) -> None:
    """
    Reset playability
    :param context: The context
    :return: None
    """

    User.update(can_play_doc_q=1).execute()


def manage(update: Update, context: CallbackContext, user: User, keyboard: Keyboard = None) -> None:
    """
    Manage Doc Q Game screen
    :param update: The update
    :param context: The context
    :param user: The user
    :param keyboard: The keyboard
    :return: None
    """
    # Request to play
    if update.message is not None:
        play_request(update, context, user)
        return

    # Interaction with keyboard
    if keyboard is None:
        full_message_send(context, GroupChatError.KEYBOARD_NOT_FOUND.build(), update)
        return

    keyboard_interaction(update, context, user, keyboard)
