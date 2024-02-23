from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.group.screens.screen_devil_fruit_sell import validate_trade, validate_buy, buy
from src.model.DevilFruit import DevilFruit
from src.model.DevilFruitTrade import DevilFruitTrade
from src.model.User import User
from src.model.enums.Notification import DevilFruitSoldNotification
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitSource import DevilFruitSource
from src.model.pojo.Keyboard import Keyboard
from src.service.date_service import get_remaining_duration
from src.service.message_service import full_message_send, get_yes_no_keyboard
from src.service.notification_service import send_notification
from src.utils.string_utils import get_belly_formatted


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
        update,
        context,
        devil_fruit,
        trade.giver,
        inbound_keyboard=inbound_keyboard,
        show_alert=True,
    ) or not await validate_buy(update, context, user, trade):
        return

    inline_keyboard: list[list[Keyboard]] = []
    if ReservedKeyboardKeys.CONFIRM not in inbound_keyboard.info:
        # Send buy confirmation request
        ot_text = phrases.DEVIL_FRUIT_SHOP_ITEM_DETAIL_BUY_CONFIRMATION.format(
            devil_fruit.get_full_name(),
            get_belly_formatted(trade.price),
            get_remaining_duration(devil_fruit.expiration_date),
        )
        inline_keyboard.append(
            get_yes_no_keyboard(
                user,
                screen=inbound_keyboard.screen,
                primary_key=trade.id,
                inbound_keyboard=inbound_keyboard,
                no_is_back_button=True,
                add_inbound_key_info=True,
            )
        )

        await full_message_send(
            context,
            ot_text,
            update=update,
            keyboard=inline_keyboard,
            inbound_keyboard=inbound_keyboard,
        )
        return

    # Buy
    ot_text = await buy(update, context, user, trade, devil_fruit, DevilFruitSource.SHOP)
    if not ot_text:  # Error during buying, message already sent
        return

    inline_keyboard.append([
        Keyboard(
            phrases.KEY_MANAGE_DEVIL_FRUIT,
            screen=Screen.PVT_DEVIL_FRUIT_DETAIL,
            info={ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: devil_fruit.id},
        )
    ])

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=inline_keyboard,
        inbound_keyboard=inbound_keyboard,
        back_screen_index=1,
    )

    # Send notification to previous owner
    await send_notification(context, trade.giver, DevilFruitSoldNotification(trade))
