import datetime
from math import ceil

from telegram import Update, Message
from telegram.ext import ContextTypes

import resources.Environment as Env
from resources import phrases
from src.model.BountyLoan import BountyLoan
from src.model.GroupChat import GroupChat
from src.model.Plunder import Plunder
from src.model.User import User
from src.model.enums.BountyLoanSource import BountyLoanSource
from src.model.enums.GameStatus import GameStatus
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.enums.impel_down.ImpelDownBountyAction import ImpelDownBountyAction
from src.model.enums.impel_down.ImpelDownSentenceType import ImpelDownSentenceType
from src.model.enums.impel_down.ImpelDownSource import ImpelDownSource
from src.model.enums.income_tax.IncomeTaxEventType import IncomeTaxEventType
from src.model.error.CustomException import OpponentValidationException
from src.model.error.GroupChatError import GroupChatError, GroupChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_loan_service import add_loan
from src.service.bounty_service import add_or_remove_bounty, validate_amount
from src.service.date_service import (
    convert_seconds_to_duration,
    get_elapsed_hours,
    get_datetime_in_future_hours,
    convert_hours_to_duration,
)
from src.service.devil_fruit_service import get_ability_adjusted_datetime, get_ability_value
from src.service.impel_down_service import add_sentence
from src.service.math_service import get_random_win, get_value_from_percentage
from src.service.message_service import (
    full_message_send,
    mention_markdown_user,
    get_yes_no_keyboard,
    full_media_send,
    full_message_or_media_send_or_edit,
    delete_message,
)
from src.service.string_service import get_belly_formatted


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    keyboard: Keyboard,
    group_chat: GroupChat,
) -> None:
    """
    Manage the plunder request
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

    # Request to plunder
    if keyboard is None:
        await send_request(update, context, user, group_chat)
        return

    await keyboard_interaction(update, context, user, keyboard, group_chat)


def get_opponent(update: Update = None, keyboard: Keyboard = None) -> User | None:
    """
    Get opponent from update or keyboard
    :param update: The update object. If None, the opponent is taken from the keyboard
    :param keyboard: The keyboard object. If None, the opponent is taken from the update
    :return: The opponent object
    """

    if update.callback_query is None:
        return User.get_or_none(User.tg_user_id == update.message.reply_to_message.from_user.id)

    plunder: Plunder = Plunder.get_or_none(
        Plunder.id == int(keyboard.info[ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY])
    )
    if plunder is None:
        return None
    return plunder.opponent


async def validate(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, keyboard: Keyboard = None
) -> bool:
    """
    Validate the plunder request
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param keyboard: The keyboard object
    :return: True if the request is valid, False otherwise
    """
    # If not query callback
    plunder: Plunder | None = None
    if update.callback_query is not None:
        # Get opponent from plunder id
        plunder: Plunder = Plunder.get_or_none(
            Plunder.id == int(keyboard.info[ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY])
        )
        if plunder is None:
            raise GroupChatException(GroupChatError.ITEM_NOT_FOUND)

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
        now = datetime.datetime.now()
        if (
            opponent.plunder_immunity_end_date is not None
            and opponent.plunder_immunity_end_date > now
        ):
            raise OpponentValidationException()

        # Opponent is arrested
        if opponent.is_arrested():
            raise OpponentValidationException()

        # Opponent in your same crew
        if user.is_crew_member() and user.crew == opponent.crew:
            raise OpponentValidationException(phrases.PLUNDER_CANNOT_PLUNDER_CREW_MEMBER)

    except OpponentValidationException as ove:
        if ove.message is not None:
            await full_message_or_media_send_or_edit(context, ove.message, update)
        else:
            await full_message_or_media_send_or_edit(
                context, phrases.PLUNDER_CANNOT_PLUNDER_USER, update=update, add_delete_button=True
            )
        return False

    # User is in plunder cooldown
    if user.plunder_cooldown_end_date is not None and user.plunder_cooldown_end_date > now:
        # Get remaining time
        remaining_time = convert_seconds_to_duration(
            (user.plunder_cooldown_end_date - datetime.datetime.now()).total_seconds()
        )
        ot_text = phrases.PLUNDER_USER_IN_COOLDOWN.format(remaining_time)
        await full_message_or_media_send_or_edit(context, ot_text, update, add_delete_button=True)
        return False

    # User does not have enough bounty
    win_amount = (get_plunder_odds(user, opponent))[1]
    if not await validate_amount(update, context, user, win_amount):
        return False

    # Wrong status
    if plunder is not None and plunder.get_status() is not GameStatus.IN_PROGRESS:
        raise GroupChatException(GroupChatError.ITEM_IN_WRONG_STATUS)

    return True


def get_plunder_odds(
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


async def delete_plunder(
    context: ContextTypes.DEFAULT_TYPE, plunder: Plunder, group_chat: GroupChat
) -> None:
    """
    Delete plunder
    :param context: The context
    :param plunder: The plunder
    :param group_chat: The group chat
    :return: None
    """
    # Try to delete message
    await delete_message(context=context, group_chat=group_chat, message_id=plunder.message_id)

    # Delete plunder
    plunder.delete_instance()


async def send_request(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, group_chat: GroupChat
) -> None:
    """
    Send request to confirm plunder
    :param update: The update
    :param context: The context
    :param user: The user
    :param group_chat: The group chat
    :return: None
    """

    # Delete all previous pending plunders
    previous_plunders: list[Plunder] = Plunder.select().where(
        (Plunder.challenger == user) & (Plunder.status == GameStatus.IN_PROGRESS)
    )
    for previous_plunder in previous_plunders:
        await delete_plunder(context, previous_plunder, group_chat)

    # Get opponent
    opponent: User = get_opponent(update)
    (
        win_probability,
        win_amount,
        lose_amount,
        win_percentage,
        final_bounty_if_win,
        final_bounty_if_lose,
        sentence,
    ) = get_plunder_odds(user, opponent)

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
        mention_markdown_user(user),
        mention_markdown_user(opponent),
        get_belly_formatted(win_amount),
        get_belly_formatted(lose_amount),
        convert_hours_to_duration(sentence, show_full=True),
        plunder.win_probability,
        user.get_bounty_formatted(),
        get_belly_formatted(final_bounty_if_win),
        get_belly_formatted(final_bounty_if_lose),
    )

    # Keyboard
    inline_keyboard: list[list[Keyboard]] = [
        get_yes_no_keyboard(
            user,
            screen=Screen.GRP_PLUNDER,
            yes_text=phrases.KEYBOARD_OPTION_PLUNDER,
            no_text=phrases.KEYBOARD_OPTION_RETREAT,
            primary_key=plunder.id,
        )
    ]

    message: Message = await full_media_send(
        context,
        saved_media_name=SavedMediaName.PLUNDER,
        update=update,
        caption=caption,
        keyboard=inline_keyboard,
    )

    plunder.message_id = message.message_id
    plunder.save()


async def keyboard_interaction(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    keyboard: Keyboard,
    group_chat: GroupChat,
) -> None:
    """
    Keyboard interaction
    :param update: The update
    :param context: The context
    :param user: The user
    :param keyboard: The keyboard
    :param group_chat: The group chat
    :return: None
    """

    # Get plunder
    plunder: Plunder = Plunder.get_or_none(
        Plunder.id == keyboard.info[ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY]
    )

    # User clicked on retreat button
    if not keyboard.info[ReservedKeyboardKeys.CONFIRM]:
        # Answer callback with retreat message
        await full_message_send(
            context, phrases.FIGHT_CONFIRMATION_RETREAT, update, answer_callback=True
        )
        await delete_plunder(context, plunder, group_chat)
        return

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
    ) = get_plunder_odds(user, opponent)

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
            update=update,
            tax_event_type=IncomeTaxEventType.PLUNDER,
            event_id=plunder.id,
            should_save=True,
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

    # Send message
    await full_media_send(
        context,
        saved_media_name=saved_media_name,
        caption=caption,
        update=update,
        add_delete_button=True,
    )

    # Save info
    opponent.save()
    plunder.save()
