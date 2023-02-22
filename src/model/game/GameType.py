from enum import IntEnum

from src.model.enums.SavedMediaName import SavedMediaName


class GameType(IntEnum):
    """
    Enum for the game type
    """
    ROCK_PAPER_SCISSORS = 1
    RUSSIAN_ROULETTE = 2
    WHOS_WHO = 3
    SHAMBLES = 4

    def get_saved_media_name(self) -> SavedMediaName:
        """
        Get the SavedMediaName for this GameType
        :return: The SavedMediaName
        """
        return GAME_TYPE_SAVED_MEDIA_NAME_DICT[self]


GAME_TYPE_SAVED_MEDIA_NAME_DICT = {
    GameType.ROCK_PAPER_SCISSORS: SavedMediaName.GAME_ROCK_PAPER_SCISSORS,
    GameType.RUSSIAN_ROULETTE: SavedMediaName.GAME_RUSSIAN_ROULETTE,
    GameType.WHOS_WHO: SavedMediaName.GAME_WHOS_WHO,
    GameType.SHAMBLES: SavedMediaName.GAME_SHAMBLES
}
