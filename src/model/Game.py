import datetime
import json

from peewee import *

import resources.Environment as Env
from resources import phrases
from src.model.BaseModel import BaseModel
from src.model.GroupChat import GroupChat
from src.model.User import User
from src.model.enums.GameStatus import GameStatus
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.game.GameBoard import GameBoard
from src.model.game.GameDifficulty import GameDifficulty
from src.model.game.GameOutcome import GameOutcome
from src.model.game.GameType import GameType
from src.model.wiki.Character import Character
from src.model.wiki.Terminology import Terminology
from src.utils.string_utils import get_belly_formatted


class Game(BaseModel):
    """
    Game class
    """

    challenger: User | ForeignKeyField = ForeignKeyField(
        User, backref="game_challengers", on_delete="CASCADE", on_update="CASCADE"
    )
    opponent: User | ForeignKeyField = ForeignKeyField(
        User, backref="game_opponents", on_delete="CASCADE", on_update="CASCADE", null=True
    )
    type: GameType | SmallIntegerField = SmallIntegerField(null=True)
    board: str | CharField = CharField(max_length=9999, null=True)
    opponent_board: str | CharField = CharField(max_length=9999, null=True)
    status: GameStatus | SmallIntegerField = SmallIntegerField(
        default=GameStatus.AWAITING_SELECTION
    )
    group_chat: GroupChat | ForeignKeyField = ForeignKeyField(
        GroupChat,
        null=True,
        backref="game_groups_chats",
        on_delete="RESTRICT",
        on_update="CASCADE",
    )
    message_id: int | IntegerField = IntegerField(null=True)
    challenger_message_id: int | IntegerField = IntegerField(null=True)
    opponent_message_id: int | IntegerField = IntegerField(null=True)
    wager: int | BigIntegerField = BigIntegerField(null=True)
    last_interaction_date: datetime.datetime | DateTimeField = DateTimeField(
        default=datetime.datetime.now
    )
    global_challenger_start_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    global_challenger_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    global_opponent_start_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    global_opponent_end_date: datetime.datetime | DateTimeField = DateTimeField(null=True)
    global_challenger_has_finished: bool | BooleanField = BooleanField(default=False)
    last_hint_date = DateTimeField(null=True)
    last_hint_opponent_date = DateTimeField(null=True)
    thread_restart_count = IntegerField(default=0)

    class Meta:
        db_table = "game"

    def is_player(self, user: User) -> bool:
        """
        Check if the user is a player of the game
        :param user: The user
        :return: True if the user is a player, False otherwise
        """

        return self.challenger == user or self.opponent == user

    def get_saved_media_name(self) -> SavedMediaName:
        """
        Get the SavedMediaName for this GameType
        :return: The SavedMediaName
        """
        return GameType(self.type).get_saved_media_name()

    def get_difficulty(self) -> GameDifficulty:
        """
        Get the difficulty level of the game
        :return: The difficulty level
        """

        return GameDifficulty.get_from_total_wager(int(str(self.wager)))

    def get_name(self) -> str:
        """
        Get the name of the game
        :return: The name
        """

        return GameType(self.type).get_name()

    @staticmethod
    def get_total_win_or_loss_or_draw(user: User, status: GameStatus) -> int:
        """
        Get the total amount of wins or losses or draws a user has
        param user: The user
        param status: The status (won or lost or draw)
        return: The total amount of wins or losses or draws
        """

        if status in (GameStatus.WON, GameStatus.LOST):
            return (
                Game().select().where((Game.challenger == user) & (Game.status == status)).count()
                + Game()
                .select()
                .where((Game.opponent == user) & (Game.status == status.get_opposite_status()))
                .count()
            )

        return Game().select().where((Game.challenger == user) & (Game.status == status)).count()

    @staticmethod
    def get_total_belly_won_or_lost(user: User, status: GameStatus) -> int:
        """
        Get the total amount of belly a user has won or lost
        param user: The user
        param status: The status (won or lost)
        return: The total amount of belly
        """

        return (
            Game.select(fn.SUM(Game.wager)).where(
                (Game.challenger == user) & (Game.status == status)
            )
        ).scalar() + (
            Game.select(fn.SUM(Game.wager)).where(
                (Game.opponent == user) & (Game.status == status.get_opposite_status())
            )
        ).scalar()

    @staticmethod
    def get_max_won_or_lost(user: User, status: GameStatus) -> "Game":
        """
        Get the game with the max belly won or lost
        param user: The user
        param status: The status (won or lost)
        return: The game
        """

        # Max game as challenger
        max_game_as_challenger: Game = (
            Game()
            .select()
            .where((Game.challenger == user) & (Game.status == status))
            .order_by(Game.wager.desc())
            .first()
        )

        # Max game as opponent
        max_game_as_opponent: Game = (
            Game()
            .select()
            .where((Game.opponent == user) & (Game.status == status.get_opposite_status()))
            .order_by(Game.wager.desc())
            .first()
        )

        if max_game_as_challenger is None:
            return max_game_as_opponent

        if max_game_as_opponent is None:
            return max_game_as_challenger

        if max_game_as_challenger.wager > max_game_as_opponent.wager:
            return max_game_as_challenger

        return max_game_as_opponent

    @staticmethod
    def get_most_challenged_user(user: User) -> (User, int):
        """
        Get the most challenged user and the amount of games
        param user: The user
        return: The most challenged user and the amount of games
        """

        # noinspection DuplicatedCode
        most_challenged_user_as_challenger = (
            Game.select(Game.opponent, fn.COUNT(Game.opponent).alias("count"))
            .where(Game.challenger == user)
            .group_by(Game.opponent)
            .order_by(SQL("count").desc())
            .first()
        )
        amount_as_challenger = most_challenged_user_as_challenger.count

        most_challenged_user_as_opponent = (
            Game.select(Game.challenger, fn.COUNT(Game.challenger).alias("count"))
            .where(Game.opponent == user)
            .group_by(Game.challenger)
            .order_by(SQL("count").desc())
            .first()
        )
        amount_as_opponent = most_challenged_user_as_opponent.count

        if amount_as_challenger > amount_as_opponent:
            return most_challenged_user_as_challenger.opponent, amount_as_challenger

        return most_challenged_user_as_opponent.challenger, amount_as_opponent

    @staticmethod
    def get_most_played_game(user: User) -> (GameType, int):
        """
        Get the most played game and the amount of games
        param user: The user
        return: The most played game and the amount of games
        """

        # noinspection DuplicatedCode
        most_played_as_challenger = (
            Game.select(Game.type, fn.COUNT(Game.type).alias("count"))
            .where(Game.challenger == user)
            .group_by(Game.type)
            .order_by(SQL("count").desc())
            .first()
        )
        amount_as_challenger = most_played_as_challenger.count

        most_played_as_opponent = (
            Game.select(Game.type, fn.COUNT(Game.type).alias("count"))
            .where(Game.opponent == user)
            .group_by(Game.type)
            .order_by(SQL("count").desc())
            .first()
        )
        amount_as_opponent = most_played_as_opponent.count

        if amount_as_challenger > amount_as_opponent:
            return GameType(most_played_as_challenger.type), amount_as_challenger

        return GameType(most_played_as_opponent.type), amount_as_opponent

    def get_type(self) -> GameType:
        """
        Get the GameType
        :return: The GameType
        """
        return GameType(self.type)

    def get_status(self) -> GameStatus:
        """
        Get the status of the game
        :return: The status of the game
        """

        return GameStatus(self.status)

    def get_players(self) -> list[User]:
        """
        Get the players
        :return: The players
        """

        return [self.challenger, self.opponent]

    def is_global(self) -> bool:
        """
        Check if the game is global
        :return: True if the game is global, False otherwise
        """

        return self.global_challenger_start_date is not None

    @staticmethod
    def get_global_games() -> list["Game"]:
        """
        Get all global games that are in progress and an opponent has not being found yet,
        first those of which the challenger has finished, then oldest
        :return: The global games
        """

        return (
            Game.select()
            .where(
                (
                    Game.global_challenger_start_date.is_null(False)
                    & (Game.global_opponent_start_date.is_null())
                    & (Game.status == GameStatus.IN_PROGRESS)
                )
            )
            .order_by(
                Game.global_challenger_has_finished.desc(), Game.global_challenger_start_date
            )
        )

    def get_wager_formatted(self) -> str:
        """
        Get the formatted wager
        :return: The formatted wager
        """

        return get_belly_formatted(self.wager)

    def get_half_wager_formatted(self) -> str:
        """
        Get the formatted half wager
        :return: The formatted half wager
        """

        return get_belly_formatted(self.wager // 2)

    def is_challenger(self, user: User) -> bool:
        """
        Check if the user is the challenger
        :param user: The user
        :return: True if the user is the challenger, False otherwise
        """

        return user == self.challenger

    def is_opponent(self, user: User) -> bool:
        """
        Check if the user is the opponent
        :param user: The user
        :return: True if the user is the opponent, False otherwise
        """

        return not self.is_challenger(user)

    def get_other_player(self, user: User) -> User:
        """
        Get the other player
        :param user: The user
        :return: The other player
        """

        if self.is_challenger(user):
            return self.opponent

        return self.challenger

    def get_winner(self) -> User | None:
        """
        Get the winner of the game
        :return: The winner
        """

        if self.get_status() is GameStatus.WON:
            return self.challenger

        if self.get_status() is GameStatus.LOST:
            return self.opponent

        return None

    def has_winner(self) -> bool:
        """
        Check if the game has a winner
        :return: True if the game has a winner, False otherwise
        """

        return self.get_winner() is not None

    def get_outcome(self) -> GameOutcome:
        """
        Get the outcome of the game
        :return: The outcome
        """

        if self.get_status() is GameStatus.WON:
            return GameOutcome.CHALLENGER_WON

        if self.get_status() is GameStatus.LOST:
            return GameOutcome.OPPONENT_WON

        if self.get_status() is GameStatus.DRAW:
            return GameOutcome.DRAW

        return GameOutcome.NONE

    def is_finished(self) -> bool:
        """
        Check if the game is finished
        :return: True if the game is finished, False otherwise
        """

        return self.get_status().is_finished()

    def set_board(self, board: GameBoard, user: User) -> None:
        """
        Set the board for the user
        :param board: The game board
        :param user: The user
        :return: None
        """

        if self.is_challenger(user) or not self.is_global():
            self.board = board.get_as_json_string()
        else:
            self.opponent_board = board.get_as_json_string()

    def is_turn_based(self) -> bool:
        """
        Check if the game is turn based
        :return: True if the game is turn based, False otherwise
        """

        return self.get_type().is_turn_based()

    def is_guess_based(self) -> bool:
        """
        Check if the game is time based
        :return: True if the game is time based, False otherwise
        """

        return self.get_type().is_guess_based()

    def has_opponent(self) -> bool:
        """
        Check if the game has an opponent
        :return: True if the game has an opponent, False otherwise
        """

        return self.opponent is not None

    def get_players_time_seconds(self) -> [int, int]:
        """
        Get the players time in seconds
        :return: The players time in seconds
        """

        from src.service.date_service import get_remaining_time_in_seconds

        challenger_total_time_seconds = get_remaining_time_in_seconds(
            (
                self.global_challenger_end_date
                if self.global_challenger_end_date
                else datetime.datetime.now()
            ),
            start_datetime=self.global_challenger_start_date,
        )

        opponent_total_time_seconds = get_remaining_time_in_seconds(
            (
                self.global_opponent_end_date
                if self.global_opponent_end_date
                else datetime.datetime.now()
            ),
            start_datetime=self.global_opponent_start_date,
        )

        return challenger_total_time_seconds, opponent_total_time_seconds

    def challenger_has_finished(self) -> bool:
        """
        Check if the challenger has finished
        :return: True if the challenger has finished, False otherwise
        """

        return self.is_global() and (
            self.global_challenger_end_date is not None or self.is_finished()
        )

    def opponent_has_finished(self) -> bool:
        """
        Check if the opponent has finished
        :return: True if the opponent has finished, False otherwise
        """

        return self.is_global() and (
            self.global_opponent_end_date is not None or self.is_finished()
        )

    def get_challenger_time_seconds(self) -> int:
        """
        Get the challenger time in seconds
        :return: The challenger time in seconds
        """

    def get_seconds_for_every_hint(self) -> int:
        """
        Get the seconds for every hint
        :return: The seconds for every hint
        """

        match self.get_type():
            case GameType.GUESS_OR_LIFE:
                return Env.GUESS_OR_LIFE_NEW_LIFE_WAIT_TIME.get_int()

            case GameType.PUNK_RECORDS:
                return Env.PUNK_RECORDS_NEXT_DETAIL_WAIT_TIME.get_int()

            case GameType.SHAMBLES:
                return Env.SHAMBLES_NEXT_LEVEL_WAIT_TIME.get_int()

            case GameType.WHOS_WHO:
                return Env.WHOS_WHO_NEXT_LEVEL_WAIT_TIME.get_int()

            case _:
                raise ValueError(f"Unsupported game type: {self.get_type()}")

    def get_terminology(self) -> Terminology:
        """
        Get the terminology from the game
        :return: The terminology
        """

        # Parse the JSON string and create a Terminology object
        json_dict = json.loads(self.board)
        if "terminology" in json_dict:
            term_dict = json_dict.pop("terminology")
            terminology: Terminology = Terminology(**term_dict)
        elif "character" in json_dict:
            char_dict = json_dict.pop("character")
            terminology: Terminology = Character(**char_dict)
        else:
            raise ValueError("No terminology or character in JSON string")

        return terminology

    def get_global_item_text(self) -> str:
        """
        Get the global item text
        :return: The global item text
        """

        return phrases.GAME_GLOBAL_ITEM_TEXT.format(
            self.get_type().get_name(), self.get_wager_formatted()
        )


Game.create_table()
