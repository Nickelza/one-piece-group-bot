from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.model.DevilFruit import DevilFruit
from src.model.DevilFruitTrade import DevilFruitTrade
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.ListPage import ListPage, EmojiLegend
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitCategory import DevilFruitCategory
from src.model.enums.devil_fruit.DevilFruitSource import DevilFruitSource
from src.model.enums.devil_fruit.DevilFruitTradeStatus import DevilFruitTradeStatus
from src.model.pojo.Keyboard import Keyboard
from src.service.devil_fruit_service import get_recap_text
from src.service.list_service import get_items_text_keyboard
from src.service.message_service import full_message_send, escape_valid_markdown_chars
from src.service.string_service import get_belly_formatted


class DevilFruitShopListPage(ListPage):
    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.object: DevilFruitTrade = DevilFruitTrade()
        self.devil_fruit: DevilFruit = DevilFruit()

    def set_object(self, object_id: int) -> None:
        self.object: DevilFruitTrade = DevilFruitTrade.get_by_id(object_id)
        self.devil_fruit: DevilFruit = self.object.devil_fruit

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[DevilFruitTrade]:
        """Get Devil Fruits that are owned by user"""

        return (
            self.object.select()
            .join(DevilFruit)
            .where(
                (DevilFruitTrade.source == DevilFruitSource.SHOP)
                & (DevilFruitTrade.status == DevilFruitTradeStatus.PENDING)
                & (self.get_active_filter_list_condition())
            )
            .order_by(DevilFruitTrade.date)
            .paginate(page, limit)
        )

    def get_item_text(self) -> str:
        return phrases.DEVIL_FRUIT_SHOP_ITEM_TEXT.format(
            self.get_emoji_legend_formatted()
            + escape_valid_markdown_chars(self.devil_fruit.get_full_name()),
            get_belly_formatted(self.object.price),
        )

    def get_item_detail_text(self) -> str:
        """
        Get the item detail text
        :return:
        """
        super().get_item_detail_text()

        return phrases.DEVIL_FRUIT_SHOP_ITEM_DETAIL_TEXT.format(
            get_recap_text(self.devil_fruit),
            self.object.giver.get_markdown_mention(),
            get_belly_formatted(self.object.price),
        )

    def get_emoji_legend_list(self) -> list[EmojiLegend]:
        """
        Get the emoji legend list

        :return: The emoji legend list
        """

        return [
            EmojiLegend(
                Emoji.GREEN,
                DevilFruitCategory.SMILE.get_description(),
                (DevilFruitTrade.devil_fruit.category == DevilFruitCategory.SMILE),
            ),
            EmojiLegend(
                Emoji.LOG_YELLOW,
                DevilFruitCategory.ZOAN.get_description(),
                (DevilFruitTrade.devil_fruit.category == DevilFruitCategory.ZOAN),
            ),
            EmojiLegend(
                Emoji.LOG_BLUE,
                DevilFruitCategory.ANCIENT_ZOAN.get_description(),
                (DevilFruitTrade.devil_fruit.category == DevilFruitCategory.ANCIENT_ZOAN),
            ),
            EmojiLegend(
                Emoji.LOG_PURPLE,
                DevilFruitCategory.MYTHICAL_ZOAN.get_description(),
                (DevilFruitTrade.devil_fruit.category == DevilFruitCategory.MYTHICAL_ZOAN),
            ),
        ]


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the devil_fruit list screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    from src.chat.private.screens.screen_devil_fruit_shop_detail import (
        manage as screen_devil_fruit_shop_detail_detail,
    )

    devil_fruit_shop_list_page: DevilFruitShopListPage = DevilFruitShopListPage()
    devil_fruit_shop_list_page.user = user

    # Has direct DF Shop item
    direct_item: DevilFruitTrade = devil_fruit_shop_list_page.get_direct_item()
    if direct_item is not None:
        inbound_keyboard.info[ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY] = direct_item.id
        await screen_devil_fruit_shop_detail_detail(update, context, inbound_keyboard, user)
        return

    # Using secondary key because in case we are coming from Devil Fruit Detail screen, there
    # will already be a Primary Key
    ot_text, items_keyboard = get_items_text_keyboard(
        inbound_keyboard,
        devil_fruit_shop_list_page,
        ReservedKeyboardKeys.DEFAULT_SECONDARY_KEY,
        Screen.PVT_DEVIL_FRUIT_SHOP_DETAIL,
        text_fill_in=phrases.DEVIL_FRUIT_SHOP_ITEM_TEXT_FILL_IN,
        empty_list_text=phrases.DEVIL_FRUIT_SHOP_LIST_NO_ITEMS,
        context=context,
        user=user,
    )

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=items_keyboard,
        inbound_keyboard=inbound_keyboard,
        excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE],
    )
