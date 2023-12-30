from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.Screen import Screen
from src.model.enums.crew.CrewChestSpendingReason import CrewChestSpendingReason
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew, get_crew_abilities_text
from src.service.message_service import full_message_send


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the Crew ability screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    try:
        crew: Crew = get_crew(user=user)
    except CrewValidationException as cve:
        await full_message_send(
            context, cve.message, update=update, inbound_keyboard=inbound_keyboard
        )
        return

    # Get all active abilities
    active_abilities = crew.get_active_abilities()

    inline_keyboard: list[list[Keyboard]] = []

    if user.is_crew_captain_or_first_mate() and len(active_abilities) < crew.max_abilities:
        # Activate ability button
        inline_keyboard.append([
            Keyboard(
                phrases.PVT_KEY_CREW_ABILITY_ACTIVATE, screen=Screen.PVT_CREW_ABILITY_ACTIVATE
            )
        ])

    abilities_text = get_crew_abilities_text(active_abilities=active_abilities, add_duration=True)

    ot_text = phrases.CREW_ABILITIES.format(
        abilities_text,
        crew.get_powerup_price_formatted(CrewChestSpendingReason.ABILITY),
        crew.get_crew_chest_formatted(),
    )

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )
