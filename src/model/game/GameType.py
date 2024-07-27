from enum import IntEnum

import resources.Environment as Env
from resources import phrases
from src.model.enums.SavedMediaName import SavedMediaName


class GameType(IntEnum):
    """
    Enum for the game type
    """

    ROCK_PAPER_SCISSORS = 1
    RUSSIAN_ROULETTE = 2
    WHOS_WHO = 3
    SHAMBLES = 4
    GUESS_OR_LIFE = 5
    PUNK_RECORDS = 6

    def get_saved_media_name(self) -> SavedMediaName:
        """
        Get the SavedMediaName for this GameType
        :return: The SavedMediaName
        """
        return GAME_TYPE_SAVED_MEDIA_NAME_DICT[self]

    def get_name(self) -> str:
        """
        Get the name for this GameType
        :return: The name
        """
        return GAME_TYPE_NAME_DICT[self]

    def get_description(self) -> str:
        """
        Get the description for this GameType
        :return: The description
        """
        return GAME_TYPE_DESCRIPTION_DICT[self]

    def has_difficulty_level(self) -> bool:
        """
        Check if this game type has a difficulty
        :return: True if it has a difficulty, False otherwise
        """
        return self in GAME_TYPE_WITH_DIFFICULTY

    def is_turn_based(self) -> bool:
        """
        Check if this game type is turn based
        :return: True if it is turn based, False otherwise
        """
        return self in GAME_TYPE_TURN_BASED_LIST

    def is_guess_based(self) -> bool:
        """
        Check if this game type is time based
        :return: True if it is time based, False otherwise
        """
        return self in GAME_TYPE_GUESS_LIST

    @staticmethod
    def get_guess_based_list() -> list["GameType"]:
        """
        Get the list of game types that are guess based
        :return: The list of game types
        """
        return GAME_TYPE_GUESS_LIST


GAME_TYPE_SAVED_MEDIA_NAME_DICT = {
    GameType.ROCK_PAPER_SCISSORS: SavedMediaName.GAME_ROCK_PAPER_SCISSORS,
    GameType.RUSSIAN_ROULETTE: SavedMediaName.GAME_RUSSIAN_ROULETTE,
    GameType.WHOS_WHO: SavedMediaName.GAME_WHOS_WHO,
    GameType.SHAMBLES: SavedMediaName.GAME_SHAMBLES,
    GameType.GUESS_OR_LIFE: SavedMediaName.GAME_GUESS_OR_LIFE,
    GameType.PUNK_RECORDS: SavedMediaName.GAME_PUNK_RECORDS,
}

GAME_TYPE_NAME_DICT = {
    GameType.ROCK_PAPER_SCISSORS: phrases.ROCK_PAPER_SCISSORS_GAME_NAME,
    GameType.RUSSIAN_ROULETTE: phrases.RUSSIAN_ROULETTE_GAME_NAME,
    GameType.WHOS_WHO: phrases.WHOS_WHO_GAME_NAME,
    GameType.SHAMBLES: phrases.SHAMBLES_GAME_NAME,
    GameType.GUESS_OR_LIFE: phrases.GUESS_OR_LIFE_GAME_NAME,
    GameType.PUNK_RECORDS: phrases.PUNK_RECORDS_GAME_NAME,
}

GAME_TYPE_DESCRIPTION_DICT = {
    GameType.ROCK_PAPER_SCISSORS: phrases.ROCK_PAPER_SCISSORS_GAME_DESCRIPTION,
    GameType.RUSSIAN_ROULETTE: phrases.RUSSIAN_ROULETTE_GAME_DESCRIPTION,
    GameType.WHOS_WHO: phrases.WHOS_WHO_GAME_DESCRIPTION.format(
        Env.WHOS_WHO_NEXT_LEVEL_WAIT_TIME.get_int()
    ),
    GameType.SHAMBLES: phrases.SHAMBLES_GAME_DESCRIPTION.format(
        Env.SHAMBLES_NEXT_LEVEL_WAIT_TIME.get_int()
    ),
    GameType.GUESS_OR_LIFE: phrases.GUESS_OR_LIFE_GAME_DESCRIPTION.format(
        Env.GUESS_OR_LIFE_NEW_LIFE_WAIT_TIME.get_int()
    ),
    GameType.PUNK_RECORDS: phrases.PUNK_RECORDS_GAME_DESCRIPTION.format(
        Env.PUNK_RECORDS_NEXT_DETAIL_WAIT_TIME.get_int()
    ),
}

GAME_TYPE_WITH_DIFFICULTY = [
    GameType.GUESS_OR_LIFE,
    GameType.SHAMBLES,
    GameType.WHOS_WHO,
    GameType.PUNK_RECORDS,
]

GAME_TYPE_TURN_BASED_LIST = [GameType.ROCK_PAPER_SCISSORS, GameType.RUSSIAN_ROULETTE]
GAME_TYPE_GUESS_LIST = [
    GameType.GUESS_OR_LIFE,
    GameType.SHAMBLES,
    GameType.WHOS_WHO,
    GameType.PUNK_RECORDS,
]
