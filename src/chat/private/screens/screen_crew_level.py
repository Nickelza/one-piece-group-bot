from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.Screen import Screen
from src.model.enums.crew.CrewChestSpendingReason import CrewChestSpendingReason
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew
from src.service.message_service import full_message_send
from src.utils.string_utils import get_belly_formatted


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

    crew = get_crew(user=user)
    inline_keyboard: list[list[Keyboard]] = []

    # Level up button (only if the user is the captain or first mate)
    if user.is_crew_captain_or_first_mate():
        inline_keyboard.append(
            [Keyboard(phrases.PVT_KEY_CREW_LEVEL_UP, screen=Screen.PVT_CREW_LEVEL_UP)]
        )

    ot_text = phrases.CREW_LEVEL.format(
        crew.level,
        crew.max_members,
        crew.max_abilities,
        crew.level + 1,
        get_level_up_recap_text(crew),
        get_belly_formatted(crew.chest_amount),
    )

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )


def get_level_up_recap_text(crew: Crew) -> str:
    """
    Get the level up recap text
    :param crew: The crew
    :return: The level up recap text
    """

    upgrade_type = crew.get_next_level_upgrade_type()
    upgrade_type_current_count = crew.get_upgrade_type_count(upgrade_type)
    return phrases.CREW_LEVEL_UP_RECAP.format(
        upgrade_type.get_description(),
        upgrade_type_current_count,
        upgrade_type_current_count + 1,
        crew.get_powerup_price_formatted(CrewChestSpendingReason.LEVEL_UP),
    )
