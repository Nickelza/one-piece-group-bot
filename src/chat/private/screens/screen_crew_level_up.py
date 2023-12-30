from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.chat.private.screens.screen_crew_level import get_level_up_recap_text
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.crew.CrewChestSpendingReason import CrewChestSpendingReason
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_belly_formatted
from src.service.crew_service import get_crew, add_powerup
from src.service.message_service import full_message_send, get_yes_no_keyboard


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage this screen
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

    # Not confirmed, show the confirmation screen
    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        await request_confirmation(update, context, inbound_keyboard, crew)
        return

    # Getting the text before adding power-up else it won't be accurate since the crew would be
    # modified
    ot_text = phrases.CREW_LEVEL_UP_SUCCESS.format(get_level_up_recap_text(crew))

    # Add powerup
    price = crew.get_powerup_price(CrewChestSpendingReason.LEVEL_UP)
    add_powerup(crew, user, CrewChestSpendingReason.LEVEL_UP, price)

    await full_message_send(context, ot_text, update=update, inbound_keyboard=inbound_keyboard)


async def request_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, crew: Crew
) -> None:
    """
    Request confirmation to level up
    :param update: The update object
    :param context: The context object
    :param inbound_keyboard: The inbound keyboard
    :param crew: The crew object
    :return: None
    """

    inline_keyboard: list[list[Keyboard]] = [
        get_yes_no_keyboard(
            screen=inbound_keyboard.screen,
            inbound_keyboard=inbound_keyboard,
            no_is_back_button=True,
            add_inbound_key_info=True,
        )
    ]

    await full_message_send(
        context,
        phrases.CREW_LEVEL_UP_CONFIRMATION_REQUEST.format(get_level_up_recap_text(crew)),
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )


async def validate(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, crew: Crew
) -> bool:
    """
    Validate the crew level up screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param crew: The crew
    :return: None
    """

    try:

        # Insufficient crew chest amount
        price = crew.get_powerup_price(CrewChestSpendingReason.LEVEL_UP)
        if crew.chest_amount < price:
            raise CrewValidationException(
                phrases.CREW_POWERUP_INSUFFICIENT_CREW_CHEST.format(
                    crew.get_crew_chest_formatted(),
                    get_belly_formatted(price),
                )
            )

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
