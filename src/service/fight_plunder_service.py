from telegram import Update
from telegram.ext import ContextTypes

import resources.Environment as Env
from resources import phrases
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitAbilityType import DevilFruitAbilityType
from src.model.pojo.Keyboard import Keyboard
from src.service.devil_fruit_service import get_ability_value
from src.service.message_service import get_yes_no_keyboard, full_media_send
from src.utils.string_utils import get_belly_formatted


def get_scout_price(user: User, is_group: bool) -> int:
    """
    Get the scout price
    :param user: The user
    :param is_group: If the scout is for a group
    :return: The scout price
    """

    price: int = Env.FIGHT_PLUNDER_SCOUT_BASE_PRICE.get_int()

    # Multiply the price by the user's location level
    price *= user.location_level

    # Add group multiplier
    if is_group:
        price *= Env.FIGHT_PLUNDER_SCOUT_PRICE_MULTIPLIER_GROUP.get_float()

    # Adjust by Devil Fruit ability
    price = int(get_ability_value(user, DevilFruitAbilityType.FIGHT_PLUNDER_SCOUT_PRICE, price))

    return price


async def send_scout_request(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user: User,
    screen: Screen,
    group_chat: GroupChat = None,
) -> None:
    """
    Send request to confirm fight
    :param update: The update
    :param context: The context
    :param user: The user
    :param screen: The screen
    :param group_chat: The group chat
    :return: None
    """

    opponent: User = get_opponent(update)
    caption = phrases.FIGHT_SCOUT_USER.format(
        opponent.get_markdown_mention(),
        get_belly_formatted(get_scout_price(user, (group_chat is not None))),
    )

    # Keyboard
    inline_keyboard: list[list[Keyboard]] = [
        get_yes_no_keyboard(
            user,
            screen=screen,
            yes_text=phrases.KEYBOARD_OPTION_SCOUT,
            no_text=phrases.KEYBOARD_OPTION_RETREAT,
            no_is_delete_button=True,
            yes_extra_keys={ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY: opponent.id},
        )
    ]

    await full_media_send(
        context,
        saved_media_name=SavedMediaName.FIGHT_PLUNDER_SCOUT,
        update=update,
        caption=caption,
        keyboard=inline_keyboard,
        add_delete_button=True,
    )


def get_opponent(update: Update = None, keyboard: Keyboard = None) -> User | None:
    """
    Get opponent from update or keyboard
    :param update: The update object. If None, the opponent is taken from the keyboard
    :param keyboard: The keyboard object. If None, the opponent is taken from the update
    :return: The opponent object
    """

    if update.callback_query is None:
        return User.get_or_none(User.tg_user_id == update.message.reply_to_message.from_user.id)

    return User.get_by_id(int(keyboard.get_int(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY)))
