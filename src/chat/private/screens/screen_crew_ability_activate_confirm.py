from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.chat.private.screens.screen_crew_ability_activate import validate
from src.model.Crew import Crew
from src.model.CrewAbility import CrewAbility
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.crew.CrewAbilityAcquiredMethod import CrewAbilityAcquiredMethod
from src.model.enums.crew.CrewChestSpendingReason import CrewChestSpendingReason
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.error.CustomException import CrewValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew, add_crew_ability, add_powerup
from src.service.math_service import get_random_int
from src.service.message_service import full_message_send, get_yes_no_keyboard
from src.service.string_service import get_belly_formatted


class CrewAbilityActivateReservedKeys(StrEnum):
    """
    The reserved keys for the Crew ability activate screen
    """

    ABILITY_TYPE = "a"


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
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

    # Activate the ability
    ability_type = inbound_keyboard.get(CrewAbilityActivateReservedKeys.ABILITY_TYPE)
    if ability_type is not None:
        ability_type = DevilFruitAbilityType(
            inbound_keyboard.get(CrewAbilityActivateReservedKeys.ABILITY_TYPE)
        )
        ability_value = Env.CREW_ABILITY_DEFAULT_VALUE_PERCENTAGE.get_int()
        acquired_method = CrewAbilityAcquiredMethod.CHOSEN
    else:
        ability_type = CrewAbility.get_random_ability()
        ability_value = get_random_int(
            Env.CREW_ABILITY_RANDOM_MIN_VALUE_PERCENTAGE.get_int(),
            Env.CREW_ABILITY_RANDOM_MAX_VALUE_PERCENTAGE.get_int(),
        )
        acquired_method = CrewAbilityAcquiredMethod.RANDOM

    await add_crew_ability(context, crew, ability_type, ability_value, acquired_method, user)

    # Add powerup
    ability_price = crew.get_powerup_price(CrewChestSpendingReason.ABILITY)
    add_powerup(crew, user, CrewChestSpendingReason.ABILITY, ability_price)

    ot_text = phrases.CREW_ABILITY_ACTIVATE_SUCCESS.format(
        ability_type.get_description(),
        str(ability_value) + "%",
        Env.CREW_ABILITY_DURATION_DAYS.get_int(),
        get_belly_formatted(ability_price),
    )

    await full_message_send(
        context, ot_text, update=update, inbound_keyboard=inbound_keyboard, back_screen_index=1
    )


async def request_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, crew: Crew
) -> None:
    """
    Request confirmation to activate the ability
    :param update: The update object
    :param context: The context object
    :param inbound_keyboard: The inbound keyboard
    :param crew: The crew object
    :return: None
    """

    ability_type = inbound_keyboard.get(CrewAbilityActivateReservedKeys.ABILITY_TYPE)
    if ability_type is not None:
        ability_type = DevilFruitAbilityType(
            inbound_keyboard.get(CrewAbilityActivateReservedKeys.ABILITY_TYPE)
        )
        ability_name = ability_type.get_description()
        ability_value_text = (
            ability_type.get_sign().value + Env.CREW_ABILITY_DEFAULT_VALUE_PERCENTAGE.get() + "%"
        )
    else:
        ability_name = ability_value_text = phrases.TEXT_RANDOM

    ot_text = phrases.CREW_ABILITY_ACTIVATE_CHOOSE_CONFIRMATION_REQUEST.format(
        ability_name,
        ability_value_text,
        Env.CREW_ABILITY_DURATION_DAYS.get_int(),
        crew.get_powerup_price_formatted(CrewChestSpendingReason.ABILITY),
    )

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
        ot_text,
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )
