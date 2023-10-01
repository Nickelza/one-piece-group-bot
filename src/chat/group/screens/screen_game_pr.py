import asyncio
import json

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.model.Game import Game
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.GameStatus import GameStatus
from src.model.enums.Screen import Screen
from src.model.game.GameOutcome import GameOutcome
from src.model.game.punkrecords.PunkRecords import PunkRecords, RevealedDetail
from src.model.pojo.Keyboard import Keyboard
from src.model.wiki.Character import Character
from src.model.wiki.SupabaseRest import SupabaseRest
from src.service.game_service import set_user_private_screen, guess_game_countdown_to_start, save_game, \
    get_terminology_from_game, validate_game, get_players, end_game, end_text_based_game
from src.service.message_service import full_message_send, escape_valid_markdown_chars


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, game: Game = None
                 ) -> None:
    """
    Manage the Punk Records screen
    :param update: The update object
    :param context: The context object
    :param inbound_keyboard: The inbound keyboard
    :param game: The game object
    :return: None
    """

    # Get the game from validation, will handle error messages
    game = await validate_game(update, context, inbound_keyboard, game)
    if game is None:
        return

    # Init board
    get_board(game)

    # From opponent confirmation, start countdown
    if inbound_keyboard.screen == Screen.GRP_GAME_OPPONENT_CONFIRMATION:
        game.status = GameStatus.COUNTDOWN_TO_START
        game.save()
        context.application.create_task(
            guess_game_countdown_to_start(update, context, game, Env.GAME_START_WAIT_TIME.get_int(), run_game))
        return


def get_board(game: Game) -> PunkRecords:
    """
    Get the board
    :param game: The game object
    :return: The board
    """

    # Create board
    if game.board is None:
        random_character: Character = SupabaseRest.get_random_character(game.get_difficulty())
        punk_records = PunkRecords(random_character)
        save_game(game, punk_records.get_board_json())
        return punk_records

    # Parse the JSON string and create a Character object
    json_dict = json.loads(game.board)
    char_dict = json_dict.pop("character")
    char: Character = Character(**char_dict)

    # Create a PunkRecords object with attribute unpacking
    return PunkRecords(character=char, **json_dict)


def get_recap_details(punk_records: PunkRecords, last_detail: RevealedDetail = None, all_details_are_new: bool = False,
                      add_instructions: bool = False) -> str:
    """
    Get the specific text
    :param punk_records: The board
    :param last_detail: The last detail revealed
    :param all_details_are_new: If all details are new
    :param add_instructions: If instructions should be added
    :return: The recap text
    """

    def detail_is_last_detail(_name: str, _value: str, _last_detail) -> bool:
        if _last_detail is None:
            return False

        return _last_detail.name == _name and _last_detail.value == _value

    ot_text_list = []
    for name in punk_records.revealed_details:
        values = punk_records.get_revealed_detail(name)

        if isinstance(values, str):
            ot_text_detail = phrases.PUNK_RECORDS_GAME_RECAP_DETAIL.format(
                (Emoji.NEW if detail_is_last_detail(name, values, last_detail) or all_details_are_new else ''),
                name, escape_valid_markdown_chars(values))
        else:
            list_details = []
            for value in values:
                item_detail = (Emoji.NEW
                               if detail_is_last_detail(name, value, last_detail) or all_details_are_new
                               else '') + value
                list_details.append(item_detail)
            ot_text_detail = phrases.PUNK_RECORDS_GAME_RECAP_DETAIL_LIST.format(
                name, escape_valid_markdown_chars('\n'.join(list_details)))

        ot_text_list.append(ot_text_detail)

    ot_text = '\n'.join(ot_text_list)

    if add_instructions:
        ot_text += '\n\n_' + phrases.GUESS_CHARACTER_GAME_INPUT_CAPTION + '_'

    return ot_text


