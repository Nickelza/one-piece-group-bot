from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.chat.private.screens.screen_crew_member import CrewMemberListPage
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew
from src.service.message_service import full_message_send


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
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
    crew_member_list_page.set_object(
        inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY)
    )

    member: User = crew_member_list_page.object
    crew: Crew = get_crew(user=user)
    inline_keyboard: list[list[Keyboard]] = []

    # Captain buttons
    if user.is_crew_captain() and user != member:
        # Promote to First Mate (only Crew does not have a First Mate and can promote one)
        if not crew.has_first_mate() and crew.can_promote_first_mate:
            inline_keyboard.append([
                Keyboard(
                    phrases.PVT_KEY_CREW_MEMBER_FIRST_MATE_PROMOTE,
                    screen=Screen.PVT_CREW_MEMBER_DETAIL_FIRST_MATE_PROMOTE,
                    info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: member.id},
                    inbound_info=inbound_keyboard.info,
                )
            ])

        # Demote from First Mate (only if the member is the First Mate)
        if member.is_crew_first_mate():
            inline_keyboard.append([
                Keyboard(
                    phrases.PVT_KEY_CREW_MEMBER_FIRST_MATE_DEMOTE,
                    screen=Screen.PVT_CREW_MEMBER_DETAIL_FIRST_MATE_DEMOTE,
                    info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: member.id},
                    inbound_info=inbound_keyboard.info,
                )
            ])
        # Remove member
        inline_keyboard.append([
            Keyboard(
                phrases.PVT_KEY_CREW_MEMBER_REMOVE,
                screen=Screen.PVT_CREW_MEMBER_DETAIL_REMOVE,
                info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: member.id},
                inbound_info=inbound_keyboard.info,
            )
        ])

    await full_message_send(
        context,
        crew_member_list_page.get_item_detail_text(),
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )
