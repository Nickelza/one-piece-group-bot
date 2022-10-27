from abc import ABC, abstractmethod
from enum import IntEnum

import constants as c
import resources.phrases as phrases
from src.model.BaseModel import BaseModel
from src.model.DocQGame import DocQGame
from src.model.Fight import Fight
from src.model.Game import Game
from src.model.User import User
from src.model.enums.Emoji import Emoji
from src.model.enums.GameStatus import GameStatus, GAME_STATUS_DESCRIPTIONS
from src.model.game.GameType import GameType
from src.service.bounty_service import get_belly_formatted


class LogType(IntEnum):
    """Enum for different types of logs"""

    FIGHT = 1
    DOC_Q_GAME = 2
    GAME = 3


LOG_TYPE_BUTTON_TEXTS = {
    LogType.FIGHT: phrases.FIGHT_LOG_KEY,
    LogType.DOC_Q_GAME: phrases.DOC_Q_GAME_LOG_KEY,
    LogType.GAME: phrases.GAME_LOG_KEY
}


class Log(ABC):
    """Abstract class for logs."""

    def __init__(self, log_type: LogType):
        """
        Constructor

        :param log_type: The type of log
        """

        self.type: LogType = log_type
        self.user: User = User()
        self.object: BaseModel = BaseModel()

    @abstractmethod
    def set_object(self, object_id: int) -> None:
        """
        Set the object of the log

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
        Get the total number of items for the log

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
        Get the details for the log item

        :return: The details
        """
        pass


class FightLog(Log):
    """Class for fight logs"""

    def __init__(self):
        """
        Constructor

        """

        super().__init__(LogType.FIGHT)

        self.object: Fight = Fight()
        self.opponent: User = User()
        self.effective_status: GameStatus = GameStatus.ND
        self.user_is_challenger: bool = False

    def set_object(self, object_id: int) -> None:
        self.object = Fight.get(Fight.id == object_id)
        self.user_is_challenger = self.object.challenger == self.user
        self.opponent = self.object.opponent if self.user_is_challenger else self.object.challenger
        self.effective_status: GameStatus = GameStatus(self.object.status).get_status_by_challenger(
            self.user_is_challenger)

    def get_items(self, page) -> list[Fight]:
        return (self.object
                .select()
                .where((Fight.challenger == self.user) | (Fight.opponent == self.user))
                .order_by(Fight.date.desc())
                .paginate(page, c.STANDARD_LIST_SIZE))

    def get_total_items_count(self) -> int:
        return (self.object
                .select()
                .where((Fight.challenger == self.user) | (Fight.opponent == self.user))
                .count())

    def get_item_text(self) -> str:
        return phrases.FIGHT_LOG_ITEM_TEXT.format(self.opponent.get_markdown_mention(),
                                                  self.effective_status.get_log_emoji(),
                                                  get_belly_formatted(self.object.belly))

    def get_item_detail_text(self) -> str:
        challenger_text = phrases.CHALLENGER if self.user_is_challenger else phrases.OPPONENT
        date = self.object.date.strftime(c.STANDARD_DATE_TIME_FORMAT)

        if self.effective_status in [GameStatus.WON, GameStatus.LOST]:
            won = self.effective_status is GameStatus.WON
            outcome_text = phrases.LOG_ITEM_DETAIL_OUTCOME_BELLY_TEXT.format(
                (Emoji.LOG_POSITIVE if won else Emoji.LOG_NEGATIVE),
                (phrases.TEXT_WON if won else phrases.TEXT_LOST),
                get_belly_formatted(self.object.belly))
        else:
            outcome_text = phrases.LOG_ITEM_DETAIL_STATUS_TEXT.format(
                GAME_STATUS_DESCRIPTIONS[self.effective_status])

        return phrases.FIGHT_LOG_ITEM_DETAIL_TEXT.format(challenger_text, self.opponent.get_markdown_mention(),
                                                         date, self.object.get_win_probability(self.user),
                                                         outcome_text, self.object.message_id)


