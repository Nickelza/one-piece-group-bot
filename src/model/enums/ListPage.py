from abc import ABC, abstractmethod

from src.model.BaseModel import BaseModel
from src.model.User import User


class ListPage(ABC):
    """Abstract class for list pages."""

    def __init__(self):
        """
        Constructor
        """

        self.user: User = User()
        self.object: BaseModel = BaseModel()

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
