import asyncio

from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Game import Game
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.game.GameOutcome import GameOutcome
from src.model.game.punkrecords.PunkRecords import PunkRecords, RevealedDetail
from src.service.game_service import (
    set_user_private_screen,
    save_game,
    get_terminology_from_game,
    get_players,
    end_game,
    end_text_based_game,
    get_player_board,
    get_guess_game_users_to_send_message_to,
    should_proceed_after_hint_sleep,
    end_global_guess_game_challenger,
    get_global_time_based_text,
    get_global_text_challenger_finished,
    get_winner_loser_text,
)
from src.service.message_service import full_message_send, escape_valid_markdown_chars


def get_recap_details(
    game: Game,
    user: User,
    last_detail: RevealedDetail = None,
    all_details_are_new: bool = False,
    add_instructions: bool = False,
    hint_text: str = None,
) -> str:
    """
    Get the specific text
    :param game: The game object
    :param user: The user to get the recap text for
    :param last_detail: The last detail revealed
    :param all_details_are_new: If all details are new
    :param add_instructions: If instructions should be added
    :param hint_text: The hint text
    :return: The recap text
    """

    def detail_is_last_detail(_name: str, _value: str, _last_detail) -> bool:
        if _last_detail is None:
            return False

        return _last_detail.name == _name and _last_detail.value == _value

    board: PunkRecords = get_player_board(game, user)

    ot_text_list = []
    for name in board.revealed_details:
        values = board.get_revealed_detail(name)

        if isinstance(values, str):
            ot_text_detail = phrases.PUNK_RECORDS_GAME_RECAP_DETAIL.format(
                (
                    Emoji.NEW
                    if detail_is_last_detail(name, values, last_detail) or all_details_are_new
                    else ""
                ),
                name,
                escape_valid_markdown_chars(values),
            )
        else:
            list_details = []
            for value in values:
                item_detail = (
                    Emoji.NEW
                    if detail_is_last_detail(name, value, last_detail) or all_details_are_new
                    else ""
                ) + value
                list_details.append(item_detail)
            ot_text_detail = phrases.PUNK_RECORDS_GAME_RECAP_DETAIL_LIST.format(
                name, escape_valid_markdown_chars("\n".join(list_details))
            )

        ot_text_list.append(ot_text_detail)

    ot_text = "\n".join(ot_text_list)

    if hint_text is not None:
        ot_text += hint_text

    if game.is_global():
        ot_text += "\n"
        ot_text += get_global_time_based_text(game, user)

        if game.is_challenger(user) and game.challenger_has_finished():
            ot_text += get_global_text_challenger_finished(
                game, should_add_already_guessed_text=False
            )

    if add_instructions:
        ot_text += "\n\n" + phrases.GUESS_CHARACTER_GAME_INPUT_CAPTION

    return ot_text


