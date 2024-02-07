from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.private.screens.screen_crew_search import CrewSearchListPage
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
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

    inline_keyboard: list[list[Keyboard]] = [
        [
            # Join
            Keyboard(
                phrases.PVT_KEY_CREW_SEARCH_JOIN,
                screen=Screen.PVT_CREW_SEARCH_DETAIL_JOIN,
                info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: crew_search_list_page.object.id},
                inbound_info=inbound_keyboard.info,
            )
        ],
    ]

    # TODO Don't show DBF button if target crew can't participate
    # Davy Back Fight, only in case user is crew captain
    if user.is_crew_captain() and crew_search_list_page.object != user.crew:
        inline_keyboard.append([
            Keyboard(
                phrases.PVT_KEY_CREW_DAVY_BACK_FIGHT,
                screen=Screen.PVT_CREW_DAVY_BACK_FIGHT_REQUEST,
                info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: crew_search_list_page.object.id},
                inbound_info=inbound_keyboard.info,
            )
        ])

    await full_message_send(
        context,
        crew_search_list_page.get_item_detail_text(),
        update=update,
        inbound_keyboard=inbound_keyboard,
        keyboard=inline_keyboard,
    )
