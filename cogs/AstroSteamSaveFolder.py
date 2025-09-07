import os
from cogs import AstroLogging as Logger
"""Helpers for locating Steam save folders."""

import os
import utils
from errors import MultipleFolderFoundError
import re
import glob
from cogs import AstroLogging as Logger


def get_steam_save_folder() -> str:
    """Return the path to the Steam save folder.

    Returns:
        str: Path to the Steam save folder.

    Raises:
        FileNotFoundError: If no save folder is found.
        MultipleFolderFoundError: If multiple folders are detected.
    """

    try:
        target = os.environ['LOCALAPPDATA'] + '\\Astro\\Saved\\SaveGames'
    except KeyError:
        Logger.logPrint("Local Appdata are missing, maybe you're on linux ?")
        Logger.logPrint("Press any key to exit")
        utils.wait_and_exit(1)

    steam_save_paths = list(glob.iglob(target))

    for path in steam_save_paths:
        Logger.logPrint(f'SES path found in appadata: {path}', 'debug')

    return steam_save_paths[0]


def seek_microsoft_save_folder(appdata_path: str) -> str:
    """Identify the unique Microsoft save folder inside ``appdata_path``.

    Args:
        appdata_path: Base directory to search.

    Returns:
        str: Path to the save folder.

    Raises:
        FileNotFoundError: If no folder is found.
        MultipleFolderFoundError: If more than one folder is found.
    """
    folders = get_save_folders_from_path(appdata_path)

    if not folders:
        Logger.logPrint(f'No save folder found.', 'debug')
        raise FileNotFoundError
    if len(folders) != 1:
        Logger.logPrint(f'More than one save folders was found:\n {folders}', 'debug')
        raise MultipleFolderFoundError

    return folders[0]


def get_save_folders_from_path(path: str) -> list:
    """Return all subdirectories containing a container file."""
    microsoft_save_folders = []

    for root, _, files in os.walk(path):
        for file in files:
            if re.search(r'^container\.', file):
                container_full_path = utils.join_paths(root, file)

                Logger.logPrint(f'Container file found: {container_full_path}', 'debug')

                container_text = read_container_text_from_path(container_full_path)

                if do_container_text_match_date(container_text):
                    Logger.logPrint(f'Matching save folder {root}', 'debug')
                    microsoft_save_folders.append(root)

    return microsoft_save_folders


def read_container_text_from_path(path: str) -> str:
    """Return decoded text from a container file."""
    with open(path, 'rb') as container_file:
        binary_content = container_file.read()
        return binary_content.decode('utf-16le', errors='ignore')


def do_container_text_match_date(text: str) -> bool:
    """Return ``True`` if ``text`` contains a date pattern."""
    return re.search(r'\$\d{4}\.\d{2}\.\d{2}', text)