async def run_game(
    context: ContextTypes.DEFAULT_TYPE,
    game: Game,
    user: User,
    should_send_to_all_players: bool = True,
    schedule_next_send: bool = True,
    hint_wait_seconds: int = None,
    is_first_run: bool = True,
) -> None:
    """
    Send the details box
    :param context: The context object
    :param game: The game object
    :param user: The user to send the image to
    :param should_send_to_all_players: If the image should be sent to all players
    :param schedule_next_send: If the next send should be scheduled
    :param hint_wait_seconds: How many seconds to wait before issuing next hint. If none, the game default is used
    :param is_first_run: If it's the first run
    :return: None
    """

    hint_wait_seconds = (
        hint_wait_seconds if hint_wait_seconds is not None else game.get_seconds_for_every_hint()
    )

    # From auto restart
    if hint_wait_seconds != game.get_seconds_for_every_hint():
        is_first_run = False

    users = await get_guess_game_users_to_send_message_to(
        game,
        user,
        (should_send_to_all_players and not game.is_global()),
        schedule_next_send,
    )

    # Get the board
    board: PunkRecords = get_player_board(game, user)

    # If detail can be revealed, add new revealed detail to text
    recap_text = ""
    new_detail_text = ""
    hint_text = ""
    new_detail = None
    # First iteration, do not reveal new detail or hint
    if not is_first_run:  # FIXME
        issue_hint_if_possible(game, user)
        board: PunkRecords = get_player_board(game, user)

    if board.revealed_letters_count > 0:
        # Add hint, goes on bottom of text just before time remaining to next hint
        hint = board.character.name[: board.revealed_letters_count]
        hint_text = phrases.GUESS_GAME_INPUT_CAPTION_HINT.format(hint)

    # Time remaining text, always after everything else
    if board.can_reveal_detail():
        recap_text += phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_DETAIL.format(
            hint_wait_seconds
        )
    elif not board.have_revealed_all_letters():
        recap_text += phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_HINT.format(
            hint_wait_seconds
        )

    ot_text = new_detail_text + phrases.PUNK_RECORDS_GAME_RECAP.format(
        get_recap_details(
            game,
            user,
            new_detail,
            all_details_are_new=is_first_run,
            add_instructions=True,
            hint_text=hint_text,
        ),
        recap_text,
    )
    for u in users:
        context.application.create_task(full_message_send(context, ot_text, chat_id=u.tg_user_id))

        # Set private screen for input
        context.application.create_task(set_user_private_screen(u, game))

    if not schedule_next_send:
        return

    await asyncio.sleep(hint_wait_seconds)

    # Refresh game, resend only if it's still ongoing
    game: Game = Game.get_by_id(game.id)

    if not await should_proceed_after_hint_sleep(context, game, user):
        return

    # Revealed all details and all letters
    if board.have_revealed_all_letters() and not board.can_reveal_detail():
        return

    await run_game(context, game, user, is_first_run=False)


async def validate_answer(
    update: Update, context: ContextTypes.DEFAULT_TYPE, game: Game, user: User
) -> None:
    """
    Validate the answer
    :param update: The update object
    :param context: The context object
    :param game: The game object
    :param user: The user object
    :return: None
    """

    try:
        answer = update.effective_message.text
    except AttributeError:
        return

    terminology = get_terminology_from_game(game)

    if not terminology.name.lower() == answer.lower():
        return

    # Correct word but game not finished
    if game.is_global() and game.is_challenger(user):
        # Set challenger and time and try enqueueing opponent timeout
        await end_global_guess_game_challenger(context, game)

        details_text = phrases.PUNK_RECORDS_GAME_RECAP.format(get_recap_details(game, user), "")

        ot_text = phrases.GUESS_GAME_CORRECT_ANSWER.format(details_text)
        await full_message_send(context, ot_text, update=update)

        return

    # End game
    challenger, opponent = get_players(game)
    outcome: GameOutcome = (
        GameOutcome.CHALLENGER_WON if user == challenger else GameOutcome.OPPONENT_WON
    )
    await end_game(game, outcome, context, update=update)
    user.should_update_model = False  # To avoid re-writing bounty
    loser = challenger if user == opponent else opponent

    details_text = phrases.PUNK_RECORDS_GAME_RECAP.format(get_recap_details(game, user), "")
    winner_text, loser_text = get_winner_loser_text(game, details_text)

    await end_text_based_game(context, game, outcome, user, winner_text, loser, loser_text)


def issue_hint_if_possible(game: Game, user: User) -> bool:
    """
    Issue a hint if possible, saving the game
    :param game: The game
    :param user: The user
    :return: If a life was issued
    """
    board: PunkRecords = get_player_board(game, user)

    if not board.can_reveal_detail() and board.have_revealed_all_letters():
        return False

    if board.can_reveal_detail():
        # New detail goes on top of text
        new_detail = board.get_random_detail_to_reveal()
        board.set_revealed_detail(new_detail)
    else:
        board.revealed_letters_count += 1

    save_game(
        game,
        board.get_as_json_string(),
        is_opponent_board=game.is_opponent(user),
        hint_was_issued=True,
    )

    return True
