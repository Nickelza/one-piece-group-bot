import random
from datetime import datetime
from enum import StrEnum

from telegram import Update, Message
from telegram.error import BadRequest
from telegram.ext import ContextTypes

import constants as c
import resources.Environment as Env
import resources.phrases as phrases
from src.model.DocQGame import DocQGame
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.GameStatus import GameStatus
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.enums.income_tax.IncomeTaxEventType import IncomeTaxEventType
from src.model.error.GroupChatError import GroupChatError, GroupChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_belly_formatted, add_or_remove_bounty
from src.service.date_service import get_remaining_duration
from src.service.devil_fruit_service import get_datetime
from src.service.message_service import full_message_send, full_media_send, full_message_or_media_send_or_edit, \
    mention_markdown_v2, delete_message


class DocQReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    DOC_Q_ID = 'a'
    CHOICE_INDEX = 'b'
    CANCEL = 'c'


def get_play_amounts(current_bounty: int, win_odds) -> tuple[int, int, int, int]:
    """
    Get play amounts
    :param current_bounty: The current bounty
    :param win_odds: The win odds
    :return: list -  [0] - Win amount, [1] - Lose amount, [2] - Final bounty if won, [3] - Final bounty if lost
    """

    # Win amount always takes in consideration standard odd
    final_bounty_if_win = int(current_bounty / Env.DOC_Q_GAME_WIN_ODD.get_float())

    final_bounty_if_lose = int(current_bounty * win_odds)
    return (final_bounty_if_win - current_bounty, current_bounty - final_bounty_if_lose, final_bounty_if_win,
            final_bounty_if_lose)


def get_win_odd(user: User) -> float:
    """
    Get win odd
    :param user: The user
    :return: The win odd
    """

    return (Env.DOC_Q_GAME_WIN_ODD_FINAL_LOCATION.get_float() if user.has_bounty_gain_limitations()
            else Env.DOC_Q_GAME_WIN_ODD.get_float())


async def validate_play(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User,
                        doc_q_game: DocQGame = None) -> bool:
    """
    Validate play request
    :param update: The update
    :param context: The context
    :param user: The user
    :param doc_q_game: The doc q game
    :return: None
    """

    # User has enough bounty
    if user.bounty < Env.DOC_Q_GAME_REQUIRED_BOUNTY.get_float():
        ot_text = phrases.DOC_Q_GAME_NOT_ENOUGH_BOUNTY.format(get_belly_formatted(
            Env.DOC_Q_GAME_REQUIRED_BOUNTY.get_int()), user.get_bounty_formatted())
        try:
            await full_message_send(context, ot_text, update=update, add_delete_button=True)
        except BadRequest:
            await full_message_or_media_send_or_edit(context, ot_text, update=update, add_delete_button=True)
        return False

    if user.doc_q_cooldown_end_date is not None and user.doc_q_cooldown_end_date > datetime.now():
        ot_text = phrases.DOC_Q_GAME_LIMIT_REACHED.format(get_remaining_duration(user.doc_q_cooldown_end_date))
        try:
            await full_message_send(context, ot_text, update=update, add_delete_button=True)
        except BadRequest:
            await full_message_or_media_send_or_edit(context, ot_text, update=update, add_delete_button=True)
        return False

    # Delete all previous pending games
    previous_games: list[DocQGame] = DocQGame.select().where((DocQGame.user == user) &
                                                             (DocQGame.status == GameStatus.IN_PROGRESS))
    for previous_game in previous_games:
        if previous_game != doc_q_game:
            await delete_game(context, previous_game)

    return True


async def delete_game(context: ContextTypes.DEFAULT_TYPE, doc_q_game: DocQGame) -> None:
    """
    Delete game
    :param context: The context
    :param doc_q_game: The doc q game
    :return: None
    """
    # Try to delete message
    await delete_message(context=context, group_chat=doc_q_game.group_chat, message_id=doc_q_game.message_id)

    # Delete game
    doc_q_game.delete_instance()


