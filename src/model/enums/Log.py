from abc import abstractmethod
from datetime import datetime
from typing import Any

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
from src.model.Plunder import Plunder
from src.model.User import User
from src.model.Warlord import Warlord
from src.model.enums.BountyGiftRole import BountyGiftRole
from src.model.enums.BountyGiftStatus import BountyGiftStatus
from src.model.enums.Emoji import Emoji
from src.model.enums.GameStatus import GameStatus, GAME_STATUS_DESCRIPTIONS
from src.model.enums.LeaderboardRank import (
    LeaderboardRank,
    get_rank_by_leaderboard_user,
    LeaderboardRankIndex,
)
from src.model.enums.ListPage import ListPage, EmojiLegend
from src.model.enums.Location import get_first_new_world
from src.model.enums.LogType import LogType
from src.model.enums.ReservedKeyboardKeys import (
    ReservedKeyboardKeys,
    LogTypeReservedKeys,
    FightPlunderReservedKeys,
)
from src.model.enums.Screen import Screen
from src.model.enums.income_tax.IncomeTaxBreakdown import IncomeTaxBreakdown
from src.model.enums.income_tax.IncomeTaxContribution import IncomeTaxContribution
from src.model.enums.income_tax.IncomeTaxDeduction import IncomeTaxDeduction
from src.model.enums.income_tax.IncomeTaxEventType import IncomeTaxEventType
from src.model.game.GameType import GameType
from src.model.pojo.Keyboard import Keyboard
from src.service.date_service import (
    default_datetime_format,
    convert_hours_to_duration,
)
from src.service.message_service import (
    mention_markdown_v2,
    escape_valid_markdown_chars,
    get_message_url,
    get_deeplink,
)
from src.utils.math_utils import get_value_from_percentage, get_percentage_from_value
from src.utils.phrase_utils import get_outcome_text
from src.utils.string_utils import get_belly_formatted

