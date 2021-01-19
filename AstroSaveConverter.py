import argparse
from argparse import Namespace
import os
import sys
import shutil
from datetime import datetime
import re
import glob
import winpath

from cogs.AstroSaveErrors import MultipleFolderFoundError
from cogs.AstroLogging import AstroLogging
from cogs.AstroSaveContainer import AstroSaveContainer

"""
"""
def get_microsoft_save_folder() -> str:
    """ Retrieves the microsoft save folders from %appdata%

    We know that the saves are stored along with a container.* file.
    We look for that specific container by checking if it contains a
    save date in order to return the whole path

    :return: The list of the microsoft save folder content found in %appdata%
    :exception: FileNotFoundError if no save folder is found
    :exception: MultipleFolderFoundError if multiple save folder are found
    """

    target = os.environ['LOCALAPPDATA'] + '\\Packages\\SystemEraSoftworks*\\SystemAppData\\wgs'
    microsoft_save_paths = list(glob.iglob(target))

    for path in microsoft_save_paths:
        AstroLogging.logPrint(f'SES path found in appadata: {path}', 'debug')

    SES_appdata_path = microsoft_save_paths[-1]

    microsoft_save_folder = seek_microsoft_save_folder(SES_appdata_path)

    return microsoft_save_folder


def seek_microsoft_save_folder(appdata_path) -> str:

    microsoft_save_folders = get_save_folders_from_path(appdata_path)

    if not microsoft_save_folders:
        AstroLogging.logPrint(f'No save folder found.', 'debug')
        raise FileNotFoundError
    elif len(microsoft_save_folders) != 1:
        # We are not supposed to have more than one save folder
        AstroLogging.logPrint(f'More than one save folders was found:\n {microsoft_save_folders}', 'debug')
        raise MultipleFolderFoundError

    return microsoft_save_folders[0]


def get_save_folders_from_path(path) -> list(str):
    microsoft_save_folders = []

    for root, _, files in os.walk(path):
        for file in files:
            if re.search(r'^container\.', file):
                container_full_path = os.path.join(root, file)

                AstroLogging.logPrint(f'Container file found:{container_full_path}', 'debug')

                container_text = read_text_from_container(container_full_path)

                if do_container_text_match_date(container_text):
                    AstroLogging.logPrint(f'Matching save folder {root}', 'debug')
                    microsoft_save_folders.append(root)

    return microsoft_save_folders


def read_text_from_container(path) -> str:
    with open(path, 'rb') as container:
        # Decoding the container to check for a date string
        binary_content = container.read()
        text = binary_content.decode('utf-16le', errors='ignore')

        return text


def do_container_text_match_date(text) -> bool:
    # Do save date matches $YYYY.MM.dd
    return re.search(r'\$\d{4}\.\d{2}\.\d{2}', text)

""""""
""""""
def get_save_folder():
    """
    Obtains the save folder

    Lets the user pick between automatic save retrieving/copying or
    a custom save folder

    Arguments:
        None

    Returns:
        Returns the save folder path

    Exception:
        None
    """
    AstroLogging.logPrint("Which  folder would you like to work with ?")
    AstroLogging.logPrint("\t1) Automatically detect and copy my save folder (Please close Astroneer first)")
    AstroLogging.logPrint("\t2) Chose a custom folder")

    work_choice = input()
    while work_choice not in ('1', '2'):
        AstroLogging.logPrint(f'\nPlease choose 1 or 2')
        work_choice = input()
        AstroLogging.logPrint(f'folder_type {work_choice}', 'debug')

    if work_choice == '1':
        microsoft_save_folder = get_microsoft_save_folder()
        AstroLogging.logPrint(f'Microsoft folder path: {microsoft_save_folder}', 'debug')

        save_path = ask_copy_target()
        copy_files(microsoft_save_folder, save_path)

        AstroLogging.logPrint(f'Save files copied to: {save_path}')

    elif work_choice == '2':
        save_path = ask_custom_folder_path()


    return save_path


def copy_files(source, target):
    if os.path.isdir(target):
        shutil.rmtree(target)
    shutil.copytree(source, target)


def ask_copy_target():
    AstroLogging.logPrint('Where would you like to copy your save folder ?')
    AstroLogging.logPrint('\t1) New folder on my desktop')
    AstroLogging.logPrint("\t2) New folder in a custom path")

    choice = input()
    while choice not in ('1', '2'):
        AstroLogging.logPrint(f'\nPlease choose 1 or 2')
        choice = input()
        AstroLogging.logPrint(f'copy_choice {choice}', 'debug')

    if choice == '1':
        # Winpath is needed here because Windows user can have a custom Desktop location
        save_path = winpath.get_desktop()
    elif choice == '2':
        AstroLogging.logPrint(f'\nEnter your custom folder path:')
        save_path = input()
        AstroLogging.logPrint(f'save_path {save_path}', 'debug')

    return os.path.join(save_path, create_folder_name())


def ask_custom_folder_path() -> str:
    AstroLogging.logPrint(f'\nEnter your custom folder path:')
    path = input()
    AstroLogging.logPrint(f'save_folder_path {path}', 'debug')

    if is_folder_a_dir(path):
        return path
    else:
        AstroLogging.logPrint(f'\nWrong path for save folder, please enter a valid path : ')
        return ask_custom_folder_path()


def get_windows_desktop_path() -> str:
    return winpath.get_desktop()


def create_folder_name() -> str:
    now = datetime.now().strftime('%Y.%m.%d-%H.%M')
    return f'AstroSaveFolder_{now}'


def is_folder_writable(path) -> bool:
    return os.access(os.path.dirname(path), os.W_OK)


def is_folder_exists(path) -> bool:
    return os.path.exists(path)


