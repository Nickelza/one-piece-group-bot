from abc import abstractmethod

import constants as c
import resources.phrases as phrases
from src.model.BaseModel import BaseModel
from src.model.BountyGift import BountyGift
from src.model.Crew import Crew
from src.model.DocQGame import DocQGame
from src.model.Fight import Fight
from src.model.Game import Game
from src.model.IncomeTaxEvent import IncomeTaxEvent
from src.model.Leaderboard import Leaderboard
from src.model.LeaderboardUser import LeaderboardUser
from src.model.LegendaryPirate import LegendaryPirate
from src.model.User import User
from src.model.enums.BountyGiftRole import BountyGiftRole
from src.model.enums.BountyGiftStatus import BountyGiftStatus
from src.model.enums.Emoji import Emoji
from src.model.enums.GameStatus import GameStatus, GAME_STATUS_DESCRIPTIONS
from src.model.enums.LeaderboardRank import LeaderboardRank, get_rank_by_leaderboard_user, LeaderboardRankIndex
from src.model.enums.ListPage import ListPage
from src.model.enums.Location import get_first_new_world
from src.model.enums.LogType import LogType
from src.model.enums.ReservedKeyboardKeys import ReservedKeyboardKeys
from src.model.enums.Screen import Screen
from src.model.enums.income_tax.IncomeTaxBreakdown import IncomeTaxBreakdown
from src.model.enums.income_tax.IncomeTaxContribution import IncomeTaxContribution
from src.model.enums.income_tax.IncomeTaxDeduction import IncomeTaxDeduction
from src.model.enums.income_tax.IncomeTaxEventType import IncomeTaxEventType
from src.model.error.CustomException import UnauthorizedToViewItemException
from src.model.game.GameType import GameType
from src.service.bounty_service import get_belly_formatted
from src.service.date_service import default_datetime_format
from src.service.math_service import get_value_from_percentage, get_percentage_from_value
from src.service.message_service import mention_markdown_v2, escape_valid_markdown_chars, get_message_url, get_deeplink

LOG_TYPE_BUTTON_TEXTS = {
    LogType.FIGHT: phrases.FIGHT_LOG_KEY,
    LogType.DOC_Q_GAME: phrases.DOC_Q_GAME_LOG_KEY,
    LogType.GAME: phrases.GAME_LOG_KEY,
    LogType.BOUNTY_GIFT: phrases.BOUNTY_GIFT_LOG_KEY,
    LogType.LEGENDARY_PIRATE: phrases.LEGENDARY_PIRATE_LOG_KEY,
    LogType.NEW_WORLD_PIRATE: phrases.NEW_WORLD_PIRATE_LOG_KEY,
    LogType.LEADERBOARD_RANK: phrases.LEADERBOARD_RANK_LOG_KEY,
    LogType.INCOME_TAX_EVENT: phrases.INCOME_TAX_EVENT_LOG_KEY,
}

LOG_TYPE_DETAIL_TEXT_FILL_IN = {
    LogType.FIGHT: phrases.FIGHT_LOG_ITEM_DETAIL_TEXT_FILL_IN,
    LogType.DOC_Q_GAME: phrases.DOC_Q_GAME_LOG_ITEM_DETAIL_TEXT_FILL_IN,
    LogType.GAME: phrases.GAME_LOG_ITEM_DETAIL_TEXT_FILL_IN,
    LogType.BOUNTY_GIFT: phrases.BOUNTY_GIFT_LOG_ITEM_DETAIL_TEXT_FILL_IN,
    LogType.LEGENDARY_PIRATE: phrases.LEGENDARY_PIRATE_LOG_ITEM_DETAIL_TEXT_FILL_IN,
    LogType.NEW_WORLD_PIRATE: phrases.NEW_WORLD_PIRATE_LOG_ITEM_DETAIL_TEXT_FILL_IN,
    LogType.LEADERBOARD_RANK: phrases.LEADERBOARD_RANK_LOG_ITEM_DETAIL_TEXT_FILL_IN,
    LogType.INCOME_TAX_EVENT: phrases.INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_FILL_IN,
}


