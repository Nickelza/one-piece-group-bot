import logging
import os
import pathlib
import shutil
import time
import urllib.error
import urllib.request
import uuid

import constants as const


def download_temp_file(url: str) -> str:
    """
    Download file to temp folder
    :param url: url of file
    :type url: str
    :return: path of downloaded file
    """

    # Create temp folder
    if not os.path.exists(const.TEMP_DIR):
        os.makedirs(const.TEMP_DIR)

    # File name
    file_name = uuid.uuid4().hex + pathlib.Path(url).suffix
    file_path = os.path.join(const.TEMP_DIR, file_name)

    # Download file
    urllib.request.urlretrieve(url, file_path)

    return file_path


def cleanup_temp_dir() -> None:
    """
    Removes files older than x time from temp folder
    """

    current_time = time.time()
    time_limit = float(os.environ[const.ENV_TEMP_DIR_CLEANUP_TIME_SECONDS])

    # Delete temp folder
    if os.path.exists(const.TEMP_DIR):  # Temp folder exists
        for file in os.listdir(const.TEMP_DIR):  # Iterate files in folder
            file_path = os.path.join(const.TEMP_DIR, file)
            try:
                pathinfo = os.stat(file_path)
                if pathinfo.st_ctime < current_time - time_limit or True:  # File is older than x time
                    logging.info("Removing temp file: %s", file_path)
                    if os.path.isfile(file_path):  # Is a file
                        os.unlink(file_path)
                    else:
                        shutil.rmtree(file_path)  # Is a folder
            except Exception as e:
                logging.error('Error while deleting temp path: %s', e)
