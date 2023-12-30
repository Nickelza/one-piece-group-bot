import json
import random

from src.model.Game import Game
from src.model.User import User
from src.model.game.GameOutcome import GameOutcome
from src.model.game.GameTurn import GameTurn
from src.model.game.russianroulette.RussianRouletteChamberStatus import (
    RussianRouletteChamberStatus as RRChamberStatus,
)


class RussianRoulette:
    def __init__(
        self,
        rows: int = 3,
        columns: int = 3,
        cylinder: list = None,
        bullet_x: int = -1,
        bullet_y: int = -1,
        game_turn: GameTurn = GameTurn.CHALLENGER,
    ):
        self.rows = rows
        self.columns = columns
        self.cylinder: list[[RRChamberStatus]] = (
            cylinder
            if cylinder is not None
            else [
                [RRChamberStatus.NOT_FIRED for _ in range(self.columns)] for _ in range(self.rows)
            ]
        )
        self.bullet_x: int = bullet_x
        self.bullet_y: int = bullet_y
        self.game_turn: GameTurn = (
            GameTurn(game_turn) if not isinstance(game_turn, GameTurn) else game_turn
        )

        # Initialize only on first creation, not json loading
        if self.bullet_x == -1 or self.bullet_y == -1:
            self.set_bullet_position()

    def set_bullet_position(self) -> None:
        """
        Sets the bullet position
        """

        while True:
            x = random.randint(0, self.rows - 1)
            y = random.randint(0, self.columns - 1)

            # If coordinates are not the center, use them
            if x != self.rows // 2 or y != self.columns // 2:
                self.bullet_x = x
                self.bullet_y = y
                break

    def is_finished(self) -> bool:
        """
        Returns if the game is finished. The game is finished when all but one chamber is fired, except for the center
        :return: GameTurn
        """

        if self.bullet_is_fired():
            return True

        not_fired_count = 0
        for row_index, row in enumerate(self.cylinder):
            for chamber_index, chamber in enumerate(row):
                if chamber == RRChamberStatus.NOT_FIRED and not self.is_chamber_center(
                    row_index, chamber_index
                ):
                    not_fired_count += 1

        return not_fired_count == 1

    def bullet_is_fired(self) -> bool:
        """
        Returns if the bullet is fired
        :return: bool
        """

        return self.get_bullet_chamber_status() == RRChamberStatus.FIRED

    def get_bullet_chamber_status(self) -> RRChamberStatus:
        """
        Returns the bullet chamber status
        :return: RRChamberStatus
        """

        return self.cylinder[self.bullet_x][self.bullet_y]

    def get_board_json(self) -> str:
        """
        Returns the board as a json string
        :return: string
        """

        return json.dumps(self.__dict__)

    def set_turn(self):
        """
        Sets the turn
        """

        self.game_turn = (
            GameTurn.CHALLENGER if self.game_turn is GameTurn.OPPONENT else GameTurn.OPPONENT
        )

    def get_outcome(self) -> GameOutcome:
        """
        Returns the outcome of the game
        :return: GameTurn
        """

        if not self.is_finished():
            return GameOutcome.NONE

        if self.bullet_is_fired():
            if self.game_turn == GameTurn.CHALLENGER:
                return GameOutcome.OPPONENT_WON
            else:
                return GameOutcome.CHALLENGER_WON

        return GameOutcome.DRAW

    def is_user_turn(self, user: User, game: Game) -> bool:
        """
        Returns if the user is the turn
        :param user: User
        :param game: Game
        :return: bool
        """

        if self.game_turn is GameTurn.CHALLENGER:
            return user == game.challenger
        else:
            return user == game.opponent

    def get_user_turn(self, game: Game) -> User:
        """
        Returns the user turn
        :param game: The game
        :return: User
        """

        if self.game_turn == GameTurn.CHALLENGER:
            return game.challenger

        return game.opponent

    def is_chamber_center(self, x: int, y: int) -> bool:
        """
        Returns if the chamber is the center
        :param x: int
        :param y: int
        :return: bool
        """

        return x == self.rows // 2 and y == self.columns // 2
