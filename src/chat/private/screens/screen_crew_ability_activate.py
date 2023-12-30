from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.CrewAbility import CrewAbility
from src.model.User import User
from src.model.enums.Screen import Screen
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew
from src.service.message_service import full_message_send


class CrewAbilityActivateReservedKeys(StrEnum):
    """
    The reserved keys for the Crew ability activate screen
    """

    ABILITY_TYPE = "a"


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the Crew ability activate choose screen
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

    if not await validate(update, context, inbound_keyboard, crew):
        return

    allowed_ability_types = CrewAbility.get_allowed_ability_types()
    inline_keyboard: list[list[Keyboard]] = []

    screen = Screen.PVT_CREW_ABILITY_ACTIVATE_CONFIRM
    for ability_type in allowed_ability_types:
        info = {CrewAbilityActivateReservedKeys.ABILITY_TYPE: ability_type}
        inline_keyboard.append(
            [Keyboard(ability_type.get_description(), info=info, screen=screen)]
        )

    # Add random ability
    info = {CrewAbilityActivateReservedKeys.ABILITY_TYPE: None}
    inline_keyboard.append(
        [Keyboard(phrases.PVT_KEY_CREW_ABILITY_RANDOM, info=info, screen=screen)]
    )

    await full_message_send(
        context,
        phrases.CREW_ABILITY_ACTIVATE_CHOOSE,
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )


async def validate(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, crew: Crew
) -> bool:
    """
    Validate the crew ability add screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param crew: The crew
    :return: None
    """

    try:
        active_abilities = crew.get_active_abilities()

        # Insufficient crew chest amount
        if crew.chest_amount < crew.get_powerup_price():
            raise CrewValidationException(
                phrases.CREW_ABILITY_INSUFFICIENT_CREW_CHEST.format(
                    crew.get_crew_chest_formatted(), crew.get_powerup_price_formatted()
                )
            )

        # Abilities limit reached
        if len(active_abilities) >= crew.max_abilities:
            raise CrewValidationException(phrases.CREW_USER_ALREADY_IN_CREW)
    except CrewValidationException as e:

        # Show alert if callback else send a message
        await full_message_send(
            context,
            str(e),
            update=update,
            answer_callback=True,
            show_alert=True,
            inbound_keyboard=inbound_keyboard,
        )
        return False

    return True
