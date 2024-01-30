from abc import ABC, abstractmethod
from enum import StrEnum

import constants as c
from resources import phrases
from src.model.BaseModel import BaseModel
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.GameStatus import GameStatus
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.error.CustomException import UnauthorizedToViewItemException


class EmojiLegend:
    """Class for emoji legends."""

    def __init__(self, emoji: Emoji, description: str, condition: any, status: any = None):
        """
        Constructor

        :param emoji: The emoji
        :param description: The description
        :param condition: The condition
        :param status: The status
        """

        self.emoji: Emoji = emoji
        self.description: str = description
        self.condition: any = condition
        self.status: any = status

    def get_formatted(self) -> str:
        return self.emoji + " "

    def get_game_status(self) -> GameStatus:
        """
        Get the game status

        :return: The game status
        """

        return GameStatus(self.status)


class ListFilterType(StrEnum):
    """Enum for list filter types."""

    STRING = "s"
    LEGEND = "l"


class ListFilter:
    """Class for list filters."""

    def __init__(
        self,
        filter_type: ListFilterType,
        description: str,
        condition: any,
        legend: EmojiLegend = None,
    ):
        """
        Constructor

        :param filter_type: The filter type
        :param description: The description
        :param condition: The condition
        """

        self.filter_type: ListFilterType = filter_type
        self.description: str = description
        self.condition: any = condition
        self.legend: EmojiLegend = legend
        self.value: any = None
        self.key: any = None


class ListPage(ABC):
    """Abstract class for list pages."""

    DEFAULT_LIMIT = c.STANDARD_LIST_SIZE
    MAX_LIMIT = c.MAX_LIMIT

    def __init__(self):
        """
        Constructor
        """

        self.user: User = User()
        self.object: BaseModel = BaseModel()
        self.emoji_legend_list: list[EmojiLegend] = []
        self.filter_list_active: list[ListFilter] = []
        self.string_filter: str | None = None
        self.default_limit = c.STANDARD_LIST_SIZE
        self.legend: EmojiLegend | None = None
        self.show_legend_list: bool = True  # If to show legend list if available

        # Adding list of all items grouped by legend emoji, as to find out the emoji for each item
        self.legend_filter_results: dict[EmojiLegend, list[BaseModel]] = {}

    def init_legend_filter_results(self):
        """
        Init the legend filter results
        """

        for filter_item in [
            f for f in self.get_filter_list() if f.filter_type is ListFilterType.LEGEND
        ]:
            self.filter_list_active = [filter_item]
            self.legend_filter_results[filter_item.legend] = self.get_all_items()
        self.filter_list_active = []

    @abstractmethod
    def set_object(self, object_id: int) -> None:
        """
        Set the object of the list

        :param object_id: The object id
        :return: None
        """

        pass

    @abstractmethod
    def get_items(self, page: int, limit: int = DEFAULT_LIMIT) -> list[BaseModel]:
        """
        Get a list item for the log

        :param page: The page
        :param limit: The limit
        :return: The list item
        """
        pass

    def get_all_items(self):
        """
        Get all items for the log

        :return: The list item
        """

        return self.get_items(1, ListPage.MAX_LIMIT)

    def get_total_items_count(self) -> int:
        """
        Get the total items count

        :return: The total items count
        """

        return len(self.get_all_items())

    @abstractmethod
    def get_item_text(self) -> str:
        """
        Get the text for an item in the list

        :return: The text
        """
        pass

    @abstractmethod
    def get_item_detail_text(self) -> str:
        """
        Get the details for the list item

        :return: The details
        """
        if self.object not in self.get_all_items():
            raise UnauthorizedToViewItemException()

        return ""

    def get_emoji_legend(self) -> EmojiLegend:
        """
        Get the emoji legend

        :return: The emoji legend
        """

        for legend, results in self.legend_filter_results.items():
            if self.object in results:
                return legend

    def get_emoji_legend_formatted(self) -> str:
        """
        Get the emoji legend formatted

        :return: The emoji legend formatted
        """

        return self.get_emoji_legend().get_formatted()

    def get_emoji_legend_list_text(self) -> str:
        """
        Get the legend text

        :return: The legend text
        """

        legend_text: str = ""

        for emoji_legend in self.emoji_legend_list:
            legend_text += phrases.LIST_EMOJI_LEGEND_ITEM.format(
                emoji_legend.emoji,
                emoji_legend.description,
                len(self.legend_filter_results[emoji_legend]),
            )

        return phrases.LIST_EMOJI_LEGEND.format(legend_text)

    def get_emoji_legend_list(self) -> list[EmojiLegend]:
        """
        Get the emoji legend list

        :return: The emoji legend list
        """

        return []

    @staticmethod
    def get_filter_key(index: int) -> str:
        """
        Get the filter key
        """

        return ReservedKeyboardKeys.FILTER + str(index)

    def get_string_filter_key(self) -> str:
        """
        Get the string filter key
        """

        for index, filter_item in enumerate(self.get_filter_list()):
            if filter_item.filter_type is ListFilterType.STRING:
                return self.get_filter_key(index)

    def get_active_filter_list_condition(self) -> any:
        """
        Get the active filter list condition
        """
        condition = True
        for list_filter in self.filter_list_active:
            condition &= list_filter.condition

        return condition

    def get_filter_list(self) -> list[ListFilter]:
        """
        Get the filter list

        :return: The filter list
        """

        # In case of Emoji legend, add list filter for it
        filter_list = []

        if len(self.emoji_legend_list) > 0:
            for legend in self.emoji_legend_list:
                filter_list.append(
                    ListFilter(
                        ListFilterType.LEGEND,
                        legend.description,
                        legend.condition,
                        legend=legend,
                    )
                )

        return filter_list