class DocQGameLog(Log):
    """Class for DocQGame logs"""

    def __init__(self):
        """
        Constructor

        """

        super().__init__(LogType.DOC_Q_GAME)

        self.object: DocQGame = DocQGame()

    def set_object(self, object_id: int) -> None:
        self.object = DocQGame.get(DocQGame.id == object_id)

    def get_items(self, page) -> list[DocQGame]:
        return (self.object
                .select()
                .where((DocQGame.user == self.user) & (DocQGame.status.in_([GameStatus.WON, GameStatus.LOST])))
                .order_by(DocQGame.datetime.desc())
                .paginate(page, c.STANDARD_LIST_SIZE))

    def get_total_items_count(self) -> int:
        return (self.object
                .select()
                .where((DocQGame.user == self.user) & (DocQGame.status.in_([GameStatus.WON, GameStatus.LOST])))
                .count())

    def get_item_text(self) -> str:
        return phrases.DOC_Q_GAME_LOG_ITEM_TEXT.format(GameStatus(self.object.status).get_log_emoji(),
                                                       get_belly_formatted(self.object.belly))

    def get_item_detail_text(self) -> str:
        date = self.object.datetime.strftime(c.STANDARD_DATE_TIME_FORMAT)
        correct_apple = int((str(self.object.correct_choices_index).split(c.STANDARD_SPLIT_CHAR))[0]) + 1
        won = GameStatus(self.object.status) is GameStatus.WON
        outcome_text = phrases.LOG_ITEM_DETAIL_OUTCOME_BELLY_TEXT.format(
            (Emoji.LOG_POSITIVE if won else Emoji.LOG_NEGATIVE),
            (phrases.TEXT_WON if won else phrases.TEXT_LOST),
            get_belly_formatted(self.object.belly))

        return phrases.DOC_Q_GAME_LOG_ITEM_DETAIL_TEXT.format(date, correct_apple, outcome_text, self.object.message_id)


class GameLog(Log):
    """Class for game logs"""

    def __init__(self):
        """
        Constructor
        """

        super().__init__(LogType.GAME)

        self.object: Game = Game()
        self.opponent: User = User()
        self.effective_status: GameStatus = GameStatus.ND
        self.user_is_challenger: bool = False

    def set_object(self, object_id: int) -> None:
        self.object = Game.get(Game.id == object_id)
        self.user_is_challenger = self.object.challenger == self.user
        self.opponent = self.object.opponent if self.user_is_challenger else self.object.challenger
        self.effective_status: GameStatus = GameStatus(self.object.status).get_status_by_challenger(
            self.user_is_challenger)

    def get_items(self, page) -> list[Game]:
        return (self.object
                .select()
                .where(((Game.challenger == self.user) | (Game.opponent == self.user)) &
                       (Game.status != GameStatus.AWAITING_SELECTION))  # Exclude because they don't have a type
                .order_by(Game.date.desc())
                .paginate(page, c.STANDARD_LIST_SIZE))

    def get_total_items_count(self) -> int:
        return (self.object
                .select()
                .where(((Game.challenger == self.user) | (Game.opponent == self.user)) &
                       (Game.status != GameStatus.AWAITING_SELECTION))
                .count())

    def get_item_text(self) -> str:
        return phrases.GAME_LOG_ITEM_TEXT.format(self.opponent.get_markdown_mention(),
                                                 self.effective_status.get_log_emoji(),
                                                 get_belly_formatted(self.object.wager))

    def get_item_detail_text(self) -> str:
        from src.service.game_service import get_game_name

        challenger_text = phrases.CHALLENGER if self.user_is_challenger else phrases.OPPONENT
        date = self.object.date.strftime(c.STANDARD_DATE_TIME_FORMAT)
        game_name = get_game_name(GameType(self.object.type))

        if self.effective_status in [GameStatus.WON, GameStatus.LOST]:
            won = self.effective_status is GameStatus.WON
            outcome_text = phrases.LOG_ITEM_DETAIL_OUTCOME_TEXT.format(
                (Emoji.LOG_POSITIVE if won else Emoji.LOG_NEGATIVE),
                (phrases.TEXT_WON if won else phrases.TEXT_LOST),
                get_belly_formatted(self.object.wager))
        else:
            outcome_text = phrases.LOG_ITEM_DETAIL_STATUS_TEXT.format(
                GAME_STATUS_DESCRIPTIONS[self.effective_status])

        return phrases.GAME_LOG_ITEM_DETAIL_TEXT.format(challenger_text, self.opponent.get_markdown_mention(),
                                                        game_name, date, get_belly_formatted(self.object.wager),
                                                        outcome_text, self.object.message_id)


LOGS = [FightLog(), DocQGameLog(), GameLog()]


def get_log_by_type(log_type: LogType) -> Log:
    """
    Get a notification by type

    :param log_type: The type of log
    :return: The notification
    """

    return next(log for log in LOGS if log.type is log_type)
