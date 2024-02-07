from telegram import Update
from telegram.ext import ContextTypes

from src.chat.private.screens.screen_crew_davy_back_fight import CrewDavyBackFightListPage
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

    dbf_list_page = CrewDavyBackFightListPage()

    dbf_list_page.user = user
    dbf_list_page.crew = user.crew
    dbf_list_page.init_legend_filter_results()
    dbf_list_page.set_object(inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY))

    inline_keyboard: list[list[Keyboard]] = []

    # TODO if "skip_list" key is set, show "Show list" button
    # Arrested user, show Post bail button if it's temporary
    # if member.is_arrested_temporary():
    #     inline_keyboard.append([
    #         Keyboard(
    #             phrases.PVT_KEY_CREW_MEMBER_POST_BAIL,
    #             screen=Screen.PVT_CREW_MEMBER_DETAIL_POST_BAIL,
    #             info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: member.id},
    #             inbound_info=inbound_keyboard.info,
    #         )
    #     ])

    await full_message_send(
        context,
        dbf_list_page.get_item_detail_text(),
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )
