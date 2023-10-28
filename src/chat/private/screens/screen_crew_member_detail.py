from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.chat.private.screens.screen_crew_member import CrewMemberListPage
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the Crew member detail screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    crew_member_list_page = CrewMemberListPage()

    crew_member_list_page.user = user
    crew_member_list_page.set_object(inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY))

    member: User = crew_member_list_page.object
    inline_keyboard: list[list[Keyboard]] = []

    # Show remove button if user is captain and member is not captain
    if user.is_crew_captain() and user != member:
        inline_keyboard.append([Keyboard(phrases.PVT_KEY_CREW_MEMBER_REMOVE,
                                         screen=Screen.PVT_CREW_MEMBER_DETAIL_REMOVE,
                                         info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: member.id},
                                         inbound_info=inbound_keyboard.info)])

    await full_message_send(context, crew_member_list_page.get_item_detail_text(), update=update,
                            keyboard=inline_keyboard, inbound_keyboard=inbound_keyboard)