class Log(ListPage):
    """Abstract class for logs."""

    def __init__(self, log_type: LogType, only_by_boss: bool = False, has_stats: bool = True):
        """
        Constructor

        :param log_type: The type of log
        :param only_by_boss: True if the log is visible only by a boss
        """

        self.type: LogType = log_type
        self.only_by_boss: bool = only_by_boss
        self.user: User = User()
        self.object: BaseModel = BaseModel()
        self.has_stats: bool = has_stats

        super().__init__()

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

    def get_stats_text(self) -> str:
        """
        Get the stats for the log

        :return: The stats
        """
        pass

    @staticmethod
    def get_deeplink_by_type(log_type: LogType, item_id: int) -> str:
        """
        Get the deeplink for the log

        :param log_type: The log type
        :param item_id: The item id
        :return: The deeplink
        """

        from src.chat.private.screens.screen_logs_type_detail import LogTypeReservedKeys

        info: dict = {LogTypeReservedKeys.TYPE: log_type, LogTypeReservedKeys.ITEM_ID: item_id}
        return get_deeplink(info, screen=Screen.PVT_LOGS_TYPE_DETAIL)

    def get_deeplink(self, item_id) -> str:
        """
        Get the deeplink for the log

        :param item_id: The item id
        :return: The deeplink
        """

        return self.get_deeplink_by_type(self.type, item_id)

    def get_text_fill_in(self) -> str:
        """
        Get the text fill in for the log

        :return: The text fill in
        """

        return LOG_TYPE_DETAIL_TEXT_FILL_IN[self.type]


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
        self.opponent = self.object.get_opponent(self.user)
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
        return phrases.FIGHT_LOG_ITEM_TEXT.format(self.effective_status.get_log_emoji(),
                                                  self.opponent.get_markdown_mention(),
                                                  get_belly_formatted(self.object.belly))

    def get_item_detail_text(self) -> str:
        if self.user != self.object.challenger and self.user != self.object.opponent:
            raise UnauthorizedToViewItemException()

        challenger_text = phrases.OPPONENT if self.user_is_challenger else phrases.CHALLENGER
        date = default_datetime_format(self.object.date, self.user)

        if self.effective_status in [GameStatus.WON, GameStatus.LOST]:
            won = self.effective_status is GameStatus.WON
            outcome_text = phrases.LOG_ITEM_DETAIL_OUTCOME_BELLY_TEXT.format(
                (Emoji.LOG_POSITIVE if won else Emoji.LOG_NEGATIVE),
                (phrases.TEXT_WON if won else phrases.TEXT_LOST),
                get_belly_formatted(self.object.belly))
        else:
            outcome_text = phrases.LOG_ITEM_DETAIL_STATUS_TEXT.format(
                GAME_STATUS_DESCRIPTIONS[self.effective_status])

        return phrases.FIGHT_LOG_ITEM_DETAIL_TEXT.format(
            challenger_text, self.opponent.get_markdown_mention(), date, self.object.get_win_probability(self.user),
            outcome_text, get_message_url(self.object.message_id, self.object.group_chat))

    def get_stats_text(self) -> str:
        total_fights = self.get_total_items_count()
        total_wins = self.object.get_total_win_or_loss(self.user, GameStatus.WON)
        total_wins_percentage = int(get_percentage_from_value(total_wins, total_fights))
        total_losses = self.object.get_total_win_or_loss(self.user, GameStatus.LOST)
        total_losses_percentage = int(get_percentage_from_value(total_losses, total_fights))
        max_won_fight = self.object.get_max_won_or_lost(self.user, GameStatus.WON)
        max_lost_fight = self.object.get_max_won_or_lost(self.user, GameStatus.LOST)
        most_fought_user, most_fought_count = self.object.get_most_fought_user(self.user)
        return phrases.FIGHT_LOG_STATS_TEXT.format(
            total_fights,
            total_wins,
            total_wins_percentage,
            total_losses,
            total_losses_percentage,
            get_belly_formatted(self.object.get_total_belly_won_or_lost(self.user, GameStatus.WON)),
            get_belly_formatted(self.object.get_total_belly_won_or_lost(self.user, GameStatus.LOST)),
            get_belly_formatted(max_won_fight.belly),
            max_won_fight.get_opponent(self.user).get_markdown_mention(),
            self.get_deeplink(max_won_fight.id),
            get_belly_formatted(max_lost_fight.belly),
            max_lost_fight.get_opponent(self.user).get_markdown_mention(),
            self.get_deeplink(max_lost_fight.id),
            most_fought_user.get_markdown_mention(),
            most_fought_count)


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
                .order_by(DocQGame.date.desc())
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
        date = default_datetime_format(self.object.date, self.user)
        correct_apple = int((str(self.object.correct_choices_index).split(c.STANDARD_SPLIT_CHAR))[0]) + 1
        won = GameStatus(self.object.status) is GameStatus.WON
        outcome_text = phrases.LOG_ITEM_DETAIL_OUTCOME_BELLY_TEXT.format(
            (Emoji.LOG_POSITIVE if won else Emoji.LOG_NEGATIVE),
            (phrases.TEXT_WON if won else phrases.TEXT_LOST),
            get_belly_formatted(self.object.belly))

        return phrases.DOC_Q_GAME_LOG_ITEM_DETAIL_TEXT.format(
            date, correct_apple, outcome_text,
            get_message_url(self.object.message_id, self.object.group_chat))

    def get_stats_text(self) -> str:
        total_games = self.get_total_items_count()
        total_wins = self.object.get_total_win_or_loss(self.user, GameStatus.WON)
        total_wins_percentage = int(get_percentage_from_value(total_wins, total_games))
        total_losses = self.object.get_total_win_or_loss(self.user, GameStatus.LOST)
        total_losses_percentage = int(get_percentage_from_value(total_losses, total_games))
        max_won_game = self.object.get_max_won_or_lost(self.user, GameStatus.WON)
        max_lost_game = self.object.get_max_won_or_lost(self.user, GameStatus.LOST)

        return phrases.DOC_Q_GAME_LOG_STATS_TEXT.format(
            total_games,
            total_wins,
            total_wins_percentage,
            total_losses,
            total_losses_percentage,
            get_belly_formatted(self.object.get_total_belly_won_or_lost(self.user, GameStatus.WON)),
            get_belly_formatted(self.object.get_total_belly_won_or_lost(self.user, GameStatus.LOST)),
            get_belly_formatted(max_won_game.belly),
            self.get_deeplink(max_won_game.id),
            get_belly_formatted(max_lost_game.belly),
            self.get_deeplink(max_lost_game.id))


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
        return phrases.GAME_LOG_ITEM_TEXT.format(self.effective_status.get_log_emoji(),
                                                 self.opponent.get_markdown_mention(),
                                                 get_belly_formatted(self.object.wager))

    def get_item_detail_text(self) -> str:

        challenger_text = phrases.OPPONENT if self.user_is_challenger else phrases.CHALLENGER
        date = default_datetime_format(self.object.date, self.user)
        game_name = (GameType(self.object.type).get_name() if self.object.type is not None
                     else phrases.GAME_NOT_SELECTED_NAME)

        if self.effective_status in [GameStatus.WON, GameStatus.LOST]:
            won = self.effective_status is GameStatus.WON
            outcome_text = phrases.LOG_ITEM_DETAIL_OUTCOME_TEXT.format(
                (Emoji.LOG_POSITIVE if won else Emoji.LOG_NEGATIVE),
                (phrases.TEXT_WON if won else phrases.TEXT_LOST),
                get_belly_formatted(self.object.wager))
        else:
            outcome_text = phrases.LOG_ITEM_DETAIL_STATUS_TEXT.format(
                GAME_STATUS_DESCRIPTIONS[self.effective_status])

        return phrases.GAME_LOG_ITEM_DETAIL_TEXT.format(
            challenger_text, self.opponent.get_markdown_mention(), game_name, date,
            get_belly_formatted(self.object.wager), outcome_text,
            get_message_url(self.object.message_id, self.object.group_chat))

    def get_stats_text(self) -> str:
        total_games = self.get_total_items_count()
        total_wins = self.object.get_total_win_or_loss_or_draw(self.user, GameStatus.WON)
        total_wins_percentage = int(get_percentage_from_value(total_wins, total_games))
        total_losses = self.object.get_total_win_or_loss_or_draw(self.user, GameStatus.LOST)
        total_losses_percentage = int(get_percentage_from_value(total_losses, total_games))
        total_draws = self.object.get_total_win_or_loss_or_draw(self.user, GameStatus.DRAW)
        total_draws_percentage = int(get_percentage_from_value(total_draws, total_games))
        max_won_game = self.object.get_max_won_or_lost(self.user, GameStatus.WON)
        max_lost_game = self.object.get_max_won_or_lost(self.user, GameStatus.LOST)
        most_challenged_user, most_challenged_count = self.object.get_most_challenged_user(self.user)
        most_played_game, most_played_count = self.object.get_most_played_game(self.user)

        return phrases.GAME_LOG_STATS_TEXT.format(
            total_games,
            total_wins,
            total_wins_percentage,
            total_losses,
            total_losses_percentage,
            total_draws,
            total_draws_percentage,
            get_belly_formatted(self.object.get_total_belly_won_or_lost(self.user, GameStatus.WON)),
            get_belly_formatted(self.object.get_total_belly_won_or_lost(self.user, GameStatus.LOST)),
            get_belly_formatted(max_won_game.wager),
            max_won_game.get_name(),
            self.get_deeplink(max_won_game.id),
            get_belly_formatted(max_lost_game.wager),
            max_lost_game.get_name(),
            self.get_deeplink(max_lost_game.id),
            most_challenged_user.get_markdown_mention(),
            most_challenged_count,
            most_played_game.get_name(),
            most_played_count)


