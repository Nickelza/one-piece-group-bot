from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.model.Crew import Crew
from src.model.DavyBackFight import DavyBackFight
from src.model.DavyBackFightParticipant import DavyBackFightParticipant
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.pojo.Keyboard import Keyboard
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
    crew: Crew = user.crew

    team_mates_text = ""
    opponents_text = ""
    for p in DavyBackFightParticipant.get_participants_by_contribution(dbf):
        text = phrases.CREW_DAVY_BACK_FIGHT_PARTICIPANTS_ITEM.format(
            p.user.get_markdown_mention(), p.get_contribution_formatted()
        )
        if p.crew == crew:
            team_mates_text += text
        else:
            opponents_text += text

    await full_message_send(
        context,
        phrases.CREW_DAVY_BACK_FIGHT_PARTICIPANTS.format(team_mates_text, opponents_text),
        update=update,
        inbound_keyboard=inbound_keyboard,
    )
