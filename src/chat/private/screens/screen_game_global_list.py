from telegram import Update
from telegram.ext import ContextTypes

from resources import phrases
from src.model.Game import Game
from src.model.User import User
from src.model.enums.ListPage import ListPage
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.pojo.Keyboard import Keyboard
from src.service.game_service import get_global_game_item_text_deeplink
from src.service.list_service import get_items_text_keyboard
from src.service.message_service import full_message_send


class GameGlobalListPage(ListPage):
    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.object: Game = Game()

    def set_object(self, object_id: int) -> None:
        self.object = Game.get(Game.id == object_id)

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[Game]:
        return Game.get_global_games()

    def get_item_text(self) -> str:
        return get_global_game_item_text_deeplink(self.object, self.user)

    def get_item_detail_text(self) -> str:
        pass


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

    game_global_list_page: GameGlobalListPage = GameGlobalListPage()
    game_global_list_page.user = user

    ot_text, items_keyboard = get_items_text_keyboard(
        inbound_keyboard,
        game_global_list_page,
        text_fill_in=phrases.GAME_GLOBAL_CHALLENGE_ITEM_TEXT_FILL_IN,
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