class BountyGiftLog(Log):
    """Class for bounty gift logs"""

    def __init__(self):
        """
        Constructor

        """

        super().__init__(LogType.BOUNTY_GIFT)

        self.object: BountyGift = BountyGift()
        self.other_user: User = User()
        self.user_is_sender: bool = False
        self.log_emoji: Emoji = Emoji.LOG_NEUTRAL

    def set_object(self, object_id: int) -> None:
        self.object: BountyGift = BountyGift.get(BountyGift.id == object_id)
        self.user_is_sender = self.object.sender == self.user
        self.other_user = self.object.receiver if self.user_is_sender else self.object.sender
        self.log_emoji = Emoji.LOG_NEGATIVE if self.user_is_sender else Emoji.LOG_POSITIVE

    def get_items(self, page) -> list[BountyGift]:
        return (self.object
                .select()
                .where(((BountyGift.sender == self.user) | (BountyGift.receiver == self.user)) &
                       (BountyGift.status == BountyGiftStatus.CONFIRMED))
                .order_by(BountyGift.date.desc())
                .paginate(page, c.STANDARD_LIST_SIZE))

    def get_total_items_count(self) -> int:
        return (self.object
                .select()
                .where(((BountyGift.sender == self.user) | (BountyGift.receiver == self.user)) &
                       (BountyGift.status == BountyGiftStatus.CONFIRMED))
                .count())

    def get_item_text(self) -> str:
        to_text = phrases.TEXT_TO if self.user_is_sender else phrases.TEXT_FROM
        return phrases.BOUNTY_GIFT_LOG_ITEM_TEXT.format(self.log_emoji, get_belly_formatted(self.object.amount),
                                                        to_text, self.other_user.get_markdown_mention())

    def get_item_detail_text(self) -> str:
        sender_text = phrases.RECEIVER if self.user_is_sender else phrases.SENDER
        date = default_datetime_format(self.object.date, self.user)

        tax_text = ''
        if self.user_is_sender:
            tax_amount = int(get_value_from_percentage(self.object.amount, self.object.tax_percentage))
            total_amount = self.object.amount + tax_amount
            tax_text = phrases.BOUNTY_GIFT_LOG_ITEM_DETAIL_TAX_TEXT.format(get_belly_formatted(tax_amount),
                                                                           self.object.tax_percentage,
                                                                           get_belly_formatted(total_amount))

        return phrases.BOUNTY_GIFT_LOG_ITEM_DETAIL_TEXT.format(
            sender_text, self.other_user.get_markdown_mention(),
            date, get_belly_formatted(self.object.amount), tax_text,
            get_message_url(self.object.message_id, self.object.group_chat))

    def get_stats_text(self) -> str:
        highest_sent_gift = self.object.get_highest_belly_sent_or_received(self.user, BountyGiftRole.SENDER)
        highest_sent_user, highest_sent_amount = highest_sent_gift.receiver, highest_sent_gift.amount
        highest_received_gift = self.object.get_highest_belly_sent_or_received(self.user, BountyGiftRole.RECEIVER)
        highest_received_user, highest_received_amount = highest_received_gift.sender, highest_received_gift.amount
        most_sent_user, most_sent_amount = self.object.get_top_givers_or_receiver(self.user, BountyGiftRole.SENDER)
        most_received_user, most_received_amount = self.object.get_top_givers_or_receiver(self.user,
                                                                                          BountyGiftRole.RECEIVER)

        return phrases.BOUNTY_GIFT_LOG_STATS_TEXT.format(
            self.get_total_items_count(),
            get_belly_formatted(self.object.get_total_belly_sent_or_received(self.user, BountyGiftRole.SENDER)),
            get_belly_formatted(self.object.get_total_belly_sent_or_received(self.user, BountyGiftRole.RECEIVER)),
            get_belly_formatted(highest_sent_amount),
            highest_sent_user.get_markdown_name(),
            self.get_deeplink(highest_sent_gift.id),
            get_belly_formatted(highest_received_amount),
            highest_received_user.get_markdown_name(),
            self.get_deeplink(highest_received_gift.id),
            most_sent_user.get_markdown_mention(),
            get_belly_formatted(most_sent_amount),
            most_received_user.get_markdown_mention(),
            get_belly_formatted(most_received_amount))


