from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.model.DevilFruit import DevilFruit
from src.model.User import User
from src.model.enums.devil_fruit.DevilFruitSource import DevilFruitSource
from src.model.pojo.Keyboard import Keyboard
from src.service.devil_fruit_service import give_devil_fruit_to_user, get_devil_fruit_abilities_text
from src.service.message_service import escape_valid_markdown_chars, full_message_send


class DevilFruitCollectReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    DEVIL_FRUIT_ID = 'a'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, user: User, inbound_keyboard: Keyboard) -> None:
    """
    Manage the collect Devil Fruit screen
    :param update: The update object
    :param context: The context object
    :param user: The user
    :param inbound_keyboard: The inbound keyboard
    :return: None
    """

    # Get the Devil Fruit
    devil_fruit: DevilFruit = DevilFruit.get_by_id(inbound_keyboard.get(DevilFruitCollectReservedKeys.DEVIL_FRUIT_ID))

    # Check that the Devil Fruit is not already owned by someone, in case multiple users are trying to collect it
    # before the keyboard is removed
    if devil_fruit.owner:
        await full_message_send(
            context, phrases.DEVIL_FRUIT_ALREADY_COLLECTED, update=update, answer_callback=True, show_alert=True)
        return

    give_devil_fruit_to_user(devil_fruit, user, DevilFruitSource.BOT)

    # Send to chat
    ot_text = phrases.DEVIL_FRUIT_COLLECT_SUCCESS.format(
        user.get_markdown_mention(), escape_valid_markdown_chars(devil_fruit.get_full_name()),
        get_devil_fruit_abilities_text(devil_fruit, always_show_abilities=False))

    await full_message_send(context, ot_text, update=update)
