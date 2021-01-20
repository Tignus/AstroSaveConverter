import os
from cogs import AstroLogging as Logger 
import utils
from cogs.AstroSaveErrors import MultipleFolderFoundError
import re
import glob

def get_microsoft_save_folder() -> str:
    """ Retrieves the microsoft save folders from %appdata%

    We know that the saves are stored along with a container.* file.
    We look for that specific container by checking if it contains a
    save date in order to return the whole path

    :return: The list of the microsoft save folder content found in %appdata%
    :exception: FileNotFoundError if no save folder is found
    :exception: MultipleFolderFoundError if multiple save folder are found
    """

    try:
        target = os.environ['LOCALAPPDATA'] + '\\Packages\\SystemEraSoftworks*\\SystemAppData\\wgs'
    except KeyError:
        Logger.logPrint("Local Appdatas are missing, maybe you're on linux ?")
        Logger.logPrint("Press key to exit")
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
    elif len(folders) != 1:
        # We are not supposed to have more than one save folder
        Logger.logPrint(f'More than one save folders was found:\n {folders}', 'debug')
        raise MultipleFolderFoundError

    return folders[0]


def get_save_folders_from_path(path) -> list:
    microsoft_save_folders = []

    for root, _, files in os.walk(path):
        for file in files:
            if re.search(r'^container\.', file):
                container_full_path = utils.join_paths(root, file)

                Logger.logPrint(f'Container file found:{container_full_path}', 'debug')

                container_text = read_container_text_from_path(container_full_path)

                if do_container_text_match_date(container_text):
                    Logger.logPrint(f'Matching save folder {root}', 'debug')
                    microsoft_save_folders.append(root)

    return microsoft_save_folders


def read_container_text_from_path(path) -> str:
    with open(path, 'rb') as container_file:
        # Decoding the container to check for a date string
        binary_content = container_file.read()
        text = binary_content.decode('utf-16le', errors='ignore')

        return text


def do_container_text_match_date(text) -> bool:
    # Do save date matches $YYYY.MM.dd
    return re.search(r'\$\d{4}\.\d{2}\.\d{2}', text)

