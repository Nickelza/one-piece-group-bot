from telegram import Update
from telegram.ext import ContextTypes

from src.chat.private.screens.screen_crew_search import CrewSearchListPage
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the Crew member screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """
    crew_search_list_page: CrewSearchListPage = CrewSearchListPage()
    crew_search_list_page.user = user
    crew_search_list_page.set_object(
        inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY)
    )

    await full_message_send(
        context,
        crew_search_list_page.get_item_detail_text(),
        update=update,
        inbound_keyboard=inbound_keyboard,
    )