class LegendaryPirateLog(Log):
    """Class for legendary pirate logs"""

    def __init__(self):
        """
        Constructor

        """

        super().__init__(LogType.LEGENDARY_PIRATE, has_stats=False)

        self.object: LegendaryPirate = LegendaryPirate()
        self.user: User = User()

    def set_object(self, object_id: int) -> None:
        self.object: LegendaryPirate = LegendaryPirate.get(LegendaryPirate.id == object_id)
        self.user: User = self.object.user

    def get_items(self, page) -> list[LegendaryPirate]:
        return (self.object
                .select()
                .order_by(LegendaryPirate.date.desc())
                .paginate(page, c.STANDARD_LIST_SIZE))

    def get_total_items_count(self) -> int:
        return (self.object
                .select()
                .count())

    def get_item_text(self) -> str:
        return phrases.LEGENDARY_PIRATE_LOG_ITEM_TEXT.format(mention_markdown_v2(self.user.tg_user_id,
                                                                                 self.object.epithet))

    def get_item_detail_text(self) -> str:
        return phrases.LEGENDARY_PIRATE_LOG_ITEM_DETAIL_TEXT.format(self.user.get_markdown_mention(),
                                                                    self.object.epithet,
                                                                    self.object.reason)


class NewWorldPirateLog(Log):
    """Class for new world pirate logs"""

    def __init__(self):
        """
        Constructor

        """

        super().__init__(LogType.NEW_WORLD_PIRATE, only_by_boss=True, has_stats=False)

        self.object: User = User()

    def set_object(self, object_id: int) -> None:
        self.object: User = User.get(User.id == object_id)

    def get_items(self, page) -> list[User]:
        return (self.object
                .select()
                .where((User.location_level >= get_first_new_world().level)
                       & (User.get_is_not_arrested_statement_condition()))
                .order_by(User.bounty.desc())
                .paginate(page, c.STANDARD_LIST_SIZE))

    def get_total_items_count(self) -> int:
        return (self.object
                .select()
                .where((User.location_level >= get_first_new_world().level)
                       & (User.get_is_not_arrested_statement_condition()))
                .count())

    def get_item_text(self) -> str:
        return phrases.NEW_WORLD_PIRATE_LOG_ITEM_TEXT.format(self.object.get_markdown_mention(),
                                                             get_belly_formatted(self.object.bounty))

    def get_item_detail_text(self) -> str:
        if self.object.is_crew_member():
            crew: Crew = self.object.crew
            crew_text = phrases.NEW_WORLD_PIRATE_LOG_ITEM_DETAIL_CREW_TEXT.format(
                escape_valid_markdown_chars(crew.name))
        else:
            crew_text = ''

        return phrases.NEW_WORLD_PIRATE_LOG_ITEM_DETAIL_TEXT.format(
            self.object.get_markdown_mention(), get_belly_formatted(self.object.bounty),
            escape_valid_markdown_chars(self.object.get_location().name), crew_text)


