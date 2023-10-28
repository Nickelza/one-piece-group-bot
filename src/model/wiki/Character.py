from src.model.wiki.Terminology import Terminology


class Character(Terminology):
    # noinspection PyUnusedLocal
    # **kwargs is used to ignore unused arguments
    def __init__(self, name: str, info_url: str, anime_image_url: str, difficulty: int, info_box: dict, **kwargs):
        """Initialize the character."""

        super().__init__(name, info_url)

        self.anime_image_url = anime_image_url
        self.difficulty = difficulty
        self.info_box = info_box
