import os

import validators
from PIL import Image

from src.utils.download_utils import download_temp_file


def compress_image(path: str, quality: int) -> str:
    """
    Reduces an image to the required max file size
    :param path: Path to the original (unchanged) image
    :type path: str
    :param quality: Quality of the compressed image (0-100)
    :type quality: int
    :return: an image path to the limited image.
    :rtype: str
    """

    # Download image if path is an url
    if validators.url(path):
        path = download_temp_file(path)

    with Image.open(path) as image:
        compressed_image_path = os.path.join(
            os.path.dirname(path), f"compressed_{os.path.basename(path)}"
        )
        image.save(compressed_image_path, quality=quality, optimize=True)

    return compressed_image_path
