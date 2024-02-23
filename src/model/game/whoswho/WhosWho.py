import json

from PIL import Image, ImageFilter

from src.model.wiki.Character import Character
from src.utils.download_utils import generate_temp_file_path, download_temp_file


class WhosWho:
    def __init__(
        self,
        character: Character,
        image_path: str = None,
        level: int = 5,
        latest_blurred_image: str = None,
        revealed_letters_count: int = 0,
    ):
        """
        Constructor
        :param character: The character
        :param image_path: The downloaded image path
        :param level: The level
        :param latest_blurred_image: The latest blurred image tg media id
        :param revealed_letters_count: The revealed letters count
        """
        self.character = character
        self.image_path = image_path
        self.level = level
        self.latest_blurred_image = latest_blurred_image
        self.revealed_letters_count = revealed_letters_count

        # Re-download the image if it doesn't exist because it was deleted
        if self.image_path is not None:
            try:
                with Image.open(self.image_path):
                    pass
            except FileNotFoundError:
                self.image_path = download_temp_file(self.character.anime_image_url, "jpg")
        else:
            self.image_path = download_temp_file(self.character.anime_image_url, "jpg")

        # Reset the blurred image if it doesn't exist because it was deleted
        if self.latest_blurred_image is not None:
            try:
                with Image.open(self.latest_blurred_image):
                    pass
            except FileNotFoundError:
                self.set_blurred_image()

        if self.latest_blurred_image is None:
            self.set_blurred_image()

    def get_board_json(self) -> str:
        """
        Returns the board as a json string
        :return: string
        """

        return json.dumps(
            self, default=lambda o: o.__dict__, sort_keys=True, separators=(",", ":")
        )

    def set_blurred_image(self):
        """
        Set the blurred image
        :return: None
        """

        with Image.open(self.image_path) as image:
            image = image.convert("RGB")
            image = image.filter(ImageFilter.GaussianBlur((self.level - 1) * 10))
            save_path = generate_temp_file_path("jpg")
            image.save(save_path)
            self.latest_blurred_image = save_path

    def reduce_level(self):
        """
        Reduce the level
        :return: None
        """
        if self.level > 0:
            self.level -= 1
            self.set_blurred_image()

    def is_correct(self, answer: str) -> bool:
        """
        Check if the answer is correct
        :param answer: The answer
        :return: bool
        """
        return answer is not None and answer.lower() == self.character.name.lower()

    def have_revealed_all_letters(self) -> bool:
        """
        Check if all letters have been revealed
        :return: bool
        """
        return self.revealed_letters_count == len(self.character.name)
