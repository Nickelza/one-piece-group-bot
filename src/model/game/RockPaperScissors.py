import json

from src.model.game.GameOutcome import GameOutcome
from src.model.game.GameTurn import GameTurn
from src.model.game.RockPaperScissorsChoice import RockPaperScissorsChoice as RPSChoice


class RockPaperScissors:
    def __init__(self, challenger_choice: RPSChoice = RPSChoice.NONE, opponent_choice: RPSChoice = RPSChoice.NONE):
        self.challenger_choice: RPSChoice = challenger_choice
        self.opponent_choice: RPSChoice = opponent_choice

    def get_turn(self) -> GameTurn:
        """
        Returns the turn of the game
        :return: GameTurn
        """
        if self.challenger_choice == RPSChoice.NONE:
            return GameTurn.CHALLENGER
        elif self.opponent_choice == RPSChoice.NONE:
            return GameTurn.OPPONENT
        else:
            return GameTurn.FINISHED

    def get_outcome(self) -> GameOutcome:
        """
        Returns the outcome of the game
        :return: GameOutcome
        """

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

        return json.dumps(self.__dict__)
