from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.private.screens.screen_crew_davy_back_fight import CrewDavyBackFightListPage
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.list_service import get_show_list_button
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

    dbf_list_page = CrewDavyBackFightListPage()

    dbf_list_page.user = user
    dbf_list_page.crew = user.crew
    dbf_list_page.init_legend_filter_results()
    dbf_list_page.set_object(inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY))

    # View participants button
    inline_keyboard: list[list[Keyboard]] = [[
        Keyboard(
            phrases.PVT_KEY_CREW_DAVY_BACK_FIGHT_PARTICIPANT_VIEW,
            inbound_info=inbound_keyboard.info,
            screen=Screen.PVT_CREW_DAVY_BACK_FIGHT_DETAIL_PARTICIPANTS_VIEW,
        )
    ]]
    if (
        ReservedKeyboardKeys.DIRECT_ITEM in inbound_keyboard.info
        and inbound_keyboard.info[ReservedKeyboardKeys.DIRECT_ITEM]
    ):
        # Show list button
        inline_keyboard.append([get_show_list_button(inbound_keyboard)])

    await full_message_send(
        context,
        dbf_list_page.get_item_detail_text(),
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )
