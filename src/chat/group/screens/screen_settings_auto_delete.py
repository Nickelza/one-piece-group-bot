from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
import resources.phrases as phrases
from src.model.GroupChat import GroupChat
from src.model.enums.Emoji import Emoji
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.pojo.Keyboard import Keyboard
from src.service.date_service import convert_minutes_to_duration
from src.service.list_service import get_options_keyboard
from src.service.message_service import full_message_send


async def manage(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    inbound_keyboard: Keyboard,
    group_chat: GroupChat,
) -> None:
    """
    Manage the auto delete screen
    :param update: The update object
    :param context: The context object
    :param inbound_keyboard: The inbound keyboard
    :param group_chat: The group chat
    :return: None
    """

    if ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY in inbound_keyboard.info:
        duration = inbound_keyboard.get(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY)
        group_chat.auto_delete_duration = duration
        group_chat.save()

    current_value = group_chat.auto_delete_duration
    # Create numeric keyboard with all possible values
    numeric_keyboard: list[list[Keyboard]] = get_options_keyboard(
        inbound_info=inbound_keyboard.info,
        values=Env.AUTO_DELETE_DURATION_VALUES.get_list(),
        current_selected=current_value,
    )

    # Add "Never" option as first option
    numeric_keyboard.insert(
        0,
        [
            Keyboard(
                (Emoji.RADIO_BUTTON if current_value is None else "") + phrases.TEXT_NEVER,
                info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: None},
                inbound_info=inbound_keyboard.info,
            )
        ],
    )

    ot_text = phrases.AUTO_DELETE_SET.format(
        phrases.TEXT_NEVER if current_value is None else convert_minutes_to_duration(current_value)
    )
    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=numeric_keyboard,
        add_delete_button=True,
        use_close_delete=True,
        inbound_keyboard=inbound_keyboard,
        should_auto_delete=False,
    )
