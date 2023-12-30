from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_belly_formatted
from src.service.crew_service import get_crew, get_crew_abilities_text
from src.service.date_service import get_remaining_time_from_next_cron, get_elapsed_duration
from src.service.message_service import full_message_send, escape_valid_markdown_chars


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

        # No new members allowed
        no_new_members_allowed_text = ""
        if not crew.can_accept_new_members:
            no_new_members_allowed_text = phrases.CREW_OVERVIEW_NO_NEW_MEMBERS_ALLOWED.format(
                get_remaining_time_from_next_cron(Env.CRON_SEND_LEADERBOARD.get())
            )

        first_mate: User = crew.get_first_mate()
        first_mate_text = ""
        if first_mate is not None:
            first_mate_text = phrases.CREW_OVERVIEW_FIRST_MATE.format(
                first_mate.get_markdown_mention()
            )

        captain: User = crew.get_captain()
        ot_text = phrases.CREW_OVERVIEW.format(
            escape_valid_markdown_chars(crew.name),
            crew.level,
            captain.get_markdown_mention(),
            first_mate_text,
            user.get_date_formatted(crew.creation_date),
            get_elapsed_duration(crew.creation_date),
            len(crew.get_members()),
            crew.max_members,
            get_belly_formatted(crew.chest_amount),
            get_crew_abilities_text(crew=crew),
            no_new_members_allowed_text,
        )

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

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
        excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE],
    )
