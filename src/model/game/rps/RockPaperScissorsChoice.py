from enum import IntEnum


class RockPaperScissorsChoice(IntEnum):
    """
    Enum for the choices a Rock Paper Scissors.
    """

    NONE = 0
    ROCK = 1
    PAPER = 2
    SCISSORS = 3

    def get_losing_choice(self) -> "RockPaperScissorsChoice":
        """
        Get the choice that loses to this
        :return: The losing choice
        """

        if self == RockPaperScissorsChoice.ROCK:
            return RockPaperScissorsChoice.SCISSORS

        if self == RockPaperScissorsChoice.PAPER:
            return RockPaperScissorsChoice.ROCK

        if self == RockPaperScissorsChoice.SCISSORS:
            return RockPaperScissorsChoice.PAPER

        raise ValueError("Invalid choice")
