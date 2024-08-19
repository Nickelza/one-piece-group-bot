from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.private.screens.screen_devil_fruit_shop import DevilFruitShopListPage
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the devil_fruit detail screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    devil_fruit_shop_list_page = DevilFruitShopListPage()

    devil_fruit_shop_list_page.user = user
    devil_fruit_shop_list_page.set_object(
        inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY)
    )

    inline_keyboard: list[list[Keyboard]] = []

    # If not owner, show buy button
    if user != devil_fruit_shop_list_page.object.giver:
        inline_keyboard.append(
            [
                Keyboard(
                    phrases.KEY_BUY,
                    screen=Screen.PVT_DEVIL_FRUIT_SHOP_DETAIL_BUY,
                    inbound_info=inbound_keyboard.info,
                )
            ]
        )
    else:  # Remove button
        inline_keyboard.append(
            [
                Keyboard(
                    phrases.KEY_REMOVE,
                    screen=Screen.PVT_DEVIL_FRUIT_SHOP_DETAIL_REMOVE,
                    inbound_info=inbound_keyboard.info,
                )
            ]
        )

    await full_message_send(
        context,
        devil_fruit_shop_list_page.get_item_detail_text(),
        update=update,
        keyboard=devil_fruit_shop_list_page.get_previous_and_next_object_keyboard(inbound_keyboard)
        + inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )
