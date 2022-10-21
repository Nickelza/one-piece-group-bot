import json

from src.model.game.GameOutcome import GameOutcome
from src.model.game.GameTurn import GameTurn
from src.model.game.rps.RockPaperScissorsChoice import RockPaperScissorsChoice as RPSChoice


class RockPaperScissors:
    def __init__(self, game_turn: GameTurn = GameTurn.CHALLENGER, challenger_choice: RPSChoice = RPSChoice.NONE,
                 opponent_choice: RPSChoice = RPSChoice.NONE):
        self.game_turn = game_turn
        self.challenger_choice: RPSChoice = challenger_choice
        self.opponent_choice: RPSChoice = opponent_choice

    def is_finished(self) -> bool:
        """
        Returns the turn of the game
        :return: GameTurn
        """

        return self.challenger_choice != RPSChoice.NONE and self.opponent_choice != RPSChoice.NONE

    def get_outcome(self) -> GameOutcome:
        """
        Returns the outcome of the game
        :return: GameOutcome
        """

        if not self.is_finished():
            return GameOutcome.NONE

        if self.challenger_choice == self.opponent_choice:
            return GameOutcome.DRAW

        if self.challenger_choice == RPSChoice.ROCK and self.opponent_choice == RPSChoice.SCISSORS:
            return GameOutcome.CHALLENGER_WON

        if self.challenger_choice == RPSChoice.PAPER and self.opponent_choice == RPSChoice.ROCK:
            return GameOutcome.CHALLENGER_WON

        if self.challenger_choice == RPSChoice.SCISSORS and self.opponent_choice == RPSChoice.PAPER:
            return GameOutcome.CHALLENGER_WON

        return GameOutcome.OPPONENT_WON

    def get_board_json(self) -> str:
        """
        Returns the board as a json string
        :return: string
        """

        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True)

    def set_turn(self):
        """
        Sets the turn
        """

        self.game_turn = GameTurn.CHALLENGER if self.game_turn is GameTurn.OPPONENT else GameTurn.OPPONENT
