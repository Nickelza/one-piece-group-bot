from abc import ABC, abstractmethod
from enum import StrEnum

from resources import phrases
from src.model.BaseModel import BaseModel
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys


class EmojiLegend:
    """Class for emoji legends."""

    def __init__(self, emoji: Emoji, description: str, condition: any):
        """
        Constructor

        :param emoji: The emoji
        :param description: The description
        :param condition: The condition
        """

        self.emoji: Emoji = emoji
        self.description: str = description
        self.condition: any = condition


class ListFilterType(StrEnum):
    """Enum for list filter types."""

    BOOLEAN = "b"
    STRING = "s"


class ListFilter:
    """Class for list filters."""

    def __init__(self, filter_type: ListFilterType, description: str, condition: any):
        """
        Constructor

        :param filter_type: The filter type
        :param description: The description
        :param condition: The condition
        """

        self.filter_type: ListFilterType = filter_type
        self.description: str = description
        self.condition: any = condition
        self.value: any = None
        self.key: any = None


class ListPage(ABC):
    """Abstract class for list pages."""

    def __init__(self):
        """
        Constructor
        """

        self.user: User = User()
        self.object: BaseModel = BaseModel()
        self.emoji_legend_list: list[EmojiLegend] = []
        self.filter_list_active: list[ListFilter] = []
        self.string_filter: str | None = None

    @abstractmethod
    def set_object(self, object_id: int) -> None:
        """
        Set the object of the list

        :param object_id: The object id
        :return: None
        """
        pass

    @abstractmethod
    def get_items(self, page: int) -> list[BaseModel]:
        """
        Get a list item for the log

        :param page: The page
        :return: The list item
        """
        pass

    @abstractmethod
    def get_total_items_count(self) -> int:
        """
        Get the total number of items for the list

        :return: The total number of items
        """
        pass

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
        pass

    def get_emoji_legend(self) -> EmojiLegend:
        """
        Get the emoji legend

        :return: The emoji legend
        """

        for emoji_legend in self.emoji_legend_list:
            if emoji_legend.condition:
                return emoji_legend

    def get_emoji_legend_formatted(self) -> str:
        """
        Get the emoji legend formatted

        :return: The emoji legend formatted
        """

        return self.get_emoji_legend().emoji + " "

    def get_emoji_legend_list_text(self) -> str:
        """
        Get the legend text

        :return: The legend text
        """

        legend_text: str = ""

        for emoji_legend in self.emoji_legend_list:
            legend_text += phrases.LIST_EMOJI_LEGEND_ITEM.format(
                emoji_legend.emoji, emoji_legend.description
            )

        return phrases.LIST_EMOJI_LEGEND.format(legend_text)

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

        return []
