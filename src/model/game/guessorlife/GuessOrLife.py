import re
from enum import IntEnum

import resources.Environment as Env
from src.model.game.GameBoard import GameBoard
from src.model.game.GameDifficulty import GameDifficulty
from src.model.game.GameOutcome import GameOutcome
from src.model.wiki.Terminology import Terminology


class PlayerInfo:
    def __init__(self, lives: int, used_letters: list[str] = None):
        self.used_letters = used_letters
        self.lives = lives

        if self.used_letters is None:
            self.used_letters = []


class PlayerType(IntEnum):
    CHALLENGER = 1
    OPPONENT = 2


class GuessOrLife(GameBoard):
    def __init__(
        self,
        terminology: Terminology,
        challenger_info: PlayerInfo = None,
        opponent_info: PlayerInfo = None,
        issued_lives: int = None,
    ):
        """
        Constructor
        :param terminology: The terminology
        :param challenger_info: The challenger info
        :param opponent_info: The opponent info
        :param issued_lives: The issued lives
        """
        super().__init__()

        self.terminology = terminology
        self.challenger_info = challenger_info
        self.opponent_info = opponent_info
        self.issued_lives = issued_lives

        if self.issued_lives is None:
            self.issued_lives = Env.GUESS_OR_LIFE_STARTING_LIVES.get_int()

        if self.challenger_info is None:
            self.challenger_info = PlayerInfo(self.issued_lives)

        if self.opponent_info is None:
            self.opponent_info = PlayerInfo(self.issued_lives)

    def get_plain_word(self) -> str:
        """
        Get the plain word, without special characters
        :return: str
        """

        return re.sub(r"\W", "", self.terminology.name)

    def has_used_letter(self, player_type: PlayerType, letter: str) -> bool:
        """
        Check if the player has used a letter
        :param player_type: The player
        :param letter: The letter
        :return: bool
        """

        if player_type == PlayerType.CHALLENGER:
            return letter.lower() in self.challenger_info.used_letters
        else:
            return letter.lower() in self.opponent_info.used_letters

    def is_letter_is_in_word(self, letter: str) -> bool:
        """
        Check if the letter is in the word
        :param letter: The letter
        :return: bool
        """

        return letter.lower() in self.get_plain_word().lower()

    def is_finished(self, player_type: PlayerType, other_board: "GuessOrLife" = None) -> bool:
        """
        Check if the game is finished
        :param player_type: The player type, challenger by default because in case it's not passed (so global board),
        then it will always be the challenger in both boards
        :param other_board: The other board, in case of global game
        :return: bool
        """

        if other_board is not None:  # Global mode
            # Current player is challenger, the game can't be finished because even if they have guessed, the fact that
            # they arrived to this point instead of being stopped earlier means that the opponent is still playing
            if player_type is PlayerType.CHALLENGER:
                return False

        return self.player_has_guessed(player_type)

    def player_has_guessed(self, player_type: PlayerType):
        """
        :param player_type: The player
        :return:
        """

        player_info = self.get_player_info(player_type)

        for letter in self.get_plain_word():
            if letter.lower() not in player_info.used_letters:
                return False

        return True

    def get_outcome(self, player_type: PlayerType) -> GameOutcome:
        """
        Get the outcome
        :return: str
        """

        if not self.is_finished(player_type):
            raise ValueError("Game is not finished")

        if player_type is PlayerType.CHALLENGER:
            return GameOutcome.CHALLENGER_WON

        return GameOutcome.OPPONENT_WON

    def get_player_info(self, player_type) -> PlayerInfo:
        """
        Get the player info
        :param player_type: The player
        :return:
        """

        if player_type == PlayerType.CHALLENGER:
            return self.challenger_info

        return self.opponent_info

    def can_issue_life(self):
        """
        Check if a live can be issued
        :return: bool
        """

        return self.issued_lives < 26

    def issue_life(self):
        """
        Issue a live
        :return: None
        """

        if not self.can_issue_life():
            raise ValueError("Cannot issue live")

        self.challenger_info.lives += 1
        self.opponent_info.lives += 1
        self.issued_lives += 1

    def get_used_letters_formatted(self, player_type: PlayerType):
        """
        Get the used letters formatted
        :param player_type: The player
        :return: str
        """

        if player_type is PlayerType.CHALLENGER:
            letters: list[str] = self.challenger_info.used_letters
        else:
            letters: list[str] = self.opponent_info.used_letters

        # Order the letters
        letters.sort()

        return str(", ".join(letters)).upper()

    def get_remaining_letters(self, player_type: PlayerType):
        """
        Get the remaining letters
        :param player_type: The player
        :return: str
        """

        used_letters = self.get_used_letters_formatted(player_type)
        return ", ".join(
            [chr(i) for i in range(ord("A"), ord("Z") + 1) if chr(i) not in used_letters]
        )

    def get_word_with_blanks(self, player_type: PlayerType, show_guessed_letters: bool = True):
        """
        Get the word with blanks
        :param player_type: The player
        :param show_guessed_letters: Show guessed letters
        :return: str
        """

        word = ""
        word_list = []
        letter_template = " {} "

        for index, letter in enumerate(self.terminology.name):
            # Guessed, show letter
            letter_to_append = letter
            if letter.lower() in self.get_player_info(player_type).used_letters:
                word += (
                    letter_template.format(letter)
                    if show_guessed_letters
                    else letter_template.format("*")
                )
            # Space, show space
            elif letter == " ":
                word += letter_template.format(letter)
            # Not guessed, but it's a special character and the character before it is guessed, show letter
            elif (
                letter.isalpha() is False and len(word_list) > 0 and word_list[index - 1].isalpha()
            ):
                word += (
                    letter_template.format(letter)
                    if show_guessed_letters
                    else letter_template.format("*")
                )
            # Not guessed, show blank
            else:
                word += letter_template.format("_")
                letter_to_append = "_"

            word_list.append(letter_to_append)

        return word.upper()

    def add_used_letter(self, player_type: PlayerType, letter: str):
        """
        Add a used letter
        :param player_type: The player
        :param letter: The letter
        :return: None
        """

        if player_type == PlayerType.CHALLENGER:
            self.challenger_info.used_letters.append(letter.lower())
        else:
            self.opponent_info.used_letters.append(letter.lower())

    def remove_life(self, player_type: PlayerType):
        """
        Remove a life
        :param player_type: The player
        :return: None
        """

        if player_type == PlayerType.CHALLENGER:
            self.challenger_info.lives -= 1
        else:
            self.opponent_info.lives -= 1

    @staticmethod
    def get_max_unique_characters_by_difficulty(difficulty: GameDifficulty) -> int or None:
        """
        Get the max unique characters by difficulty
        :param difficulty: The difficulty
        :return: int
        """

        match difficulty:
            case GameDifficulty.EASY:
                return Env.GUESS_OR_LIFE_MAX_UNIQUE_CHARACTERS_EASY.get_int()

            case GameDifficulty.MEDIUM:
                return Env.GUESS_OR_LIFE_MAX_UNIQUE_CHARACTERS_MEDIUM.get_int()

            case GameDifficulty.HARD:
                return None

            case _:
                raise ValueError("Invalid difficulty")

    @staticmethod
    def get_min_unique_characters_by_difficulty(difficulty: GameDifficulty) -> int or None:
        """
        Get the min unique characters by difficulty
        :param difficulty: The difficulty
        :return: int
        """

        match difficulty:
            case GameDifficulty.EASY:
                return None

            case GameDifficulty.MEDIUM:
                return Env.GUESS_OR_LIFE_MAX_UNIQUE_CHARACTERS_EASY.get_int() + 1

            case GameDifficulty.HARD:
                return Env.GUESS_OR_LIFE_MAX_UNIQUE_CHARACTERS_MEDIUM.get_int() + 1

            case _:
                raise ValueError("Invalid difficulty")
