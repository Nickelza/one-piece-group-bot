from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew, get_crew_overview_text
from src.service.message_service import full_message_send


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the crew screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    inline_keyboard: list[list[Keyboard]] = []
    if not user.is_crew_member():
        ot_text = phrases.CREW_USER_NOT_IN_CREW

        # Create crew button
        inline_keyboard.append(
            [Keyboard(phrases.KEY_CREATE, screen=Screen.PVT_CREW_CREATE_OR_EDIT)]
        )
    else:
        crew: Crew = get_crew(user=user)

        ot_text = get_crew_overview_text(crew, user, from_search=False)

        # Members button
        inline_keyboard.append(
            [Keyboard(phrases.PVT_KEY_CREW_MEMBERS, screen=Screen.PVT_CREW_MEMBER)]
        )

        # Powerup button
        inline_keyboard.append(
            [Keyboard(phrases.PVT_KEY_CREW_POWERUP, screen=Screen.PVT_CREW_POWERUP)]
        )

        if user.is_crew_captain():
            # Modify button
            inline_keyboard.append([Keyboard(phrases.KEY_MODIFY, screen=Screen.PVT_CREW_MODIFY)])
        else:
            # Leave crew button
            inline_keyboard.append(
                [Keyboard(phrases.PVT_KEY_CREW_LEAVE, screen=Screen.PVT_CREW_LEAVE)]
            )

        # Search button
        inline_keyboard.append(
            [Keyboard(phrases.PVT_KEY_CREW_SEARCH, screen=Screen.PVT_CREW_SEARCH)]
        )

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
        excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE],
    )
