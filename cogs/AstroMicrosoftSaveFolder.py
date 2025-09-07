"""Utilities for locating and backing up Microsoft/Xbox save folders."""

import os
from cogs import AstroLogging as Logger
import utils
import re
import glob
from datetime import datetime


def get_microsoft_save_folder() -> str:
    """Return the path to the Microsoft save folder.

    Returns:
        str: Path to the save folder.

    Raises:
        FileNotFoundError: If no folder can be located.
    """

    try:
        target = os.environ['LOCALAPPDATA'] + '\\Packages\\SystemEraSoftworks*\\SystemAppData\\wgs'
    except KeyError:
        Logger.logPrint("Local Appdata are missing, maybe you're on linux ?")
        Logger.logPrint("Press any key to exit")
        utils.wait_and_exit(1)

    microsoft_save_paths = list(glob.iglob(target))

    for path in microsoft_save_paths:
        Logger.logPrint(f'SES path found in appadata: {path}', 'debug')

    if not microsoft_save_paths:
        raise FileNotFoundError("No Microsoft save folder detected")

    SES_appdata_path = microsoft_save_paths[-1]

    microsoft_save_folder = seek_microsoft_save_folder(SES_appdata_path)

    return microsoft_save_folder


def seek_microsoft_save_folder(appdata_path: str) -> str:
    """Search for a valid Microsoft save folder inside ``appdata_path``.

    Args:
        appdata_path: Base directory to search.

    Returns:
        str: Chosen save folder path.

    Raises:
        FileNotFoundError: If no folders are found.
    """
    folders = get_save_folders_from_path(appdata_path)

    if not folders:
        Logger.logPrint(f'No save folder found.', 'debug')
        raise FileNotFoundError

    if len(folders) == 1:
        return folders[0]

    Logger.logPrint(
        f"{len(folders)} Microsoft save folders have been found. Select the one to use:"
    )
    for i, folder in enumerate(folders, 1):
        Logger.logPrint(f"\t{i}) {folder}")
        Logger.logPrint("\tFolder content:")
        for name, date in get_save_details(folder):
            Logger.logPrint(f"\t\t{name} - {date}")

    while True:
        choice = input()
        Logger.logPrint(f"User choice: {choice}", "debug")
        try:
            index = int(choice)
            if 1 <= index <= len(folders):
                break
        except ValueError:
            pass
        Logger.logPrint('Invalid selection. Please enter a valid number.')

    return folders[index - 1]


def get_save_folders_from_path(path: str) -> list:
    """Return all subdirectories containing a valid container file.

    Args:
        path: Directory to scan recursively.

    Returns:
        list: Paths of detected save folders.
    """
    microsoft_save_folders = []

    for root, _, files in os.walk(path):
        for file in files:
            if re.search(r'^container\.', file):
                container_full_path = utils.join_paths(root, file)

                Logger.logPrint(f'Container file found: {container_full_path}', 'debug')

                container_text = read_container_text_from_path(container_full_path)

                if do_container_text_match_date(container_text):
                    Logger.logPrint(f'Matching save folder: {root}', 'debug')
                    microsoft_save_folders.append(root)

    return microsoft_save_folders


def get_save_details(folder_path: str):
    """Return list of ``(save_name, date_str)`` for saves in ``folder_path``."""
    container_files = glob.glob(utils.join_paths(folder_path, 'container.*'))
    if not container_files:
        return []

    container_path = container_files[0]
    with open(container_path, 'rb') as container_file:
        text = container_file.read().decode('utf-16le', errors='ignore')

    pattern = re.compile(r'([A-Za-z0-9_]+)\$c?(\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2})')
    details = []
    for name, date_str in pattern.findall(text):
        try:
            dt = datetime.strptime(date_str, '%Y.%m.%d-%H.%M.%S')
            formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            formatted_date = date_str
        details.append((name, formatted_date))
    return details


def read_container_text_from_path(path: str) -> str:
    """Read a container file and return its decoded text."""
    with open(path, 'rb') as container_file:
        binary_content = container_file.read()
        return binary_content.decode('utf-16le', errors='ignore')


def do_container_text_match_date(text: str) -> bool:
    """Check whether container text contains a date pattern."""
    return re.search(r'\$\d{4}\.\d{2}\.\d{2}', text)


def backup_microsoft_save_folder(to_path: str) -> str:
    """Copy the Microsoft save folder to ``to_path``.

    Args:
        to_path: Destination directory for the backup.

    Returns:
        str: Path to the original save folder that was backed up.
    """
    astroneer_save_folder = get_microsoft_save_folder()
    utils.copy_files(astroneer_save_folder, to_path)

    return astroneer_save_folder


def find_microsoft_save_folders() -> list:
    """Find all Microsoft save folders on the system."""
    save_folders = []

    try:
        target = os.environ['LOCALAPPDATA'] + '\\Packages\\SystemEraSoftworks*\\SystemAppData\\wgs'
    except KeyError:
        Logger.logPrint("Local Appdata are missing, maybe you're on linux ?")
        Logger.logPrint("Press any key to exit")
        utils.wait_and_exit(1)

    for path in glob.iglob(target):
        save_folders.extend(get_save_folders_from_path(path))

    Logger.logPrint(f'{len(save_folders)} save folders found', 'debug')
    for folder in save_folders:
        Logger.logPrint(f'Save folder found: {folder}', 'debug')

    if not save_folders:
        raise FileNotFoundError

    return save_folders


def backup_microsoft_save_folders(folders: list, to_path: str) -> list:
    """Backup multiple Microsoft save folders into numbered directories."""
    utils.make_dir_if_doesnt_exists(to_path)
    for i, folder in enumerate(folders, 1):
        destination = utils.join_paths(to_path, f'Backup_{i}')
        utils.copy_files(folder, destination)

    return folders
