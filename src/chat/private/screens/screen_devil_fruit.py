from enum import StrEnum

from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.model.DevilFruit import DevilFruit
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.ListPage import ListPage, EmojiLegend
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.enums.devil_fruit.DevilFruitStatus import DevilFruitStatus
from src.model.error.CustomException import UnauthorizedToViewItemException
from src.model.pojo.Keyboard import Keyboard
from src.service.devil_fruit_service import get_recap_text
from src.service.list_service import get_items_text_keyboard
from src.service.message_service import full_message_send, escape_valid_markdown_chars


class DevilFruitReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """

    ITEM_ID = "a"


class DevilFruitListPage(ListPage):
    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.object: DevilFruit = DevilFruit()

    def set_object(self, object_id: int) -> None:
        self.object = DevilFruit.get(DevilFruit.id == object_id)

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[DevilFruit]:
        """Get Devil Fruits that are owned by user"""

        return (
            self.object.select()
            .where((DevilFruit.owner == self.user) & (self.get_active_filter_list_condition()))
            .order_by(DevilFruit.status.desc(), DevilFruit.name.asc(), DevilFruit.model.asc())
            .paginate(page, limit)
        )

    def get_item_text(self) -> str:
        return phrases.DEVIL_FRUIT_ITEM_TEXT.format(
            self.get_emoji_legend_formatted()
            + escape_valid_markdown_chars(self.object.get_full_name())
        )

    def get_item_detail_text(self) -> str:
        """
        Get the item detail text
        :return:
        """
        try:
            super().get_item_detail_text()
        except UnauthorizedToViewItemException:
            raise UnauthorizedToViewItemException

        return get_recap_text(self.object, add_sell_command=True)

    def get_emoji_legend_list(self) -> list[EmojiLegend]:
        """
        Get the emoji legend list

        :return: The emoji legend list
        """

        return [
            EmojiLegend(
                Emoji.LOG_NEGATIVE,
                DevilFruitStatus.EATEN.get_description(),
                (DevilFruit.status == DevilFruitStatus.EATEN),
            ),
            EmojiLegend(
                Emoji.LOG_POSITIVE,
                DevilFruitStatus.COLLECTED.get_description(),
                (DevilFruit.status == DevilFruitStatus.COLLECTED),
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
    from src.chat.private.screens.screen_devil_fruit_detail import (
        manage as manage_screen_devil_fruit_detail,
    )

    devil_fruit_list_page: DevilFruitListPage = DevilFruitListPage()
    devil_fruit_list_page.user = user

    # Has direct DF
    direct_item: DevilFruit = devil_fruit_list_page.get_direct_item()
    if direct_item is not None:
        inbound_keyboard.info[ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY] = direct_item.id
        await manage_screen_devil_fruit_detail(update, context, inbound_keyboard, user)
        return

    ot_text, items_keyboard = get_items_text_keyboard(
        inbound_keyboard,
        devil_fruit_list_page,
        DevilFruitReservedKeys.ITEM_ID,
        Screen.PVT_DEVIL_FRUIT_DETAIL,
        text_fill_in=phrases.DEVIL_FRUIT_ITEM_TEXT_FILL_IN,
        empty_list_text=phrases.DEVIL_FRUIT_LIST_NO_ITEMS,
        context=context,
        user=user,
    )

    # Shop button
    items_keyboard.append([
        Keyboard(
            phrases.KEY_SHOP,
            screen=Screen.PVT_DEVIL_FRUIT_SHOP,
            inbound_info=inbound_keyboard.info,
        )
    ])

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=items_keyboard,
        inbound_keyboard=inbound_keyboard,
        excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE],
    )
