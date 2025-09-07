import os
from cogs import AstroLogging as Logger
import utils
import re
import glob
from datetime import datetime


def get_microsoft_save_folder() -> str:
    """ Retrieves the microsoft save folders from %LocalAppdata%

    We know that the saves are stored along with a container.* file.
    We look for that specific container by checking if it contains a
    save date in order to return the whole path

    If multiple folders are detected, the user will be prompted to select one.

    :return: The list of the microsoft save folder content found in %appdata%
    :exception: FileNotFoundError if no save folder is found
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

    SES_appdata_path = microsoft_save_paths[-1]

    microsoft_save_folder = seek_microsoft_save_folder(SES_appdata_path)

    return microsoft_save_folder


def seek_microsoft_save_folder(appdata_path) -> str:
    folders = get_save_folders_from_path(appdata_path)

    if not folders:
        Logger.logPrint(f'No save folder found.', 'debug')
        raise FileNotFoundError

    if len(folders) == 1:
        return folders[0]

    for i, folder in enumerate(folders, 1):
        details = get_save_details(folder)
        if details:
            formatted = ', '.join([f"{name} ({date})" for name, date in details])
        else:
            formatted = folder
        Logger.logPrint(f"{i}) {formatted}")

    while True:
        Logger.logPrint('Select the save folder to use:')
        choice = input()
        try:
            index = int(choice)
            if 1 <= index <= len(folders):
                return folders[index - 1]
        except ValueError:
            pass
        Logger.logPrint('Invalid selection. Please enter a valid number.')


def get_save_folders_from_path(path) -> list:
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
    """Return list of (save_name, date_str) found in the folder's container file."""
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


def read_container_text_from_path(path) -> str:
    with open(path, 'rb') as container_file:
        # Decoding the container to check for a date string
        binary_content = container_file.read()
        text = binary_content.decode('utf-16le', errors='ignore')

        return text


def do_container_text_match_date(text) -> bool:
    # Do save date matches $YYYY.MM.dd
    return re.search(r'\$\d{4}\.\d{2}\.\d{2}', text)


def backup_microsoft_save_folder(to_path: str) -> str:
    astroneer_save_folder = get_microsoft_save_folder()
    utils.copy_files(astroneer_save_folder, to_path)

    return astroneer_save_folder
