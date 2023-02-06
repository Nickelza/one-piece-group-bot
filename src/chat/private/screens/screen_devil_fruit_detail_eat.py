import datetime
from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.DevilFruit import DevilFruit
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitStatus import DevilFruitStatus
from src.model.error.CustomException import DevilFruitValidationException
from src.model.pojo.Keyboard import Keyboard
from src.service.devil_fruit_service import get_devil_fruit_abilities_text
from src.service.message_service import full_message_send, get_yes_no_keyboard


class DevilFruitEatReservedKeys(StrEnum):
    """
    The reserved keys for the Devil Fruit Eat screen
    """
    DEVIL_FRUIT_ID = 'a'


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the Devil Fruit eat screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """

    # Get devil fruit
    devil_fruit: DevilFruit = DevilFruit.get_by_id(inbound_keyboard.info[DevilFruitEatReservedKeys.DEVIL_FRUIT_ID])

    try:
        validate(devil_fruit, user)
    except DevilFruitValidationException as ve:
        await full_message_send(context, ve.message, update=update, inbound_keyboard=inbound_keyboard)
        return

    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        # Send eat confirmation request
        abilities_text = (phrases.DEVIL_FRUIT_EAT_CONFIRMATION_REQUEST_ABILITIES.format(
            get_devil_fruit_abilities_text(devil_fruit, add_header=False)) if devil_fruit.should_show_abilities else '')

        ot_text = phrases.DEVIL_FRUIT_EAT_CONFIRMATION_REQUEST.format(devil_fruit.get_full_name(), abilities_text)
        inline_keyboard: list[list[Keyboard]] = [
            get_yes_no_keyboard(user, screen=Screen.PVT_DEVIL_FRUIT_DETAIL_EAT, primary_key=devil_fruit.id,
                                inbound_keyboard=inbound_keyboard, no_is_back_button=True)]

        await full_message_send(context, ot_text, update=update, keyboard=inline_keyboard,
                                inbound_keyboard=inbound_keyboard)
        return

    # Eat Devil Fruit
    devil_fruit.status = DevilFruitStatus.EATEN
    devil_fruit.eaten_date = datetime.datetime.now()
    devil_fruit.expiration_date = None
    devil_fruit.should_show_abilities = True
    devil_fruit.save()

    # Send success message
    ot_text = phrases.DEVIL_FRUIT_EAT_CONFIRMATION_CONFIRMED.format(
        devil_fruit.get_full_name(), get_devil_fruit_abilities_text(devil_fruit, add_header=False))
    await full_message_send(context, ot_text, update=update, inbound_keyboard=inbound_keyboard)


def validate(devil_fruit: DevilFruit, user: User) -> None:
    """
    Validate the devil fruit eat, raise an exception if the devil fruit cannot be eaten
    :param devil_fruit: The devil fruit
    :param user: The user
    :return: None
    """

    # User is not owner
    if devil_fruit.owner != user:
        raise DevilFruitValidationException(phrases.DEVIL_FRUIT_NOT_OWNER)

    # User already ate a devil fruit
    if DevilFruit.get_by_owner_if_eaten(user) is not None:
        raise DevilFruitValidationException(phrases.DEVIL_FRUIT_EAT_USER_ALREADY_ATE)
