import random

from src.model.enums.AssetPath import AssetPath


def get_random_item_from_txt(asset_path: AssetPath) -> str:
    """
    Get a random item from a txt file
    :param asset_path: The asset path
    :return: A random item from the txt file
    """

    with open(asset_path) as file:
        lines = file.readlines()
        return random.choice(lines).strip()
