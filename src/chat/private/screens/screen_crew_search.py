from telegram import Update
from telegram.ext import ContextTypes

import resources.phrases as phrases
from src.model.Crew import Crew
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.ListPage import ListPage, EmojiLegend, ListFilter, ListFilterType
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.error.PrivateChatError import PrivateChatException
from src.model.pojo.Keyboard import Keyboard
from src.service.crew_service import get_crew_overview_text
from src.service.list_service import get_items_text_keyboard
from src.service.message_service import full_message_send


class CrewSearchListPage(ListPage):
    def __init__(self):
        """
        Constructor
        """

        super().__init__()

        self.object: Crew = Crew()  # Current crew

    def set_object(self, object_id: int) -> None:
        self.object = Crew.logical_get(object_id)
        if self.object is None:
            raise PrivateChatException(text=phrases.CREW_NOT_FOUND)

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[User]:
        return (
            self.object.select()
            .where(
                (Crew.is_active == True)
                & (Crew.allow_view_in_search == True)
                & (self.get_active_filter_list_condition())
            )
            .order_by(Crew.level.desc(), Crew.total_gained_chest_amount.desc())
            .paginate(page, limit)
        )

    def get_item_text(self) -> str:
        return self.get_emoji_legend_formatted() + phrases.CREW_SEARCH_ITEM_TEXT.format(
            self.object.get_name_escaped(), self.object.level
        )

    def get_item_detail_text(self) -> str:
        super().get_item_detail_text()

        return get_crew_overview_text(self.object, self.user)

    def get_emoji_legend_list(self) -> list[EmojiLegend]:
        """
        Get the emoji legend list

        :return: The emoji legend list
        """

        return [
            EmojiLegend(
                Emoji.LOG_POSITIVE,
                phrases.CREW_SEARCH_ITEM_LEGEND_CAN_JOIN,
                self.get_can_join_condition(),
            ),
            EmojiLegend(
                Emoji.LOG_NEGATIVE,
                phrases.CREW_SEARCH_ITEM_LEGEND_CANNOT_JOIN,
                ~(self.get_can_join_condition()),
            ),
        ]

    def get_filter_list(self) -> list[ListFilter]:
        """
        Get the filter list

        :return: The filter list
        """

        return super().get_filter_list() + [
            ListFilter(
                ListFilterType.STRING,
                phrases.CREW_SEARCH_FILTER_NAME,
                (Crew.name ** ("%" + str(self.string_filter) + "%")),
            ),
        ]

    def get_can_join_condition(self):
        """
        Whether the user can join the crew
        """

        return (
            (Crew.is_full == False)
            & (Crew.can_accept_new_members == True)
            & (Crew.allow_join_from_search == True)
            & (Crew.required_bounty <= self.user.bounty)
            & (Crew.id != self.user.crew.id)
        )


async def manage(
    update: Update, context: ContextTypes.DEFAULT_TYPE, inbound_keyboard: Keyboard, user: User
) -> None:
    """
    Manage the Crew member screen
    :param update: The update object
    :param context: The context object
    :param user: The user object
    :param inbound_keyboard: The keyboard object
    :return: None
    """
    crew_search_list_page: CrewSearchListPage = CrewSearchListPage()
    crew_search_list_page.user = user

    # Add string filter

    ot_text, items_keyboard = get_items_text_keyboard(
        inbound_keyboard,
        crew_search_list_page,
        ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY,
        Screen.PVT_CREW_SEARCH_DETAIL,
        text_fill_in=phrases.CREW_SEARCH_ITEM_TEXT_FILL_IN,
        context=context,
        user=user,
        update=update,
        allow_string_filter=True,
    )

    await full_message_send(
        context,
        ot_text,
        update=update,
        keyboard=items_keyboard,
        inbound_keyboard=inbound_keyboard,
        excluded_keys_from_back_button=[ReservedKeyboardKeys.PAGE],
        previous_screens=user.get_private_screen_list(),
    )
