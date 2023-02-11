from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.model.DevilFruit import DevilFruit
from src.model.User import User
from src.model.enums.devil_fruit.DevilFruitCategory import DevilFruitCategory
from src.model.enums.devil_fruit.DevilFruitSource import DevilFruitSource
from src.model.error.CustomException import DevilFruitValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_next_bounty_reset_time
from src.service.cron_service import get_remaining_time
from src.service.devil_fruit_service import give_devil_fruit_to_user, get_devil_fruit_abilities_text
from src.service.message_service import escape_valid_markdown_chars, full_message_send, full_media_send


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

    try:
        # Not managing in validate because give_devil_fruit_to_user() also raises a DevilFruitValidationException
        validate(user, devil_fruit)

        give_devil_fruit_to_user(devil_fruit, user, DevilFruitSource.BOT)

        user.can_collect_devil_fruit = False

        # Send to chat
        ot_text = phrases.DEVIL_FRUIT_COLLECT_SUCCESS.format(
            user.get_markdown_mention(), escape_valid_markdown_chars(devil_fruit.get_full_name()),
            DevilFruitCategory(devil_fruit.category).get_description(),
            get_devil_fruit_abilities_text(devil_fruit, always_show_abilities=False))

        await full_media_send(context, caption=ot_text, update=update, edit_only_caption_and_keyboard=True)

    except DevilFruitValidationException as e:
        await full_message_send(context, e.message, update=update, answer_callback=True, show_alert=True)


def validate(user: User, devil_fruit: DevilFruit) -> None:
    """
    Validate the collect Devil Fruit collection, raising an exception if the validation fails
    :param user: The user
    :param devil_fruit: The Devil Fruit
    :return: True if the screen is valid, False otherwise
    """

    #  Devil Fruit is not already owned by someone, in case multiple users are trying to collect it
    #  before the keyboard is updated
    if devil_fruit.owner:
        raise DevilFruitValidationException(phrases.DEVIL_FRUIT_ALREADY_COLLECTED)

    # User cannot collect Devil Fruits
    if not user.can_collect_devil_fruit:
        raise DevilFruitValidationException(
            phrases.DEVIL_FRUIT_USER_CANNOT_COLLECT.format(get_remaining_time(get_next_bounty_reset_time())))
