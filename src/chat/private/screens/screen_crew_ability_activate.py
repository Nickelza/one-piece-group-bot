from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.User import User
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew
from src.service.message_service import full_message_send


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the Crew ability activate screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    try:
        crew: Crew = get_crew(user=user)
    except CrewValidationException as cve:
        await full_message_send(context, cve.message, update=update, inbound_keyboard=inbound_keyboard)
        return

    if not await validate(update, context, inbound_keyboard, crew):
        return

    await full_message_send(
        context, "Awkward, this is not implemented yet, never thought a Crew would get here this fast."
                 "\nForward this message to an Admin in @onepiecegroup to get a special price",
        update=update, inbound_keyboard=inbound_keyboard)


async def validate(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, crew: Crew) -> bool:
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
            raise CrewValidationException(phrases.CREW_ABILITY_INSUFFICIENT_CREW_CHEST.format(
                crew.get_crew_chest_formatted(), crew.get_powerup_price_formatted()
            ))

        # Abilities limit reached
        if len(active_abilities) >= crew.max_abilities:
            raise CrewValidationException(phrases.CREW_USER_ALREADY_IN_CREW)
    except CrewValidationException as e:

        # Show alert if callback else send a message
        await full_message_send(context, str(e), update=update, answer_callback=True, show_alert=True,
                                inbound_keyboard=inbound_keyboard)
        return False

    return True