class LeaderboardRankLog(Log):
    """Class for leaderboard rank logs"""

    def __init__(self):
        """
        Constructor

        """

        super().__init__(LogType.LEADERBOARD_RANK)

        self.object: LeaderboardUser = LeaderboardUser()
        self.leaderboard: Leaderboard = Leaderboard()

    def set_object(self, object_id: int) -> None:
        self.object: LeaderboardUser = LeaderboardUser.get(LeaderboardUser.id == object_id)
        self.leaderboard: Leaderboard = self.object.leaderboard

    def get_items(self, page) -> list[LeaderboardUser]:
        return (self.object
                .select().join(Leaderboard)
                .where((LeaderboardUser.user == self.user) & (Leaderboard.group.is_null()))
                .order_by(LeaderboardUser.id.desc())
                .paginate(page, c.STANDARD_LIST_SIZE))

    def get_total_items_count(self) -> int:
        return (self.object
                .select().join(Leaderboard)
                .where((LeaderboardUser.user == self.user) & (Leaderboard.group.is_null()))
                .count())

    def get_item_text(self) -> str:
        return phrases.LEADERBOARD_RANK_LOG_ITEM_TEXT.format(
            self.leaderboard.week, self.leaderboard.year,
            LeaderboardRank.get_emoji_and_rank_message(get_rank_by_leaderboard_user(self.object)))

    def get_item_detail_text(self) -> str:
        return phrases.LEADERBOARD_RANK_LOG_ITEM_DETAIL_TEXT.format(
            self.leaderboard.week, self.leaderboard.year,
            self.object.position,
            LeaderboardRank.get_emoji_and_rank_message(get_rank_by_leaderboard_user(self.object)),
            get_belly_formatted(self.object.bounty))

    def get_stats_text(self) -> str:
        total_appearances = self.get_total_items_count()
        appearances_as_pirate_king = self.object.get_appearances_as_rank(self.user, LeaderboardRankIndex.PIRATE_KING)
        appearances_as_pirate_king_percentage = int(get_percentage_from_value(appearances_as_pirate_king,
                                                                              total_appearances))
        appearances_as_emperor = self.object.get_appearances_as_rank(self.user, LeaderboardRankIndex.EMPEROR)
        appearances_as_emperor_percentage = int(get_percentage_from_value(appearances_as_emperor, total_appearances))
        appearances_as_first_mate = self.object.get_appearances_as_rank(self.user, LeaderboardRankIndex.FIRST_MATE)
        appearances_as_first_mate_percentage = int(get_percentage_from_value(appearances_as_first_mate,
                                                                             total_appearances))
        appearances_as_supernova = self.object.get_appearances_as_rank(self.user, LeaderboardRankIndex.SUPERNOVA)
        appearances_as_supernova_percentage = int(get_percentage_from_value(appearances_as_supernova,
                                                                            total_appearances))
        max_by_rank: LeaderboardUser = self.object.get_max_rank_attained(self.user)
        max_by_bounty: LeaderboardUser = self.object.get_max_bounty_attained(self.user)

        return phrases.LEADERBOARD_RANK_LOG_STATS_TEXT.format(
            total_appearances,
            appearances_as_pirate_king,
            appearances_as_pirate_king_percentage,
            appearances_as_emperor,
            appearances_as_emperor_percentage,
            appearances_as_first_mate,
            appearances_as_first_mate_percentage,
            appearances_as_supernova,
            appearances_as_supernova_percentage,
            get_rank_by_leaderboard_user(max_by_rank).get_emoji_and_rank_message(),
            max_by_rank.position,
            self.get_deeplink(max_by_rank.id),
            get_belly_formatted(max_by_bounty.bounty),
            max_by_bounty.position,
            self.get_deeplink(max_by_bounty.id))


