from src.model.enums.AssetPath import AssetPath
from src.model.enums.SavedMediaName import SavedMediaName
from src.model.enums.SavedMediaType import SavedMediaType


class SavedMedia:
    """
    SavedMedia class
    """

    def __init__(
        self,
        media_type: SavedMediaType = None,
        media_id: str = None,
        name: SavedMediaName = None,
        file_name: str = None,
    ):
        """
        Constructor
        :param media_type: Media type
        :param media_id: Media id
        :param name: Media name
        :param file_name: File name
        """
        self.type: SavedMediaType = media_type
        self.media_id: str = media_id
        self.name: SavedMediaName = name
        self.file_name: str = file_name

    @staticmethod
    def get_by_name(name: SavedMediaName) -> "SavedMedia":
        """
        Get a SavedMedia by name
        :param name: Name of the SavedMedia
        :return: The SavedMedia
        """
        return SAVED_MEDIA_DICT[name]


SAVED_MEDIA_DICT = {}

# noinspection DuplicatedCode
CREW_INVITE = SavedMedia(
    media_type=SavedMediaType.PHOTO,
    name=SavedMediaName.CREW_INVITE,
    file_name=AssetPath.CREW_INVITE,
)
SAVED_MEDIA_DICT[SavedMediaName.CREW_INVITE] = CREW_INVITE

CREW_JOIN = SavedMedia(
    media_type=SavedMediaType.PHOTO, name=SavedMediaName.CREW_JOIN, file_name=AssetPath.CREW_JOIN
)
SAVED_MEDIA_DICT[SavedMediaName.CREW_JOIN] = CREW_JOIN

DEVIL_FRUIT_NEW = SavedMedia(
    media_type=SavedMediaType.PHOTO,
    name=SavedMediaName.DEVIL_FRUIT_NEW,
    file_name=AssetPath.DEVIL_FRUIT_NEW,
)
SAVED_MEDIA_DICT[SavedMediaName.DEVIL_FRUIT_NEW] = DEVIL_FRUIT_NEW

DOC_Q = SavedMedia(
    media_type=SavedMediaType.PHOTO, name=SavedMediaName.DOC_Q, file_name=AssetPath.DOC_Q
)
SAVED_MEDIA_DICT[SavedMediaName.DOC_Q] = DOC_Q

FIGHT = SavedMedia(
    media_type=SavedMediaType.PHOTO, name=SavedMediaName.FIGHT, file_name=AssetPath.FIGHT
)
SAVED_MEDIA_DICT[SavedMediaName.FIGHT] = FIGHT

# noinspection DuplicatedCode
GAME = SavedMedia(
    media_type=SavedMediaType.PHOTO, name=SavedMediaName.GAME, file_name=AssetPath.GAME
)
SAVED_MEDIA_DICT[SavedMediaName.GAME] = GAME

# noinspection DuplicatedCode
GAME_ROCK_PAPER_SCISSORS = SavedMedia(
    media_type=SavedMediaType.PHOTO,
    name=SavedMediaName.GAME_ROCK_PAPER_SCISSORS,
    file_name=AssetPath.GAME_ROCK_PAPER_SCISSORS,
)
SAVED_MEDIA_DICT[SavedMediaName.GAME_ROCK_PAPER_SCISSORS] = GAME_ROCK_PAPER_SCISSORS

GAME_RUSSIAN_ROULETTE = SavedMedia(
    media_type=SavedMediaType.PHOTO,
    name=SavedMediaName.GAME_RUSSIAN_ROULETTE,
    file_name=AssetPath.GAME_RUSSIAN_ROULETTE,
)

SAVED_MEDIA_DICT[SavedMediaName.GAME_RUSSIAN_ROULETTE] = GAME_RUSSIAN_ROULETTE

GAME_WHOS_WHO = SavedMedia(
    media_type=SavedMediaType.PHOTO,
    name=SavedMediaName.GAME_WHOS_WHO,
    file_name=AssetPath.GAME_WHOS_WHO,
)
SAVED_MEDIA_DICT[SavedMediaName.GAME_WHOS_WHO] = GAME_WHOS_WHO

GAME_SHAMBLES = SavedMedia(
    media_type=SavedMediaType.PHOTO,
    name=SavedMediaName.GAME_SHAMBLES,
    file_name=AssetPath.GAME_SHAMBLES,
)
SAVED_MEDIA_DICT[SavedMediaName.GAME_SHAMBLES] = GAME_SHAMBLES

GAME_GUESS_OR_LIFE = SavedMedia(
    media_type=SavedMediaType.PHOTO,
    name=SavedMediaName.GAME_GUESS_OR_LIFE,
    file_name=AssetPath.GAME_GUESS_OR_LIFE,
)
SAVED_MEDIA_DICT[SavedMediaName.GAME_GUESS_OR_LIFE] = GAME_GUESS_OR_LIFE

PUNK_RECORDS = SavedMedia(
    media_type=SavedMediaType.PHOTO,
    name=SavedMediaName.GAME_PUNK_RECORDS,
    file_name=AssetPath.GAME_PUNK_RECORDS,
)
SAVED_MEDIA_DICT[SavedMediaName.GAME_PUNK_RECORDS] = PUNK_RECORDS

# noinspection DuplicatedCode
SILENCE = SavedMedia(
    media_type=SavedMediaType.PHOTO, name=SavedMediaName.SILENCE, file_name=AssetPath.SILENCE
)
SAVED_MEDIA_DICT[SavedMediaName.SILENCE] = SILENCE

PLUNDER = SavedMedia(
    media_type=SavedMediaType.PHOTO, name=SavedMediaName.PLUNDER, file_name=AssetPath.PLUNDER
)
SAVED_MEDIA_DICT[SavedMediaName.PLUNDER] = PLUNDER

PLUNDER_SUCCESS = SavedMedia(
    media_type=SavedMediaType.PHOTO,
    name=SavedMediaName.PLUNDER_SUCCESS,
    file_name=AssetPath.PLUNDER_SUCCESS,
)
SAVED_MEDIA_DICT[SavedMediaName.PLUNDER_SUCCESS] = PLUNDER_SUCCESS

PLUNDER_FAIL = SavedMedia(
    media_type=SavedMediaType.PHOTO,
    name=SavedMediaName.PLUNDER_FAIL,
    file_name=AssetPath.PLUNDER_FAIL,
)
SAVED_MEDIA_DICT[SavedMediaName.PLUNDER_FAIL] = PLUNDER_FAIL

DAILY_REWARD = SavedMedia(
    media_type=SavedMediaType.PHOTO,
    name=SavedMediaName.DAILY_REWARD,
    file_name=AssetPath.DAILY_REWARD,
)
SAVED_MEDIA_DICT[SavedMediaName.DAILY_REWARD] = DAILY_REWARD

FIGHT_PLUNDER_SCOUT = SavedMedia(
    media_type=SavedMediaType.PHOTO,
    name=SavedMediaName.FIGHT_PLUNDER_SCOUT,
    file_name=AssetPath.FIGHT_PLUNDER_SCOUT,
)
SAVED_MEDIA_DICT[SavedMediaName.FIGHT_PLUNDER_SCOUT] = FIGHT_PLUNDER_SCOUT
