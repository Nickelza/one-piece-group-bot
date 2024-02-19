from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.group.screens.screen_devil_fruit_sell import validate_trade
from src.model.DevilFruit import DevilFruit
from src.model.DevilFruitTrade import DevilFruitTrade
from src.model.User import User
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.pojo.Keyboard import Keyboard
from src.service.message_service import full_message_send, get_yes_no_keyboard


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage this screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    trade: DevilFruitTrade = DevilFruitTrade.get_by_id(
        inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY)
    )
    devil_fruit: DevilFruit = trade.devil_fruit

    if not await validate_trade(
        update, context, devil_fruit, user, inbound_keyboard=inbound_keyboard, show_alert=True
    ):
        return

    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        # Send remove confirmation request
        ot_text = phrases.DEVIL_FRUIT_SHOP_ITEM_DETAIL_REMOVE_CONFIRMATION
        inline_keyboard: list[list[Keyboard]] = [
            get_yes_no_keyboard(
                user,
                screen=inbound_keyboard.screen,
                primary_key=trade.id,
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
        return

    # Remove trade
    DevilFruitTrade.delete_pending_trades(devil_fruit)

    # Send success message
    ot_text = phrases.DEVIL_FRUIT_SHOP_ITEM_DETAIL_REMOVE_SUCCESS
    await full_message_send(
        context, ot_text, update=update, inbound_keyboard=inbound_keyboard, back_screen_index=1
    )