LOG_TYPE_BUTTON_TEXTS = {
    LogType.FIGHT: phrases.FIGHT_LOG_KEY,
    LogType.DOC_Q_GAME: phrases.DOC_Q_GAME_LOG_KEY,
    LogType.GAME: phrases.GAME_LOG_KEY,
    LogType.BOUNTY_GIFT: phrases.BOUNTY_GIFT_LOG_KEY,
    LogType.LEGENDARY_PIRATE: phrases.LEGENDARY_PIRATE_LOG_KEY,
    LogType.NEW_WORLD_PIRATE: phrases.NEW_WORLD_PIRATE_LOG_KEY,
    LogType.WARLORD: phrases.WARLORD_LOG_KEY,
    LogType.LEADERBOARD_RANK: phrases.LEADERBOARD_RANK_LOG_KEY,
    LogType.INCOME_TAX_EVENT: phrases.INCOME_TAX_EVENT_LOG_KEY,
    LogType.PLUNDER: phrases.PLUNDER_LOG_KEY,
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
    LogType.WARLORD: phrases.WARLORD_LOG_ITEM_DETAIL_TEXT_FILL_IN,
    LogType.PLUNDER: phrases.PLUNDER_LOG_ITEM_DETAIL_TEXT_FILL_IN,
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
    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[BaseModel]:
        """
        Get a list item for the log

        :param page: The page
        :param limit: The limit
        :return: The list item
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
        return super().get_item_detail_text()

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

    def get_is_admin_condition_stmt(self) -> Any:
        """
        Get the is admin condition statement for the log

        :return: The is admin condition statement
        """

        return True if self.user.is_admin else (User.is_admin == False)

    def get_keyboard(self) -> list[list[Keyboard]]:
        """
        Get a custom keyboard for the log

        :return: The keyboard
        """

        pass


# noinspection DuplicatedCode
# Same as plunder
class FightLog(Log):
    """Class for fight logs"""

    def __init__(self):
        """
        Constructor

        """

        super().__init__(LogType.FIGHT)

        self.object: Fight = Fight()
        self.opponent: User = User()
        self.user_is_challenger: bool = False
        self.effective_status: GameStatus = GameStatus.ND

    def set_object(self, object_id: int) -> None:
        self.object = Fight.get(Fight.id == object_id)
        self.user_is_challenger = self.object.challenger == self.user
        self.opponent = self.object.get_opponent(self.user)
        self.legend = self.get_emoji_legend()
        self.effective_status = self.legend.get_game_status()

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[Fight]:
        return (
            self.object.select()
            .where(
                ((Fight.challenger == self.user) | (Fight.opponent == self.user))
                & (Fight.status.in_([GameStatus.WON, GameStatus.LOST]))
                & (self.get_active_filter_list_condition())
            )
            .order_by(Fight.date.desc())
            .paginate(page, limit)
        )

    def get_item_text(self) -> str:
        return phrases.FIGHT_LOG_ITEM_TEXT.format(
            self.legend.get_formatted(),
            self.opponent.get_markdown_mention(),
            get_belly_formatted(self.object.belly),
        )

    def get_item_detail_text(self) -> str:
        super().get_item_detail_text()

        challenger_text = phrases.OPPONENT if self.user_is_challenger else phrases.CHALLENGER
        date = default_datetime_format(self.object.date, self.user)

        if self.effective_status in [GameStatus.WON, GameStatus.LOST]:
            outcome_text = get_outcome_text(
                (GameStatus(self.legend.status) is GameStatus.WON), self.object.belly
            )
        else:
            outcome_text = phrases.LOG_ITEM_DETAIL_STATUS_TEXT.format(
                GAME_STATUS_DESCRIPTIONS[self.effective_status]
            )

        go_to_message_text = ""
        if self.object.group_chat is not None:
            go_to_message_text = phrases.LOG_ITEM_DETAIL_GO_TO_MESSAGE.format(
                get_message_url(self.object.message_id, self.object.group_chat)
            )

        ot_text = phrases.FIGHT_LOG_ITEM_DETAIL_TEXT.format(
            challenger_text,
            self.opponent.get_markdown_mention(),
            date,
            self.object.get_win_probability(self.user),
            outcome_text,
            go_to_message_text,
        )

        # Fight still revengable
        if self.object.can_revenge(self.user):
            ot_text += phrases.FIGHT_ATTACK_CAN_REVENGE.format(
                self.object.get_revenge_remaining_duration()
            )
        # Was in response to a previous attack
        elif self.object.in_revenge_to_fight is not None:
            ot_text += phrases.FIGHT_LOG_ITEM_DETAIL_TEXT_IN_RESPONSE.format(
                Log.get_deeplink_by_type(LogType.FIGHT, self.object.in_revenge_to_fight.id)
            )
        # Has been revenged
        if revenge_fight := self.object.get_revenge_fight():
            ot_text += phrases.FIGHT_LOG_ITEM_DETAIL_TEXT_REVENGED.format(
                Log.get_deeplink_by_type(LogType.FIGHT, revenge_fight.id)
            )

        return ot_text

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
            get_belly_formatted(
                self.object.get_total_belly_won_or_lost(self.user, GameStatus.WON)
            ),
            get_belly_formatted(
                self.object.get_total_belly_won_or_lost(self.user, GameStatus.LOST)
            ),
            get_belly_formatted(max_won_fight.belly),
            max_won_fight.get_opponent(self.user).get_markdown_mention(),
            self.get_deeplink(max_won_fight.id),
            get_belly_formatted(max_lost_fight.belly),
            max_lost_fight.get_opponent(self.user).get_markdown_mention(),
            self.get_deeplink(max_lost_fight.id),
            most_fought_user.get_markdown_mention(),
            most_fought_count,
        )

    def get_emoji_legend_list(self) -> list[EmojiLegend]:
        return [
            EmojiLegend(
                Emoji.LOG_POSITIVE,
                phrases.GAME_STATUS_WON,
                (
                    ((Fight.challenger == self.user) & (Fight.status == GameStatus.WON))
                    | ((Fight.opponent == self.user) & (Fight.status == GameStatus.LOST))
                ),
                status=GameStatus.WON,
            ),
            EmojiLegend(
                Emoji.LOG_NEGATIVE,
                phrases.GAME_STATUS_LOST,
                (
                    ((Fight.opponent == self.user) & (Fight.status == GameStatus.WON))
                    | ((Fight.challenger == self.user) & (Fight.status == GameStatus.LOST))
                ),
                status=GameStatus.LOST,
            ),
        ]

    def get_keyboard(self) -> list[list[Keyboard]]:
        # Return the revenge button
        if not self.object.can_revenge(self.user):
            return []

        return [
            [
                Keyboard(
                    phrases.PVT_KEY_FIGHT_REVENGE,
                    screen=Screen.PVT_FIGHT,
                    info={
                        ReservedKeyboardKeys.CONFIRM: 1,
                        FightPlunderReservedKeys.OPPONENT_ID: self.object.challenger.id,
                        FightPlunderReservedKeys.IN_REVENGE_TO_ATTACK_ID: self.object.id,
                    },
                )
            ]
        ]


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
        self.legend = self.get_emoji_legend()

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[DocQGame]:
        return (
            self.object.select()
            .where(
                (DocQGame.user == self.user)
                & (DocQGame.status.in_([GameStatus.WON, GameStatus.LOST]))
                & (self.get_active_filter_list_condition())
            )
            .order_by(DocQGame.date.desc())
            .paginate(page, limit)
        )

    def get_item_text(self) -> str:
        return phrases.DOC_Q_GAME_LOG_ITEM_TEXT.format(
            self.legend.get_formatted(), get_belly_formatted(self.object.belly)
        )

    def get_item_detail_text(self) -> str:
        super().get_item_detail_text()

        date = default_datetime_format(self.object.date, self.user)
        correct_apple = self.object.get_correct_apple_number()
        won = GameStatus(self.object.status) is GameStatus.WON
        outcome_text = get_outcome_text(won, self.object.belly)

        go_to_message_text = ""
        if self.object.group_chat is not None:
            go_to_message_text = phrases.LOG_ITEM_DETAIL_GO_TO_MESSAGE.format(
                get_message_url(self.object.message_id, self.object.group_chat)
            )

        return phrases.DOC_Q_GAME_LOG_ITEM_DETAIL_TEXT.format(
            date,
            correct_apple,
            outcome_text,
            go_to_message_text,
        )

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
            get_belly_formatted(
                self.object.get_total_belly_won_or_lost(self.user, GameStatus.WON)
            ),
            get_belly_formatted(
                self.object.get_total_belly_won_or_lost(self.user, GameStatus.LOST)
            ),
            get_belly_formatted(max_won_game.belly),
            self.get_deeplink(max_won_game.id),
            get_belly_formatted(max_lost_game.belly),
            self.get_deeplink(max_lost_game.id),
        )

    def get_emoji_legend_list(self) -> list[EmojiLegend]:
        """
        Get the emoji legend list

        :return: The emoji legend list
        """

        return [
            EmojiLegend(
                Emoji.LOG_POSITIVE,
                phrases.GAME_STATUS_WON,
                DocQGame.status == GameStatus.WON,
            ),
            EmojiLegend(
                Emoji.LOG_NEGATIVE,
                phrases.GAME_STATUS_LOST,
                DocQGame.status == GameStatus.LOST,
            ),
        ]


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
        self.legend = self.get_emoji_legend()
        self.effective_status = self.legend.get_game_status()

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[Game]:
        return (
            self.object.select()
            .where(
                ((Game.challenger == self.user) | (Game.opponent == self.user))
                & (Game.status.in_(GameStatus.get_finished() + [GameStatus.IN_PROGRESS]))
                & (self.get_active_filter_list_condition())
            )  # Exclude because they don't have a type
            .order_by(Game.date.desc())
            .paginate(page, limit)
        )

    def get_item_text(self) -> str:
        return phrases.GAME_LOG_ITEM_TEXT.format(
            self.legend.get_formatted(),
            self.opponent.get_markdown_mention(),
            get_belly_formatted(self.object.wager),
        )

    def get_item_detail_text(self) -> str:
        super().get_item_detail_text()

        challenger_text = phrases.OPPONENT if self.user_is_challenger else phrases.CHALLENGER
        date = default_datetime_format(self.object.date, self.user)
        game_name = (
            GameType(self.object.type).get_name()
            if self.object.type is not None
            else phrases.GAME_NOT_SELECTED_NAME
        )

        if self.effective_status in [GameStatus.WON, GameStatus.LOST]:
            won = self.effective_status is GameStatus.WON
            outcome_text = phrases.LOG_ITEM_DETAIL_OUTCOME_TEXT.format(
                (Emoji.LOG_POSITIVE if won else Emoji.LOG_NEGATIVE),
                (phrases.TEXT_WON if won else phrases.TEXT_LOST),
                get_belly_formatted(self.object.wager),
            )
        else:
            outcome_text = phrases.LOG_ITEM_DETAIL_STATUS_TEXT.format(
                GAME_STATUS_DESCRIPTIONS[self.effective_status]
            )

        go_to_message_text = ""
        if not self.object.is_global():
            go_to_message_text = phrases.LOG_ITEM_DETAIL_GO_TO_MESSAGE.format(
                get_message_url(self.object.message_id, self.object.group_chat)
            )

        return phrases.GAME_LOG_ITEM_DETAIL_TEXT.format(
            challenger_text,
            self.opponent.get_markdown_mention(),
            game_name,
            date,
            get_belly_formatted(self.object.wager),
            outcome_text,
            get_message_url(self.object.message_id, self.object.group_chat),
            go_to_message_text,
        )

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
        most_challenged_user, most_challenged_count = self.object.get_most_challenged_user(
            self.user
        )
        most_played_game, most_played_count = self.object.get_most_played_game(self.user)

        return phrases.GAME_LOG_STATS_TEXT.format(
            total_games,
            total_wins,
            total_wins_percentage,
            total_losses,
            total_losses_percentage,
            total_draws,
            total_draws_percentage,
            get_belly_formatted(
                self.object.get_total_belly_won_or_lost(self.user, GameStatus.WON)
            ),
            get_belly_formatted(
                self.object.get_total_belly_won_or_lost(self.user, GameStatus.LOST)
            ),
            get_belly_formatted(max_won_game.wager),
            max_won_game.get_name(),
            self.get_deeplink(max_won_game.id),
            get_belly_formatted(max_lost_game.wager),
            max_lost_game.get_name(),
            self.get_deeplink(max_lost_game.id),
            most_challenged_user.get_markdown_mention(),
            most_challenged_count,
            most_played_game.get_name(),
            most_played_count,
        )

    def get_emoji_legend_list(self) -> list[EmojiLegend]:
        return [
            EmojiLegend(
                Emoji.LOG_POSITIVE,
                phrases.GAME_STATUS_WON,
                (
                    ((Game.challenger == self.user) & (Game.status == GameStatus.WON))
                    | ((Game.opponent == self.user) & (Game.status == GameStatus.LOST))
                ),
                status=GameStatus.WON,
            ),
            EmojiLegend(
                Emoji.LOG_NEGATIVE,
                phrases.GAME_STATUS_LOST,
                (
                    ((Game.opponent == self.user) & (Game.status == GameStatus.WON))
                    | ((Game.challenger == self.user) & (Game.status == GameStatus.LOST))
                ),
                status=GameStatus.LOST,
            ),
            EmojiLegend(
                Emoji.LOG_DRAW,
                phrases.GAME_STATUS_DRAW,
                (Game.status == GameStatus.DRAW),
                status=GameStatus.DRAW,
            ),
            EmojiLegend(
                Emoji.LOG_FORCED_END,
                phrases.GAME_STATUS_FORCED_END,
                (Game.status == GameStatus.FORCED_END),
                status=GameStatus.FORCED_END,
            ),
            EmojiLegend(
                Emoji.LOG_NEUTRAL,
                phrases.GAME_STATUS_IN_PROGRESS,
                (Game.status == GameStatus.IN_PROGRESS),
                status=GameStatus.IN_PROGRESS,
            ),
        ]


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

    def set_object(self, object_id: int) -> None:
        self.object: BountyGift = BountyGift.get(BountyGift.id == object_id)
        self.user_is_sender = self.object.sender == self.user
        self.other_user = self.object.receiver if self.user_is_sender else self.object.sender

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[BountyGift]:
        return (
            self.object.select()
            .where(
                ((BountyGift.sender == self.user) | (BountyGift.receiver == self.user))
                & (BountyGift.status == BountyGiftStatus.CONFIRMED)
                & (self.get_active_filter_list_condition())
            )
            .order_by(BountyGift.date.desc())
            .paginate(page, limit)
        )

    def get_item_text(self) -> str:
        to_text = phrases.TEXT_TO if self.user_is_sender else phrases.TEXT_FROM
        return phrases.BOUNTY_GIFT_LOG_ITEM_TEXT.format(
            self.get_emoji_legend_formatted(),
            get_belly_formatted(self.object.amount),
            to_text,
            self.other_user.get_markdown_mention(),
        )

    def get_item_detail_text(self) -> str:
        super().get_item_detail_text()

        sender_text = phrases.RECEIVER if self.user_is_sender else phrases.SENDER
        date = default_datetime_format(self.object.date, self.user)

        tax_text = ""
        if self.user_is_sender:
            tax_amount = int(
                get_value_from_percentage(self.object.amount, self.object.tax_percentage)
            )
            total_amount = self.object.amount + tax_amount
            tax_text = phrases.BOUNTY_GIFT_LOG_ITEM_DETAIL_TAX_TEXT.format(
                get_belly_formatted(tax_amount),
                self.object.tax_percentage,
                get_belly_formatted(total_amount),
            )

        return phrases.BOUNTY_GIFT_LOG_ITEM_DETAIL_TEXT.format(
            sender_text,
            self.other_user.get_markdown_mention(),
            date,
            get_belly_formatted(self.object.amount),
            tax_text,
            get_message_url(self.object.message_id, self.object.group_chat),
        )

    def get_stats_text(self) -> str:
        highest_sent_gift = self.object.get_highest_belly_sent_or_received(
            self.user, BountyGiftRole.SENDER
        )
        highest_sent_user, highest_sent_amount = (
            highest_sent_gift.receiver,
            highest_sent_gift.amount,
        )
        highest_received_gift = self.object.get_highest_belly_sent_or_received(
            self.user, BountyGiftRole.RECEIVER
        )
        highest_received_user, highest_received_amount = (
            highest_received_gift.sender,
            highest_received_gift.amount,
        )
        most_sent_user, most_sent_amount = self.object.get_top_givers_or_receiver(
            self.user, BountyGiftRole.SENDER
        )
        most_received_user, most_received_amount = self.object.get_top_givers_or_receiver(
            self.user, BountyGiftRole.RECEIVER
        )

        return phrases.BOUNTY_GIFT_LOG_STATS_TEXT.format(
            self.get_total_items_count(),
            get_belly_formatted(
                self.object.get_total_belly_sent_or_received(self.user, BountyGiftRole.SENDER)
            ),
            get_belly_formatted(
                self.object.get_total_belly_sent_or_received(self.user, BountyGiftRole.RECEIVER)
            ),
            get_belly_formatted(highest_sent_amount),
            highest_sent_user.get_markdown_name(),
            self.get_deeplink(highest_sent_gift.id),
            get_belly_formatted(highest_received_amount),
            highest_received_user.get_markdown_name(),
            self.get_deeplink(highest_received_gift.id),
            most_sent_user.get_markdown_mention(),
            get_belly_formatted(most_sent_amount),
            most_received_user.get_markdown_mention(),
            get_belly_formatted(most_received_amount),
        )

    def get_emoji_legend_list(self) -> list[EmojiLegend]:
        """
        Get the emoji legend list

        :return: The emoji legend list
        """

        return [
            EmojiLegend(
                Emoji.LOG_BLUE,
                phrases.BOUNTY_GIFT_LOG_LEGEND_SENT,
                BountyGift.sender == self.user,
            ),
            EmojiLegend(
                Emoji.LOG_POSITIVE,
                phrases.BOUNTY_GIFT_LOG_LEGEND_RECEIVED,
                ~(BountyGift.sender == self.user),
            ),
        ]


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

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[LegendaryPirate]:
        return self.object.select().order_by(LegendaryPirate.date.desc()).paginate(page, limit)

    def get_item_text(self) -> str:
        return phrases.LEGENDARY_PIRATE_LOG_ITEM_TEXT.format(
            mention_markdown_v2(self.user.tg_user_id, self.object.epithet)
        )

    def get_item_detail_text(self) -> str:
        super().get_item_detail_text()

        return phrases.LEGENDARY_PIRATE_LOG_ITEM_DETAIL_TEXT.format(
            self.user.get_markdown_mention(), self.object.epithet, self.object.reason
        )


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

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[User]:
        return (
            self.object.select()
            .where(
                (User.location_level >= get_first_new_world().level)
                & (User.get_is_not_arrested_statement_condition())
                & (self.get_is_admin_condition_stmt())
            )
            .order_by(User.bounty.desc())
            .paginate(page, limit)
        )

    def get_item_text(self) -> str:
        return phrases.NEW_WORLD_PIRATE_LOG_ITEM_TEXT.format(
            self.object.get_markdown_mention(), get_belly_formatted(self.object.bounty)
        )

    def get_item_detail_text(self) -> str:
        super().get_item_detail_text()

        if self.object.is_crew_member():
            crew: Crew = self.object.crew
            crew_text = phrases.NEW_WORLD_PIRATE_LOG_ITEM_DETAIL_CREW_TEXT.format(
                crew.get_name_escaped()
            )
        else:
            crew_text = ""

        return phrases.NEW_WORLD_PIRATE_LOG_ITEM_DETAIL_TEXT.format(
            self.object.get_markdown_mention(),
            get_belly_formatted(self.object.bounty),
            escape_valid_markdown_chars(self.object.get_location().name),
            crew_text,
        )


class LeaderboardRankLog(Log):
    """Class for leaderboard rank logs"""

    def __init__(self):
        """
        Constructor

        """

        super().__init__(LogType.LEADERBOARD_RANK)

        self.object: LeaderboardUser = LeaderboardUser()
        self.leaderboard: Leaderboard = Leaderboard()
        self.show_legend_list = False

    def set_object(self, object_id: int) -> None:
        self.object: LeaderboardUser = LeaderboardUser.get(LeaderboardUser.id == object_id)
        self.leaderboard: Leaderboard = self.object.leaderboard
        self.legend = self.get_emoji_legend()

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[LeaderboardUser]:
        return (
            self.object.select()
            .join(Leaderboard)
            .where(
                (LeaderboardUser.user == self.user)
                & (Leaderboard.group.is_null())
                & (self.get_active_filter_list_condition())
            )
            .order_by(LeaderboardUser.id.desc())
            .paginate(page, limit)
        )

    def get_item_text(self) -> str:
        return phrases.LEADERBOARD_RANK_LOG_ITEM_TEXT.format(
            self.leaderboard.week,
            self.leaderboard.year,
            LeaderboardRank.get_emoji_and_rank_message(get_rank_by_leaderboard_user(self.object)),
        )

    def get_item_detail_text(self) -> str:
        super().get_item_detail_text()

        return phrases.LEADERBOARD_RANK_LOG_ITEM_DETAIL_TEXT.format(
            self.leaderboard.week,
            self.leaderboard.year,
            self.object.position,
            LeaderboardRank.get_emoji_and_rank_message(get_rank_by_leaderboard_user(self.object)),
            get_belly_formatted(self.object.bounty),
        )

    def get_stats_text(self) -> str:
        total_appearances = self.get_total_items_count()
        appearances_as_pirate_king = self.object.get_appearances_as_rank(
            self.user, LeaderboardRankIndex.PIRATE_KING
        )
        appearances_as_pirate_king_percentage = int(
            get_percentage_from_value(appearances_as_pirate_king, total_appearances)
        )
        appearances_as_emperor = self.object.get_appearances_as_rank(
            self.user, LeaderboardRankIndex.EMPEROR
        )
        appearances_as_emperor_percentage = int(
            get_percentage_from_value(appearances_as_emperor, total_appearances)
        )
        appearances_as_first_mate = self.object.get_appearances_as_rank(
            self.user, LeaderboardRankIndex.FIRST_MATE
        )
        appearances_as_first_mate_percentage = int(
            get_percentage_from_value(appearances_as_first_mate, total_appearances)
        )
        appearances_as_supernova = self.object.get_appearances_as_rank(
            self.user, LeaderboardRankIndex.SUPERNOVA
        )
        appearances_as_supernova_percentage = int(
            get_percentage_from_value(appearances_as_supernova, total_appearances)
        )
        appearances_as_warlord = self.object.get_appearances_as_rank(
            self.user, LeaderboardRankIndex.WARLORD
        )
        appearances_as_warlord_percentage = int(
            get_percentage_from_value(appearances_as_warlord, total_appearances)
        )
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
            appearances_as_warlord,
            appearances_as_warlord_percentage,
            get_rank_by_leaderboard_user(max_by_rank).get_emoji_and_rank_message(),
            max_by_rank.position,
            self.get_deeplink(max_by_rank.id),
            get_belly_formatted(max_by_bounty.bounty),
            max_by_bounty.position,
            self.get_deeplink(max_by_bounty.id),
        )

    def get_emoji_legend_list(self) -> list[EmojiLegend]:
        return [
            EmojiLegend(
                Emoji.LEADERBOARD_PIRATE_KING,
                phrases.LEADERBOARD_RANK_PIRATE_KING,
                (LeaderboardUser.rank_index == LeaderboardRankIndex.PIRATE_KING),
            ),
            EmojiLegend(
                Emoji.LEADERBOARD_EMPEROR,
                phrases.LEADERBOARD_RANK_EMPEROR,
                (LeaderboardUser.rank_index == LeaderboardRankIndex.EMPEROR),
            ),
            EmojiLegend(
                Emoji.LEADERBOARD_FIRST_MATE,
                phrases.LEADERBOARD_RANK_FIRST_MATE,
                (LeaderboardUser.rank_index == LeaderboardRankIndex.FIRST_MATE),
            ),
            EmojiLegend(
                Emoji.LEADERBOARD_SUPERNOVA,
                phrases.LEADERBOARD_RANK_SUPERNOVA,
                (LeaderboardUser.rank_index == LeaderboardRankIndex.SUPERNOVA),
            ),
            EmojiLegend(
                Emoji.LEADERBOARD_WARLORD,
                phrases.LEADERBOARD_RANK_WARLORD,
                (LeaderboardUser.rank_index == LeaderboardRankIndex.WARLORD),
            ),
        ]


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

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[IncomeTaxEvent]:
        return (
            self.object.select()
            .where((IncomeTaxEvent.user == self.user))
            .order_by(IncomeTaxEvent.date.desc())
            .paginate(page, limit)
        )

    def get_item_text(self) -> str:
        return phrases.INCOME_TAX_EVENT_LOG_ITEM_TEXT.format(
            self.object.get_event_type_description(), get_belly_formatted(self.object.amount)
        )

    def get_item_detail_text(self) -> str:
        super().get_item_detail_text()

        from src.service.message_service import get_deeplink

        # Build url to event log
        event_type = self.object.get_event_type()
        log_type: LogType = event_type.get_log_type()
        event_log_url = ""

        if log_type is not None:
            event_log_url = Log.get_deeplink_by_type(log_type, self.object.event_id)
        else:
            # Manually manage events that are not shown in regular logs screen
            item_id = self.object.event_id
            match event_type:
                case IncomeTaxEventType.BOUNTY_LOAN:
                    event_log_url = get_deeplink(
                        {ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: item_id},
                        screen=Screen.PVT_BOUNTY_LOAN_DETAIL,
                    )

                case IncomeTaxEventType.PREDICTION:
                    event_log_url = get_deeplink(
                        {ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: item_id},
                        screen=Screen.PVT_PREDICTION_DETAIL,
                    )

                case IncomeTaxEventType.DAVY_BACK_FIGHT:
                    event_log_url = get_deeplink(
                        {ReservedKeyboardKeys.DEFAULT_PRIMARY_KEY: item_id},
                        screen=Screen.PVT_CREW_DAVY_BACK_FIGHT_DETAIL,
                    )

        breakdown_list = IncomeTaxBreakdown.from_string(self.object.breakdown_list)
        deduction_list = IncomeTaxDeduction.from_string(self.object.deduction_list)
        contribution_list = IncomeTaxContribution.from_string(self.object.contribution_list)

        total_tax = IncomeTaxBreakdown.get_amount_with_deduction_from_list(
            breakdown_list, deduction_list
        )
        total_tax_percentage = int(
            get_percentage_from_value(total_tax, self.object.amount, add_decimal=False)
        )
        net_income = self.object.amount - total_tax

        deduction_text = ""
        if len(deduction_list) > 0:
            deduction_text = phrases.INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_DEDUCTION
            for deduction in deduction_list:
                deduction_text += (
                    phrases.INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_DEDUCTION_ITEM.format(
                        deduction.get_description(), deduction.percentage
                    )
                )

        contribution_text = ""
        if len(contribution_list) > 0:
            contribution_text = phrases.INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_CONTRIBUTION
            for contribution in contribution_list:
                contribution_text += (
                    phrases.INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_CONTRIBUTION_ITEM.format(
                        contribution.get_description(),
                        get_belly_formatted(
                            int(get_value_from_percentage(total_tax, contribution.percentage))
                        ),
                        contribution.percentage,
                    )
                )

        breakdown_text = ""
        for breakdown in breakdown_list:
            breakdown_text += phrases.INCOME_TAX_EVENT_LOG_ITEM_DETAIL_TEXT_BREAKDOWN_ITEM.format(
                get_belly_formatted(breakdown.taxable_amount),
                get_belly_formatted(breakdown.taxable_amount - breakdown.tax_amount),
                get_belly_formatted(breakdown.tax_amount),
                int(get_percentage_from_value(breakdown.tax_amount, breakdown.taxable_amount)),
            )

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
            breakdown_text,
        )


class WarlordLog(Log):
    """Class for warlord logs"""

    def __init__(self):
        """
        Constructor

        """

        super().__init__(LogType.WARLORD, has_stats=False)

        self.object: Warlord = Warlord()
        self.user: User = User()

    def set_object(self, object_id: int) -> None:
        self.object: Warlord = Warlord.get(Warlord.id == object_id)
        self.user: User = self.object.user

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[Warlord]:
        return (
            self.object.select()
            .where(Warlord.end_date >= datetime.now())
            .order_by(Warlord.date.desc())
            .paginate(page, limit)
        )

    def get_item_text(self) -> str:
        return phrases.WARLORD_LOG_ITEM_TEXT.format(
            mention_markdown_v2(self.user.tg_user_id, self.object.epithet)
        )

    def get_item_detail_text(self) -> str:
        super().get_item_detail_text()

        return phrases.WARLORD_LOG_ITEM_DETAIL_TEXT.format(
            self.user.get_markdown_mention(), self.object.epithet, self.object.reason
        )


# noinspection DuplicatedCode
# Same as fight
class PlunderLog(Log):
    """Class for plunder logs"""

    def __init__(self):
        """
        Constructor

        """

        super().__init__(LogType.PLUNDER)

        self.object: Plunder = Plunder()
        self.opponent: User = User()
        self.user_is_challenger: bool = False
        self.effective_status: GameStatus = GameStatus.ND
        self.effective_belly = None

    def set_object(self, object_id: int) -> None:
        self.object: Plunder = Plunder.get(Plunder.id == object_id)
        self.user_is_challenger = self.object.challenger == self.user
        self.opponent = self.object.get_opponent(self.user)
        self.legend = self.get_emoji_legend()
        self.effective_status = self.legend.get_game_status()

        if self.object.get_status() is GameStatus.LOST:
            self.effective_belly = self.object.get_loan().repay_amount
        else:
            self.effective_belly = self.object.belly

    def get_items(self, page, limit=ListPage.DEFAULT_LIMIT) -> list[Plunder]:
        return (
            self.object.select()
            .where(
                ((Plunder.challenger == self.user) | (Plunder.opponent == self.user))
                & (Plunder.status.in_([GameStatus.WON, GameStatus.LOST]))
                & (self.get_active_filter_list_condition())
            )
            .order_by(Plunder.date.desc())
            .paginate(page, limit)
        )

    def get_item_text(self) -> str:
        return phrases.PLUNDER_LOG_ITEM_TEXT.format(
            self.legend.get_formatted(),
            self.opponent.get_markdown_mention(),
            get_belly_formatted(self.effective_belly),
        )

    def get_item_detail_text(self) -> str:
        super().get_item_detail_text()

        challenger_text = phrases.OPPONENT if self.user_is_challenger else phrases.CHALLENGER
        date = default_datetime_format(self.object.date, self.user)

        if self.effective_status in [GameStatus.WON, GameStatus.LOST]:
            if not self.user_is_challenger and self.effective_status is GameStatus.WON:
                loan = self.object.get_loan()
                outcome_text = phrases.PLUNDER_LOG_ITEM_DETAIL_TEXT_WON_LOAN.format(
                    get_belly_formatted(self.effective_belly), loan.get_deeplink()
                )
            else:
                if self.user_is_challenger:
                    inner_text = (
                        phrases.TEXT_STOLE
                        if self.effective_status is GameStatus.WON
                        else phrases.TEXT_OWE.format(self.object.get_loan().get_deeplink())
                    )
                else:
                    inner_text = phrases.TEXT_LOST

                outcome_text = phrases.LOG_ITEM_DETAIL_OUTCOME_BELLY_TEXT.format(
                    self.legend.get_formatted(),
                    inner_text,
                    get_belly_formatted(self.object.belly),
                )
        else:
            outcome_text = phrases.LOG_ITEM_DETAIL_STATUS_TEXT.format(
                GAME_STATUS_DESCRIPTIONS[self.effective_status]
            )

        if self.effective_status is GameStatus.LOST and self.user_is_challenger:
            outcome_text += phrases.PLUNDER_LOG_ITEM_DETAIL_SENTENCE_DURATION.format(
                convert_hours_to_duration(self.object.sentence_duration, show_full=True)
            )

        go_to_message_text = ""
        if self.object.group_chat is not None:
            go_to_message_text = phrases.LOG_ITEM_DETAIL_GO_TO_MESSAGE.format(
                get_message_url(self.object.message_id, self.object.group_chat)
            )

        ot_text = phrases.PLUNDER_LOG_ITEM_DETAIL_TEXT.format(
            challenger_text,
            self.opponent.get_markdown_mention(),
            date,
            self.object.get_win_probability(self.user),
            outcome_text,
            go_to_message_text,
        )

        # Plunder still revengable
        if self.object.can_revenge(self.user):
            ot_text += phrases.PLUNDER_ATTACK_CAN_REVENGE.format(
                self.object.get_revenge_remaining_duration()
            )
        # Was in response to a previous attack
        elif self.object.in_revenge_to_plunder is not None:
            ot_text += phrases.PLUNDER_LOG_ITEM_DETAIL_TEXT_IN_RESPONSE.format(
                Log.get_deeplink_by_type(LogType.PLUNDER, self.object.in_revenge_to_plunder.id)
            )
        # Has been revenged
        if revenge_plunder := self.object.get_revenge_plunder():
            ot_text += phrases.PLUNDER_LOG_ITEM_DETAIL_TEXT_REVENGED.format(
                Log.get_deeplink_by_type(LogType.PLUNDER, revenge_plunder.id)
            )

        return ot_text

    def get_stats_text(self) -> str:
        total_plunders = self.get_total_items_count()
        total_wins = self.object.get_total_win_or_loss(self.user, GameStatus.WON)
        total_wins_percentage = int(get_percentage_from_value(total_wins, total_plunders))
        total_losses = self.object.get_total_win_or_loss(self.user, GameStatus.LOST)
        total_losses_percentage = int(get_percentage_from_value(total_losses, total_plunders))
        max_won_plunder = self.object.get_max_won_or_lost(self.user, GameStatus.WON)
        max_lost_plunder = self.object.get_max_won_or_lost(self.user, GameStatus.LOST)
        most_plundered_user, most_plundered_count = self.object.get_most_plundered_user(self.user)
        max_sentence = self.object.get_max_sentence(self.user)
        return phrases.PLUNDER_LOG_STATS_TEXT.format(
            total_plunders,
            total_wins,
            total_wins_percentage,
            total_losses,
            total_losses_percentage,
            get_belly_formatted(
                self.object.get_total_belly_won_or_lost(self.user, GameStatus.WON)
            ),
            get_belly_formatted(
                self.object.get_total_belly_won_or_lost(self.user, GameStatus.LOST)
            ),
            get_belly_formatted(max_won_plunder.belly),
            max_won_plunder.get_opponent(self.user).get_markdown_mention(),
            self.get_deeplink(max_won_plunder.id),
            get_belly_formatted(max_lost_plunder.belly),
            max_lost_plunder.get_opponent(self.user).get_markdown_mention(),
            self.get_deeplink(max_lost_plunder.id),
            convert_hours_to_duration(self.object.sentence_duration, show_full=True),
            self.get_deeplink(max_sentence.id),
            most_plundered_user.get_markdown_mention(),
            most_plundered_count,
        )

    def get_emoji_legend_list(self) -> list[EmojiLegend]:
        return [
            EmojiLegend(
                Emoji.LOG_POSITIVE,
                phrases.GAME_STATUS_WON,
                (
                    ((Plunder.challenger == self.user) & (Plunder.status == GameStatus.WON))
                    | ((Plunder.opponent == self.user) & (Plunder.status == GameStatus.LOST))
                ),
                status=GameStatus.WON,
            ),
            EmojiLegend(
                Emoji.LOG_NEGATIVE,
                phrases.GAME_STATUS_LOST,
                (
                    ((Plunder.opponent == self.user) & (Plunder.status == GameStatus.WON))
                    | ((Plunder.challenger == self.user) & (Plunder.status == GameStatus.LOST))
                ),
                status=GameStatus.LOST,
            ),
        ]

    def get_keyboard(self) -> list[list[Keyboard]]:
        # Return the revenge button
        if not self.object.can_revenge(self.user):
            return []

        return [
            [
                Keyboard(
                    phrases.PVT_KEY_PLUNDER_REVENGE,
                    screen=Screen.PVT_PLUNDER,
                    info={
                        ReservedKeyboardKeys.CONFIRM: 1,
                        FightPlunderReservedKeys.OPPONENT_ID: self.object.challenger.id,
                        FightPlunderReservedKeys.IN_REVENGE_TO_ATTACK_ID: self.object.id,
                    },
                )
            ]
        ]


LOGS = [
    FightLog(),
    DocQGameLog(),
    GameLog(),
    BountyGiftLog(),
    LegendaryPirateLog(),
    NewWorldPirateLog(),
    LeaderboardRankLog(),
    IncomeTaxEventLog(),
    WarlordLog(),
    PlunderLog(),
]


def get_log_by_type(log_type: LogType) -> Log:
    """
    Get a notification by type

    :param log_type: The type of log
    :return: The notification
    """

    log: Log = next(log for log in LOGS if log.type is log_type)

    # Need to re-initialize the class since it would be initialized only once on program start, and it would keep in
    # memory items like filters each user
    # noinspection PyArgumentList
    log.__init__()

    return log