def is_folder_a_dir(path) -> bool:
    return os.path.isdir(path)


def is_a_file(path) -> bool:
    return os.path.isfile(path)


def is_a_container_file(path) -> bool:
    return is_a_file(path) and path.rfind('container') != -1


def get_folder_content(path) -> list(str):
    return os.listdir(path)


def get_containers_list(path) -> list(str):
    """
    List all containers in a folder
    Arguments:
        path -- path for search containers
    Returns:
        Returns a list of all containers found (only filename of container)
    Exception:
        None
    """
    folder_content = get_folder_content(path)
    containers_list = [file for file in folder_content if is_a_container_file(file)]

    if not containers_list or len(containers_list) == 0:
        AstroLogging.logPrint('\nNo container found in path: ' + path)
        raise FileNotFoundError

    return containers_list


def ask_user_to_choose_in_a_list(text, file_list):
    """ Defines the container to use

    Print every *container* file in the
    given and make the user choose one

    :param containers_list: A list of identified to be containers

    :returns: The chosen container filename
    """
    max_container_number = len(file_list)
    min_container_number = 1
    choice_index = 0

    while choice_index == 0:
        AstroLogging.logPrint('\nWhich container would you like to convert ?')
        print_list_elements(file_list)
        choice_index = input()
        try:
            choice_index = int(choice_index)
            verify_choice_input(choice_index, min_container_number, max_container_number)
        except ValueError:
            choice_index = 0
            AstroLogging.logPrint(f'Please use only values between {min_container_number} and {max_container_number}')

    return file_list[choice_index-1]


def print_list_elements(list):
    for i, container in containers_list:
        AstroLogging.logPrint(f'\t {i+1}) {container}')


def verify_choice_input(choice, min, max):
    if (choice < min or choice > max):
        raise ValueError


""""""
def process_multiple_choices_input(choices, max_value) -> list(int):
    choices = choices.split(',').map(lambda x: int(x))
    choices = [number for number in choices if number >= 0 or number < max_value]
    return choices


def verify_choices_input(choices):
    if len(choices) == 0:
        raise ValueError

    if 0 in choices and len(choices) != 1:
        raise ValueError


def multiple_choice_input(maximum_value) -> list(int):
    """ Let the user choose multiple numbers between 0 and a maximum value

    If the user choice is 0 then return an array with all values

    :Example:

    -  [1,2,4]
    -  [0]

    :return: The list of numbers
    :exception: None (repeat until the choices are valid)
    """
    choices = []
    while not choices:
        choices = input()
        choices = process_multiple_choices_input(choices, maximum_value)

        try:
            verify_choices_input(choices)
        except ValueError:
            choices = []
            AstroLogging.logPrint(f'Please use only values between 1 and {maximum_value} or 0 alone')

        if saves_to_export == [0]:
            return list(range(1, maximum_value))
        else:
            return choices


def rename_saves(container):
    """ Rename all the list of save in the container

    :param container: Container from which to rename the saves
    """
    for number in saves_to_export:
        container.save_list[number - 1].rename()


def get_args() -> Namespace:
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "-p", "--savesPath", help="Path from which to read the container and extract the saves", required=False)

        args = parser.parse_args()

        # Default values

        try:
            args.savesPath = args.savesPath or get_save_folder()
        except MultipleFolderFoundError:
            AstroLogging.logPrint(f'\nToo many save folders found ! Please use custom folder mode.')
            # Recursive until it works
            return get_args()

        return args


def wait_and_exit(code):
    input()
    sys.exit(code)


def rm_dir_if_exists(path):
    if not os.path.isdir(path):
        os.mkdir(path)


if __name__ == "__main__":

    AstroLogging.setup_logging(os.getcwd())

    try:
        os.system("title AstroSaveConverter - Migrate your Astroneer save from Microsoft to Steam")
    except:
        pass

    args = get_args()

    try:
        containers_list = get_containers_list(args.savesPath)
        AstroLogging.logPrint('\nContainers found:')
    except FileNotFoundError as e:
        AstroLogging.logPrint('\nContainer not found, press any key to exit')
        AstroLogging.logPrint(e, 'exception')
        wait_and_exit(1)

    if len(containers_list) == 1:
        container_name = containers_list[0]
    else:
        container_name = ask_user_to_choose_in_a_list(
            '\nWhich container would you like to convert ?',
            containers_list
        )

    try:
        container = AstroSaveContainer(os.path.join(args.savesPath, container_file_name))

        AstroLogging.logPrint('Container file loaded successfully !\n')
        container.print_container()

        AstroLogging.logPrint('\nWhich saves would you like to convert ? (Choose 0 for all of them)')
        AstroLogging.logPrint('(Multi-convert is supported. Ex: "1,2,4")')

        maximum_save_number = len(container.save_list)
        saves_to_export = multiple_choice_input(maximum_save_number)
        AstroLogging.logPrint(saves_to_export)

        do_rename = None
        while do_rename not in ('y', 'n'):
            AstroLogging.logPrint('\nWould you like to rename a save ? (y/n)')
            do_rename = input().lower()
        if do_rename == 'y': rename_saves(container)

        AstroLogging.logPrint(f'\nExtracting saves {str(saves_to_export)}')

        export_saves_path = os.path.join(args.savesPath, 'Steam saves')
        rm_dir_if_exists(export_saves_path)

        # Core function
        container.xbox_to_steam(saves_to_export, export_saves_path)

        AstroLogging.logPrint(f'\nTask completed, press any key to exit')

        wait_and_exit(0)
    except Exception as ex:
        AstroLogging.logPrint(ex)
        AstroLogging.logPrint('', 'exception')
        wait_and_exit(1)
""""""
