from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.model.Crew import Crew
from src.model.DavyBackFight import DavyBackFight
from src.model.DavyBackFightParticipant import DavyBackFightParticipant
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew
from src.service.message_service import full_message_send


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    dbf: DavyBackFight = DavyBackFight.get_by_id(
        inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY)
    )
    crew: Crew = get_crew(user)

    team_mates_text = ""
    opponents_text = ""
    for p in DavyBackFightParticipant.get_participants_by_contribution(dbf):
        # Show basic recap
        text = phrases.CREW_DAVY_BACK_FIGHT_PARTICIPANTS_ITEM.format(
            p.user.get_markdown_mention(), p.get_contribution_formatted()
        )

        # Show potential win
        if dbf.in_progress():
            text += phrases.CREW_DAVY_BACK_FIGHT_PARTICIPANTS_ITEM_POTENTIAL_WIN.format(
                p.get_win_amount_formatted()
            )
        # Show effective win
        elif p.in_winner_crew():
            text += phrases.CREW_DAVY_BACK_FIGHT_PARTICIPANTS_ITEM_WIN.format(
                p.get_win_amount_formatted()
            )

        if p.crew == crew:
            team_mates_text += text
        else:
            opponents_text += text

    inline_keyboard: list[list[Keyboard]] = []

    # Select participants button, only for Captain if the davy back fight is not started
    if dbf.get_status() is GameStatus.COUNTDOWN_TO_START and user.is_crew_captain():
        inline_keyboard.append([
            Keyboard(
                phrases.PVT_KEY_CREW_DAVY_BACK_FIGHT_PARTICIPANT_SELECT,
                inbound_info=inbound_keyboard.info,
                screen=Screen.PVT_CREW_DAVY_BACK_FIGHT_DETAIL_PARTICIPANTS_SELECT,
            )
        ])

    await full_message_send(
        context,
        phrases.CREW_DAVY_BACK_FIGHT_PARTICIPANTS.format(team_mates_text.rstrip(), opponents_text),
        update=update,
        inbound_keyboard=inbound_keyboard,
        keyboard=inline_keyboard,
    )
