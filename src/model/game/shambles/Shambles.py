import json
import random
import string

from PIL import Image, ImageDraw, ImageFont

import resources.Environment as Env
from src.model.enums.AssetPath import AssetPath
from src.model.game.GameDifficulty import GameDifficulty
from src.model.wiki.Terminology import Terminology
from src.utils.download_utils import generate_temp_file_path


class Shambles:
    def __init__(
        self,
        terminology: Terminology,
        grid_size: int,
        grid: list[list[str]] = None,
        word_coordinates: list[tuple[int, int]] = None,
        excluded_coordinates: list[tuple[int, int]] = None,
        image_path: str = None,
        revealed_letters_count: int = 0,
    ):
        """
        Constructor
        :param terminology: The terminology
        :param grid_size: The grid size
        :param grid: The grid of letters
        :param word_coordinates: The coordinates of the word
        :param excluded_coordinates: The coordinates of the letters that have been blanked out to
        make it easier
        :param image_path: The crossword image path
        :param revealed_letters_count: The revealed letters count
        """

        self.terminology = terminology
        self.grid_size = grid_size
        self.grid = grid
        self.word_coordinates = word_coordinates
        self.excluded_coordinates = (
            excluded_coordinates if excluded_coordinates is not None else []
        )
        self.image_path = image_path
        self.revealed_letters_count = revealed_letters_count

        if self.grid is None:
            self.create_grid()

        # Reset the image if it doesn't exist because it was deleted
        if self.image_path is not None:
            try:
                with Image.open(self.image_path):
                    pass
            except FileNotFoundError:
                self.set_grid_image()

        if self.image_path is None:
            self.set_grid_image()

    def get_board_json(self) -> str:
        """
        Returns the board as a json string
        :return: string
        """

        return json.dumps(
            self, default=lambda o: o.__dict__, sort_keys=True, separators=(",", ":")
        )

    def create_grid(self):
        """
        Create the grid
        :return: None
        """

        word = self.terminology.name.replace(" ", "")
        grid_size = self.grid_size

        # Check if the word length is larger than the grid size
        if len(word) > self.grid_size:
            raise ValueError("The length of the word cannot be larger than the grid size")

        # Convert the word to uppercase
        word = word.upper()

        # Define the grid for the crossword puzzle.
        grid = [[" " for _ in range(self.grid_size)] for _ in range(self.grid_size)]

        # Select a random direction for the word (either horizontal, vertical, or diagonal).
        direction = random.choice(["horizontal", "vertical", "diagonal"])

        # Determine the number of cells in the grid that the word will occupy based on its length
        # and direction.
        word_len = len(word)
        if direction == "horizontal":
            max_start_x = self.grid_size - word_len
            max_start_y = self.grid_size - 1
        elif direction == "vertical":
            max_start_x = self.grid_size - 1
            max_start_y = self.grid_size - word_len
        else:
            max_start_x = max_start_y = self.grid_size - word_len

        # Select a random starting point for the word that is within the grid boundaries.
        start_x = random.randint(0, max_start_x)
        start_y = random.randint(0, max_start_y)

        # Place the word in the selected direction starting from the chosen starting point.
        for i in range(word_len):
            x = start_x + i if direction in ["horizontal", "diagonal"] else start_x
            y = start_y + i if direction in ["vertical", "diagonal"] else start_y

            grid[y][x] = word[i]

        # For the remaining cells in the grid that are not occupied by the placed word,
        # fill them with random letters from the alphabet.
        alphabet = string.ascii_uppercase
        for y in range(grid_size):
            for x in range(grid_size):
                if grid[y][x] == " ":
                    grid[y][x] = random.choice(alphabet)

        # Save the coordinates of the word in the grid
        word_coordinates = []
        for i in range(word_len):
            word_coordinates.append((
                start_x + i * (direction == "horizontal") + i * (direction == "diagonal"),
                start_y + i * (direction == "vertical") + i * (direction == "diagonal"),
            ))

        self.grid = grid
        self.word_coordinates = word_coordinates

    def set_grid_image(self, highlight_answer: bool = False):
        """
        Set the grid image
        :return: None
        """

        # Open the crossword puzzle template image
        with Image.open(AssetPath.GAME_BACKGROUND) as image:
            # Get the box size of the image
            left, upper, right, lower = image.getbbox()
            width = right - left
            height = lower - upper

            # Calculate the width and height of each cell in the grid
            cell_width = width / self.grid_size
            cell_height = height / self.grid_size

            # Get the font size based on the cell size, 8/10 of the cell width
            font_size = int(cell_width * 8 / 10)
            stroke_width = int(font_size / 25)

            # Get the font
            font = ImageFont.truetype(AssetPath.FONT_BLOGGER_SANS_BOLD, font_size)

            # Write the word in the grid on the image, with an outline for each letter
            for y in range(self.grid_size):
                for x in range(self.grid_size):
                    letter = self.grid[y][x]

                    if letter != " ":
                        # Calculate the position of the letter on the image
                        x_pos = x * cell_width + cell_width / 2
                        y_pos = y * cell_height + cell_height / 2

                        # Get the width and height of the letter
                        letter_width, letter_height = font.getsize(letter)

                        # Calculate the position of the letter on the image
                        x_pos -= letter_width / 2
                        y_pos -= letter_height / 2

                        fill_color = "white"
                        if highlight_answer and [x, y] in self.word_coordinates:
                            fill_color = "#39FF14"  # Neon green

                        # Draw the letter on the image
                        draw = ImageDraw.Draw(image)
                        draw.text(
                            (x_pos, y_pos),
                            letter,
                            font=font,
                            fill=fill_color,
                            stroke_width=stroke_width,
                            stroke_fill="black",
                        )

            # Save the image
            save_path = generate_temp_file_path("jpg")
            image.save(save_path)
            self.image_path = save_path

    def is_correct(self, answer: str) -> bool:
        """
        Check if the answer is correct
        :param answer: The answer
        :return: bool
        """
        return answer is not None and answer.lower() == self.terminology.name.lower()

    def get_excludable_letters_count(self) -> int:
        """
        Get the number of letters that can be excluded
        :return: int
        """

        grid_total_size = len(self.grid) * len(self.grid[0])
        return grid_total_size - len(self.word_coordinates) - len(self.excluded_coordinates)

    def can_reduce_level(self) -> bool:
        """
        Check if another letter can be excluded
        :return: bool
        """

        return self.get_excludable_letters_count() > 0

    def reduce_level(self, should_set_image: bool = True):
        """
        Reduce the level of the terminology
        :param should_set_image: Whether to set the image
        :return: None
        """

        if not self.can_reduce_level():
            raise ValueError("Cannot reduce level")

        # Coordinates of non-excluded letters that are not part of the word
        non_excluded_coordinates = []
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                if [x, y] not in self.excluded_coordinates and [x, y] not in self.word_coordinates:
                    non_excluded_coordinates.append((x, y))

        # Select a random coordinate from the non-excluded coordinates
        coordinate = random.choice(non_excluded_coordinates)

        # Remove the letter from the grid
        self.grid[coordinate[1]][coordinate[0]] = "·"

        # Add the coordinate to the excluded coordinates
        self.excluded_coordinates.append(coordinate)

        if should_set_image:
            self.set_grid_image()

    def have_revealed_all_letters(self) -> bool:
        """
        Check if all the letters have been revealed
        :return: bool
        """
        return self.revealed_letters_count == len(self.terminology.name)

    @staticmethod
    def get_grid_size_by_difficulty(difficulty: GameDifficulty) -> int:
        """
        Get the grid size by difficulty level
        :return: int
        """

        match difficulty:
            case GameDifficulty.EASY:
                return Env.SHAMBLES_GRID_SIZE_EASY.get_int()

            case GameDifficulty.MEDIUM:
                return Env.SHAMBLES_GRID_SIZE_MEDIUM.get_int()

            case GameDifficulty.HARD:
                return Env.SHAMBLES_GRID_SIZE_HARD.get_int()

            case _:
                raise ValueError("Invalid difficulty")
