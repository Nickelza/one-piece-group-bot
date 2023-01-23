from strenum import StrEnum
from telegram import Update
from telegram.ext import ContextTypes

import constants as c
from resources import phrases
from src.model.DevilFruit import DevilFruit
from src.model.User import User
from src.model.enums.ListPage import ListPage
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.pojo.Keyboard import Keyboard
from src.service.cron_service import get_remaining_time
from src.service.devil_fruit_service import get_devil_fruit_abilities_text
from src.service.english_phrase_service import determine_article
from src.service.list_service import get_items_text_keyboard
from src.service.message_service import full_message_send, escape_valid_markdown_chars


class DevilFruitReservedKeys(StrEnum):
    """
    The reserved keys for this screen
    """
    ITEM_ID = 'a'


class DevilFruitListPage(ListPage):
    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.object: DevilFruit = DevilFruit()

    def set_object(self, object_id: int) -> None:
        self.object = DevilFruit.get(DevilFruit.id == object_id)

    def get_items(self, page) -> list[DevilFruit]:
        """Get Devil Fruits that are owned by user"""

        return (self.object
                .select()
                .where(DevilFruit.owner == self.user)
                .order_by(DevilFruit.status.desc(), DevilFruit.name.asc(), DevilFruit.model.asc())
                .paginate(page, c.STANDARD_LIST_SIZE))

    def get_total_items_count(self) -> int:
        return (self.object
                .select()
                .where(DevilFruit.owner == self.user)
                .order_by(DevilFruit.status.desc(), DevilFruit.name.asc(), DevilFruit.model.asc())
                .count())

    def get_item_text(self) -> str:
        return phrases.DEVIL_FRUIT_ITEM_TEXT.format(escape_valid_markdown_chars(self.object.get_full_name()))

    def get_item_detail_text(self) -> str:
        expiring_date_text = phrases.DEVIL_FRUIT_ITEM_DETAIL_TEXT_EXPIRING_DATE.format(
            get_remaining_time(self.object.expiration_date)) if self.object.expiration_date else ''

        abilities_text = get_devil_fruit_abilities_text(self.object) if self.object.should_show_abilities else ''
        return phrases.DEVIL_FRUIT_ITEM_DETAIL_TEXT.format(
            self.object.get_full_name(), abilities_text, expiring_date_text)


async def manage(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User) -> None:
    """
    Manage the devil_fruit list screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :return: None
    """

    devil_fruit_list_page: DevilFruitListPage = DevilFruitListPage()
    devil_fruit_list_page.user = user

    items_count = devil_fruit_list_page.get_total_items_count()

    # If no Devil Fruits, show error message
    if items_count == 0:
        await full_message_send(context, phrases.DEVIL_FRUIT_LIST_NO_ITEMS, update=update,
                                inbound_keyboard=inbound_keyboard)
        return

    # If only 1 devil fruit, go directly to the devil fruit detail screen
    if items_count == 1:
        await skip_screen(update, context, inbound_keyboard, user, devil_fruit_list_page)
        return

    items_text, items_keyboard = get_items_text_keyboard(inbound_keyboard, devil_fruit_list_page,
                                                         DevilFruitReservedKeys.ITEM_ID, Screen.PVT_DEVIL_FRUIT_DETAIL)

    ot_text = phrases.LIST_OVERVIEW.format(determine_article(phrases.DEVIL_FRUIT_ITEM_TEXT_FILL_IN),
                                           phrases.DEVIL_FRUIT_ITEM_TEXT_FILL_IN, items_text)

    await full_message_send(context, ot_text, update=update, keyboard=items_keyboard,
                            inbound_keyboard=inbound_keyboard,
                            excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE])


async def skip_screen(update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User,
                      devil_fruit_list_page: DevilFruitListPage) -> None:
    """
    Skip the Devil Fruit list screen and go to devil fruit detail screen
    :param update: The update
    :param context: The context
    :param inbound_keyboard: The inbound keyboard
    :param user: The user
    :param devil_fruit_list_page: The devil fruit list page
    :return: None
    """
    from src.chat.private.screens.screen_devil_fruit_detail import manage as manage_screen_devil_fruit_detail

    devil_fruit: DevilFruit = devil_fruit_list_page.get_items(1)[0]
    inbound_keyboard.info[DevilFruitReservedKeys.ITEM_ID] = devil_fruit.id
    inbound_keyboard.screen = Screen.PVT_DEVIL_FRUIT_DETAIL

    await manage_screen_devil_fruit_detail(update, context, inbound_keyboard, user)