async def run_game(context: ContextTypes.DEFAULT_TYPE, game: Game, send_to_user: User = None,
                   should_send_to_all_players: bool = True, schedule_next_send: bool = True,
                   is_first_run: bool = True) -> None:
    """
    Send the details box
    :param context: The context object
    :param game: The game object
    :param send_to_user: The user to send the image to
    :param should_send_to_all_players: If the image should be sent to all players
    :param schedule_next_send: If the next send should be scheduled
    :param is_first_run: If it's the first run
    :return: None
    """

    if send_to_user is not None and should_send_to_all_players:
        raise ValueError('Cannot send to user and all players')

    if not should_send_to_all_players and schedule_next_send:
        raise ValueError('Cannot schedule next send if not sending to all players')

    if send_to_user is not None:
        users: list[User] = [send_to_user]
    else:
        challenger: User = game.challenger
        opponent: User = game.opponent
        users: list[User] = [challenger, opponent]

    # Get the board
    punk_records = get_board(game)

    # If detail can be revealed, add new revealed detail to text
    recap_text = ''
    new_detail_text = ''
    new_detail = None
    # First iteration, do not reveal new detail or hint
    if not is_first_run:
        if punk_records.can_reveal_detail():
            # New detail goes on top of text
            new_detail = punk_records.get_random_detail_to_reveal()
            punk_records.set_revealed_detail(new_detail)
        else:
            if not punk_records.have_revealed_all_letters():
                punk_records.revealed_letters_count += 1

        # Add hint, goes on bottom of text just before time remaining to next hint
        hint = punk_records.character.name[:punk_records.revealed_letters_count]
        recap_text = '\n' + phrases.GUESS_GAME_INPUT_CAPTION_HINT.format(hint)

    save_game(game, punk_records.get_board_json())

    # Time remaining text, always after everything else
    if punk_records.can_reveal_detail():
        recap_text += '\n' + phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_DETAIL.format(
            Env.PUNK_RECORDS_NEXT_DETAIL_WAIT_TIME.get_int())
    elif not punk_records.have_revealed_all_letters():
        recap_text += '\n' + phrases.GUESS_GAME_INPUT_CAPTION_SECONDS_TO_NEXT_HINT.format(
            Env.PUNK_RECORDS_NEXT_DETAIL_WAIT_TIME.get_int())

    # Refresh board
    punk_records = get_board(game)

    ot_text = new_detail_text + phrases.PUNK_RECORDS_GAME_RECAP.format(
        get_recap_details(
            punk_records, new_detail, add_instructions=True, all_details_are_new=is_first_run), recap_text)
    for user in users:
        context.application.create_task(full_message_send(context, ot_text, chat_id=user.tg_user_id))

        # Set private screen for input
        context.application.create_task(set_user_private_screen(user, game))

    if not schedule_next_send:
        return

    await asyncio.sleep(Env.PUNK_RECORDS_NEXT_DETAIL_WAIT_TIME.get_int())

    # Refresh game, resend only if it's still ongoing
    game = Game.get_by_id(game.id)
    if GameStatus(game.status) is not GameStatus.IN_PROGRESS:
        return

    # Revealed all details and all letters
    if punk_records.have_revealed_all_letters() and not punk_records.can_reveal_detail():
        return

    await run_game(context, game, is_first_run=False)


async def validate_answer(update: Update, context: ContextTypes.DEFAULT_TYPE, game: Game, user: User
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

    terminology = await get_terminology_from_game(game)

    if not terminology.name.lower() == answer.lower():
        return

    # End game
    challenger, opponent = get_players(game)
    outcome: GameOutcome = GameOutcome.CHALLENGER_WON if user == challenger else GameOutcome.OPPONENT_WON
    await end_game(game, outcome, update=update)
    user.should_update_model = False  # To avoid re-writing bounty
    loser = challenger if user == opponent else opponent

    details_text = phrases.PUNK_RECORDS_GAME_RECAP.format(get_recap_details(get_board(game)), '')
    winner_text = phrases.GUESS_GAME_CORRECT_ANSWER.format(details_text)
    loser_text: str = phrases.GUESS_GAME_OPPONENT_CORRECT_ANSWER.format(details_text)

    await end_text_based_game(context, game, outcome, user, winner_text, loser, loser_text)
