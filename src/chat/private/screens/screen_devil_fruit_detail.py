from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.private.screens.screen_devil_fruit import DevilFruitListPage
from src.model.DevilFruit import DevilFruit
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitStatus import DevilFruitStatus
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

    devil_fruit_list_page = DevilFruitListPage()

    devil_fruit_list_page.user = user
    devil_fruit_list_page.set_object(
        inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY)
    )

    devil_fruit: DevilFruit = devil_fruit_list_page.object
    inline_keyboard: list[list[Keyboard]] = []

    devil_fruit_status: DevilFruitStatus = DevilFruitStatus(devil_fruit.status)
    button_info = {ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: devil_fruit.id}

    # Show eat and trade buttons if the user have not eaten the Devil Fruit
    if devil_fruit_status is DevilFruitStatus.COLLECTED:
        # Eat button
        inline_keyboard.append([
            Keyboard(
                phrases.PVT_KEY_DEVIL_FRUIT_DETAIL_EAT,
                screen=Screen.PVT_DEVIL_FRUIT_DETAIL_EAT,
                info=button_info,
            )
        ])

        # Sell button
        inline_keyboard.append([
            Keyboard(
                phrases.PVT_KEY_DEVIL_FRUIT_DETAIL_SELL,
                screen=Screen.PVT_DEVIL_FRUIT_DETAIL_SELL,
                info=button_info,
            )
        ])

    # Discard button
    inline_keyboard.append([
        Keyboard(
            phrases.PVT_KEY_DEVIL_FRUIT_DETAIL_DISCARD,
            screen=Screen.PVT_DEVIL_FRUIT_DETAIL_DISCARD,
            info=button_info,
        )
    ])

    await full_message_send(
        context,
        devil_fruit_list_page.get_item_detail_text(),
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
    )
