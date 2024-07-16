from enum import IntEnum

from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.chat.common.screens.screen_devil_fruit_sell import validate_trade
from src.model.DevilFruit import DevilFruit
from src.model.DevilFruitTrade import DevilFruitTrade
from src.model.User import User
from src.model.enums.ContextDataKey import ContextDataKey
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitSource import DevilFruitSource
from src.model.pojo.Keyboard import Keyboard
from src.service.bounty_service import get_amount_from_string, validate_amount
from src.service.message_service import (
    full_message_send,
    get_yes_no_keyboard,
    get_create_or_edit_status,
)
from src.utils.string_utils import get_belly_formatted


class Step(IntEnum):
    REQUEST_AMOUNT = 0
    REQUEST_CONFIRMATION = 1
    END = 2


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

    should_ignore_input, should_create_item, should_validate_input = get_create_or_edit_status(
        user, inbound_keyboard
    )

    if should_ignore_input:
        return

    if inbound_keyboard is not None:
        devil_fruit: DevilFruit = DevilFruit.get(
            DevilFruit.id == inbound_keyboard.get_int(ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY)
        )
    else:
        devil_fruit: DevilFruit = DevilFruit.get(DevilFruit.id == user.private_screen_in_edit_id)

    step = Step(user.private_screen_step if user.private_screen_step else Step.REQUEST_AMOUNT)

    # Validate the sell
    if not await validate_trade(
        update,
        context,
        devil_fruit,
        user,
        inbound_keyboard=inbound_keyboard,
    ):
        return

    # Already for sale in the shop, no need for hard validation since all previous trades will be
    # deleted on new trade
    trade = DevilFruitTrade.get_pending_in_shop(devil_fruit)
    if trade is not None:
        inline_keyboard: list[list[Keyboard]] = [
            [
                Keyboard(
                    phrases.PVT_KEY_DEVIL_FRUIT_VIEW_IN_SHOP,
                    screen=Screen.PVT_DEVIL_FRUIT_SHOP,
                    info={ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY: trade.id},
                    inbound_info=inbound_keyboard.info,
                )
            ]
        ]
        ot_text = phrases.DEVIL_FRUIT_DETAIL_SELL_ALREADY_FOR_SALE
        await full_message_send(
            context,
            ot_text,
            update=update,
            keyboard=inline_keyboard,
            inbound_keyboard=inbound_keyboard,
        )
        return

    user.private_screen_in_edit_id = devil_fruit.id

    if user.private_screen_step is None:
        user.private_screen_step = Step.REQUEST_AMOUNT

    inline_keyboard = [[]]
    match step:
        case Step.REQUEST_AMOUNT:
            ot_text = phrases.DEVIL_FRUIT_DETAIL_SELL
            average_price = devil_fruit.get_average_price()
            if average_price is not None:
                ot_text += phrases.DEVIL_FRUIT_DETAIL_SELL_AVERAGE_PRICE.format(
                    get_belly_formatted(average_price)
                )

        case Step.REQUEST_CONFIRMATION:
            amount = update.message.text

            # Validate the amount
            if not await validate_amount(
                update, context, user, update.message.text, should_validate_user_has_amount=False
            ):
                return

            amount = get_amount_from_string(amount, user)
            ot_text = phrases.DEVIL_FRUIT_DETAIL_SELL_CONFIRMATION_REQUEST.format(
                devil_fruit.get_full_name(), get_belly_formatted(amount)
            )

            # Save amount to user_data
            user.set_context_data(context, ContextDataKey.AMOUNT, amount)

            # Add confirmation buttons
            # Adding no_extra_keys to go back to the request amount step
            # Adding yes_extra_keys to preserve extra step, else it will get erased
            inline_keyboard.append(
                get_yes_no_keyboard(
                    user,
                    Screen.PVT_DEVIL_FRUIT_DETAIL_SELL,
                    primary_key=devil_fruit.id,
                    no_extra_keys={ReservedKeyboardKeys.SCREEN_STEP: Step.REQUEST_AMOUNT},
                    yes_extra_keys={ReservedKeyboardKeys.SCREEN_STEP: Step.END},
                )
            )

        case Step.END:
            if inbound_keyboard is None:
                return

            # Remove previous trades
            DevilFruitTrade.delete_pending_trades_in_shop(devil_fruit)

            amount = int(user.get_context_data(context, ContextDataKey.AMOUNT))
            # Sell the fruit
            trade: DevilFruitTrade = DevilFruitTrade()
            trade.devil_fruit = devil_fruit
            trade.giver = user
            trade.source = DevilFruitSource.SHOP
            trade.price = amount
            trade.save()

            user.private_screen_in_edit_id = None
            user.private_screen_force_go_back = True

            inline_keyboard.append(
                [
                    Keyboard(
                        phrases.PVT_KEY_DEVIL_FRUIT_VIEW_IN_SHOP,
                        screen=Screen.PVT_DEVIL_FRUIT_SHOP_DETAIL,
                        info={
                            ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: devil_fruit.id,
                            ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY: trade.id,
                        },
                        previous_screen_list=[
                            Screen.PVT_DEVIL_FRUIT,
                            Screen.PVT_DEVIL_FRUIT_DETAIL,
                        ],
                    )
                ]
            )

            ot_text = phrases.DEVIL_FRUIT_DETAIL_SELL_CONFIRMATION_CONFIRMED.format(
                devil_fruit.get_full_name(),
                get_belly_formatted(amount),
            )

        case _:
            raise ValueError(f"Invalid step: {step}")

    if user.private_screen_step is not None:
        user.private_screen_step += 1

    # Send message
    previous_screens = user.get_private_screen_list()[:-1]
    previous_screen_list_keyboard_info = {ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: devil_fruit.id}
    if step > 0:
        previous_screen_list_keyboard_info[ReservedKeyboardKeys.SCREEN_STEP] = step - 1

    await full_message_send(
        context,
        str(ot_text),
        update=update,
        inbound_keyboard=inbound_keyboard,
        keyboard=inline_keyboard,
        previous_screens=previous_screens,
        previous_screen_list_keyboard_info=previous_screen_list_keyboard_info,
        user=user,
    )