class IncomeTaxEventLog(Log):
    """Class for income tax event logs"""

    def __init__(self):
        """
        Constructor

        """

        super().__init__(LogType.INCOME_TAX_EVENT, has_stats=False)

        self.object: IncomeTaxEvent = IncomeTaxEvent()
        self.user: User = User()

    def set_object(self, object_id: int) -> None:
        self.object: IncomeTaxEvent = IncomeTaxEvent.get(IncomeTaxEvent.id == object_id)
        self.user: User = self.object.user

    def get_items(self, page) -> list[IncomeTaxEvent]:
        return (self.object
                .select()
                .where((IncomeTaxEvent.user == self.user))
                .order_by(IncomeTaxEvent.date.desc())
                .paginate(page, c.STANDARD_LIST_SIZE))

    def get_total_items_count(self) -> int:
        return (self.object
                .select()
                .where((IncomeTaxEvent.user == self.user))
                .count())

    def get_item_text(self) -> str:
        return phrases.INCOME_TAX_EVENT_LOG_ITEM_TEXT.format(self.object.get_event_type_description(),
                                                             get_belly_formatted(self.object.amount))

    def get_item_detail_text(self) -> str:
        from src.service.message_service import get_deeplink

        # Build url to event log
        event_type = self.object.get_event_type()
        log_type: LogType = event_type.get_log_type()
        event_log_url = ''

        if log_type is not None:
            event_log_url = Log.get_deeplink_by_type(log_type, self.object.event_id)
        else:
            # Manually manage events that are not shown in regular logs screen
            item_id = self.object.event_id
            match event_type:
                case IncomeTaxEventType.BOUNTY_LOAN:
                    event_log_url = get_deeplink({ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: item_id},
                                                 screen=Screen.PVT_BOUNTY_LOAN_DETAIL)

                case IncomeTaxEventType.PREDICTION:
                    event_log_url = get_deeplink({ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: item_id},
                                                 screen=Screen.PVT_PREDICTION_DETAIL)

        breakdown_list = IncomeTaxBreakdown.from_string(self.object.breakdown_list)
        deduction_list = IncomeTaxDeduction.from_string(self.object.deduction_list)
        contribution_list = IncomeTaxContribution.from_string(self.object.contribution_list)

        total_tax = IncomeTaxBreakdown.get_amount_with_deduction_from_list(breakdown_list, deduction_list)
        total_tax_percentage = int(get_percentage_from_value(total_tax, self.object.amount, add_decimal=False))
        net_income = self.object.amount - total_tax

        deduction_text = ''
        if len(deduction_list) > 0:
            deduction_text = phrases.INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_DEDUCTION
            for deduction in deduction_list:
                deduction_text += phrases.INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_DEDUCTION_ITEM.format(
                    deduction.get_description(),
                    deduction.percentage)

        contribution_text = ''
        if len(contribution_list) > 0:
            contribution_text = phrases.INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_CONTRIBUTION
            for contribution in contribution_list:
                contribution_text += phrases.INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_CONTRIBUTION_ITEM.format(
                    contribution.get_description(),
                    get_belly_formatted(int(get_value_from_percentage(total_tax, contribution.percentage))),
                    contribution.percentage)

        breakdown_text = ''
        for breakdown in breakdown_list:
            breakdown_text += phrases.INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_BREAKDOWN_ITEM.format(
                get_belly_formatted(breakdown.taxable_amount),
                get_belly_formatted(breakdown.taxable_amount - breakdown.tax_amount),
                get_belly_formatted(breakdown.tax_amount),
                int(get_percentage_from_value(breakdown.tax_amount, breakdown.taxable_amount)))

        return phrases.INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT.format(
            self.object.get_event_type_description(),
            event_log_url,
            self.user.get_datetime_formatted(self.object.date),
            get_belly_formatted(self.object.amount),
            get_belly_formatted(net_income),
            get_belly_formatted(total_tax),
            total_tax_percentage,
            deduction_text,
            contribution_text,
            breakdown_text)


LOGS = [FightLog(), DocQGameLog(), GameLog(), BountyGiftLog(), LegendaryPirateLog(), NewWorldPirateLog(),
        LeaderboardRankLog(), IncomeTaxEventLog()]


def get_log_by_type(log_type: LogType) -> Log:
    """
    Get a notification by type

    :param log_type: The type of log
    :return: The notification
    """

    return next(log for log in LOGS if log.type is log_type)