async def play_request(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, group_chat: GroupChat) -> None:
    """
    User request to play Doc Q Game
    :param update: The update
    :param context: The context
    :param user: The user
    :param group_chat: The group chat
    :return: None
    """
    if await validate_play(update, context, user):
        doc_q_game = DocQGame()
        doc_q_game.user = user
        doc_q_game.group_chat = group_chat
        doc_q_game.save()

        if user.has_bounty_gain_limitations():
            options_count = Env.DOC_Q_GAME_OPTIONS_COUNT_FINAL_LOCATION.get_int()
        else:
            options_count = Env.DOC_Q_GAME_OPTIONS_COUNT.get_int()

        win_odd = get_win_odd(user)
        # Number of possible correct choices is determined by number of options * success rate
        possible_correct_choices = int(options_count * win_odd)

        correct_choices_index = []
        # Generate correct choices
        for i in range(possible_correct_choices):
            index = random.randint(0, options_count - 1)
            while index in correct_choices_index:
                index = random.randint(0, options_count - 1)
            correct_choices_index.append(index)

        # Add correct choices to game
        doc_q_game.correct_choices_index = c.STANDARD_SPLIT_CHAR.join(str(i) for i in correct_choices_index)

        # Create Keyboard with n apple buttons
        keyboard_data_template: dict = {DocQReservedKeys.DOC_Q_ID: doc_q_game.id}
        inline_keyboard = []
        apples_keyboard: list[Keyboard] = []
        for i in range(options_count):
            keyboard_data = keyboard_data_template | {DocQReservedKeys.CHOICE_INDEX: i}
            option_emoji = Emoji.DOC_Q_GAME_OPTION

            # should show correct answer
            if Env.DOC_Q_GAME_SHOW_CORRECT_OPTION.get_bool() and i in correct_choices_index:
                option_emoji = Emoji.DOC_Q_GAME_CORRECT_OPTION

            apples_keyboard.append(Keyboard(option_emoji, keyboard_data, Screen.GRP_DOC_Q_GAME))

            # Add new keyboard line if needed
            if (i + 1) % c.STANDARD_LIST_KEYBOARD_ROW_SIZE == 0 and i != 0:
                inline_keyboard.append(apples_keyboard)
                apples_keyboard = []

        inline_keyboard.append(apples_keyboard)

        win_amount, lose_amount, final_bounty_if_win, final_bounty_if_lose = get_play_amounts(user.bounty, win_odd)
        # Send media
        caption = phrases.DOC_Q_GAME_START.format(mention_markdown_v2(user.tg_user_id, user.tg_first_name),
                                                  get_belly_formatted(win_amount),
                                                  get_belly_formatted(lose_amount),
                                                  user.get_bounty_formatted(),
                                                  get_belly_formatted(final_bounty_if_win),
                                                  get_belly_formatted(final_bounty_if_lose))

        # Delete button, can't be replaced by add_delete_button because wagers have to be returned
        inline_keyboard.append(
            [Keyboard(phrases.KEYBOARD_OPTION_CANCEL,
                      info={DocQReservedKeys.DOC_Q_ID: doc_q_game.id, DocQReservedKeys.CANCEL: True},
                      screen=Screen.GRP_DOC_Q_GAME)])

        message: Message = await full_media_send(context, saved_media_name=SavedMediaName.DOC_Q, update=update,
                                                 caption=caption, keyboard=inline_keyboard)

        doc_q_game.message_id = message.message_id
        doc_q_game.save()


async def keyboard_interaction(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User,
                               keyboard: Keyboard) -> None:
    """
    Keyboard interaction
    :param update: The update
    :param context: The context
    :param user: The user
    :param keyboard: The keyboard
    :return: None
    """

    doc_q_game: DocQGame = DocQGame.get_or_none(DocQGame.id == keyboard.info[DocQReservedKeys.DOC_Q_ID])

    if doc_q_game is None:
        raise GroupChatException(GroupChatError.DOC_Q_GAME_NOT_FOUND)

    if await validate_play(update, context, user, doc_q_game):
        # User clicked on cancel button
        if DocQReservedKeys.CANCEL in keyboard.info:
            # Answer callback with goodbye message
            await full_message_send(context, phrases.DOC_Q_GAME_CANCEL, update, answer_callback=True)
            await delete_game(context, doc_q_game)
            return

        win_odd = get_win_odd(user)
        win_amount, lose_amount, final_bounty_if_win, final_bounty_if_lose = get_play_amounts(user.bounty, win_odd)
        # User chose correct option
        correct_choices_index = str(doc_q_game.correct_choices_index).split(c.STANDARD_SPLIT_CHAR)
        if str(keyboard.info[DocQReservedKeys.CHOICE_INDEX]) in correct_choices_index:
            # Increase user's bounty
            await add_or_remove_bounty(user, win_amount, update=update, tax_event_type=IncomeTaxEventType.DOC_Q_GAME,
                                       event_id=doc_q_game.id)

            # Update game status
            doc_q_game.status = GameStatus.WON
            doc_q_game.belly = win_amount

            ot_text = phrases.DOC_Q_GAME_WIN.format(mention_markdown_v2(user.tg_user_id, user.tg_first_name),
                                                    Emoji.DOC_Q_GAME_WIN,
                                                    get_belly_formatted(win_amount),
                                                    user.get_bounty_formatted())
        else:  # User chose wrong option
            # Decrease user's bounty
            await add_or_remove_bounty(user, lose_amount, add=False, update=update)

            # Update game status
            doc_q_game.status = GameStatus.LOST
            doc_q_game.belly = lose_amount

            ot_text = phrases.DOC_Q_GAME_LOSE.format(mention_markdown_v2(user.tg_user_id, user.tg_first_name),
                                                     Emoji.DOC_Q_GAME_LOSE,
                                                     get_belly_formatted(lose_amount),
                                                     user.get_bounty_formatted())

        # Send outcome text
        await full_media_send(context, update=update, caption=ot_text, edit_only_caption_and_keyboard=True,
                              add_delete_button=True)

        # Save update
        user.doc_q_cooldown_end_date = get_datetime(
            user, DevilFruitAbilityType.DOC_Q_COOLDOWN_DURATION, Env.DOC_Q_GAME_COOLDOWN_DURATION.get_int())
        doc_q_game.save()


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, keyboard: Keyboard,
                 group_chat: GroupChat) -> None:
    """
    Manage Doc Q Game screen
    :param update: The update
    :param context: The context
    :param user: The user
    :param keyboard: The keyboard
    :param group_chat: The group chat
    :return: None
    """
    # Request to play
    if keyboard is None:
        await play_request(update, context, user, group_chat)
        return

    await keyboard_interaction(update, context, user, keyboard)
