import argparse
import os
import sys
import shutil
from datetime import datetime
import re
import glob
import winpath

from cogs.AstroLogging import AstroLogging
from cogs.AstroSaveContainer import AstroSaveContainer


def get_microsoft_save_folder():
    """
    Retrieves the microsoft save folders from %appdata%

    We know that the saves are stored along with a container.* file.
    We look for that specific container by checking if it contains a
    save date in order to return the whole path

    Arguments:
        None

    Returns:
        Returns the list of the microsoft save folder path found in %appdata%

    Exception:
        FileNotFoundError if no save folder is found
    """
    # glob is used to get the path using the wildcard *
    for result in glob.iglob(os.environ['LOCALAPPDATA'] + '\\Packages\\SystemEraSoftworks*\\SystemAppData\\wgs'):
        AstroLogging.logPrint(f'SES path found in appadata: {result}', 'debug')
        SES_appdata_path = result

    microsoft_save_folders = []

    for root, _, files in os.walk(SES_appdata_path):
        # Seeking every file in the SES folder
        for file in files:
            if re.search(r'^container\.', file):
                # We matched a container.* file
                container_full_path = os.path.join(root, file)
                AstroLogging.logPrint(
                    f'Container file found:{container_full_path}', 'debug')

                with open(container_full_path, 'rb') as container:
                    # Decoding the container to check for a date string
                    container_binary_content = container.read()
                    container_text = container_binary_content.decode(
                        'utf-16le', errors='ignore')

                    # Save date matches $YYYY.MM.dd
                    if re.search(r'\$\d{4}\.\d{2}\.\d{2}', container_text):
                        AstroLogging.logPrint(
                            f'Matching save folder {root}', 'debug')
                        microsoft_save_folders.append(root)

    if not microsoft_save_folders:
        AstroLogging.logPrint(f'No save folder found.', 'debug')
        raise FileNotFoundError
    elif len(microsoft_save_folders) != 1:
        # We are not supposed to have more than one save folder
        AstroLogging.logPrint(
            f'More than one save folders was found:\n {microsoft_save_folders}', 'debug')

    return microsoft_save_folders


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
    AstroLogging.logPrint(
        "\t1) Automatically detect and copy my save folder (Please close Astroneer first)")
    AstroLogging.logPrint("\t2) Chose a custom folder")

    folder_type = input()
    while folder_type not in ('1', '2'):
        AstroLogging.logPrint(f'\nPlease choose 1 or 2')
        folder_type = input()
        AstroLogging.logPrint(f'folder_type {folder_type}', 'debug')

    if folder_type == '1':
        microsoft_save_folders = get_microsoft_save_folder()

        if len(microsoft_save_folders) != 1:
            AstroLogging.logPrint(
                f'\nToo many save folders found ! Please use custom folder mode.')
            AstroLogging.logPrint('\nPress any key to exit')
            input()
            exit(-1)

        AstroLogging.logPrint(
            'Where would you like to copy your save folder ?')
        AstroLogging.logPrint(
            '\t1) New folder on my desktop')
        AstroLogging.logPrint("\t2) New folder in a custom path")

        copy_choice = input()
        while copy_choice not in ('1', '2'):
            AstroLogging.logPrint(f'\nPlease choose 1 or 2')
            copy_choice = input()
            AstroLogging.logPrint(f'copy_choice {copy_choice}', 'debug')

        # Using date and time to create a unique folder name
        now = datetime.now().strftime('%Y.%m.%d-%H.%M')
        astrosave_folder_name = f'AstroSaveFolder_{now}'

        if copy_choice == '1':
            # Winpath is needed here because Windows user can have a custom Desktop location
            astrosave_folder_path = winpath.get_desktop()
        elif copy_choice == '2':
            AstroLogging.logPrint(f'\nEnter your custom folder path:')
            astrosave_folder_path = input()
            AstroLogging.logPrint(
                f'astrosave_folder_path {astrosave_folder_path}', 'debug')

        save_folder_path = os.path.join(
            astrosave_folder_path, astrosave_folder_name)

        AstroLogging.logPrint(
            f'Microsoft folder path: {microsoft_save_folders[0]}', 'debug')
        AstroLogging.logPrint(
            f'Save files copied to: {save_folder_path}')

        # Creating the new folder and copying the saves and container into it
        if os.path.isdir(save_folder_path):
            shutil.rmtree(save_folder_path)
        shutil.copytree(microsoft_save_folders[0], save_folder_path)

    elif folder_type == '2':
        AstroLogging.logPrint(f'\nEnter your custom folder path:')
        save_folder_path = input()
        AstroLogging.logPrint(f'save_folder_path {save_folder_path}', 'debug')

        while not os.path.isdir(save_folder_path):
            AstroLogging.logPrint(
                f'\nWrong path for save folder, please enter a valid path : ')
            save_folder_path = input()
            AstroLogging.logPrint(
                f'save_folder_path {save_folder_path}', 'debug')

    return save_folder_path


def get_container_list(path):
    """
    List all containers in a folder
    Arguments:
        path -- path for search containers
    Returns:
        Returns a list of all containers found (only filename of container)
    Exception:
        None
    """
    list_containers = []

    for file in [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]:
        if file.rfind("container") != -1:
            list_containers.append(file)

    if not list_containers:
        AstroLogging.logPrint('\nNo container found in path: ' + path)
    elif len(list_containers) == 1:
        AstroLogging.logPrint('\nOne container found', 'debug')
    else:
        AstroLogging.logPrint('\nContainers found:')
        for i, container in enumerate(list_containers):
            AstroLogging.logPrint(f'\t {i+1}) {container}')

    return list_containers


def check_container_path(path):
    """
    Defines the container to use

    Find every *container* file in the
    given path and make the user chose one

    Arguments:
        path -- path where to look for the containers

    Returns:
        Returns the chosen container filename

    Exception:
        Raise FileNotFoundError if no container is found
    """
    list_containers = []
    list_containers = get_container_list(path)

    if len(list_containers) == 0:
        raise FileNotFoundError
    if len(list_containers) == 1:
        container_name = list_containers[0]
    else:

        min_container_number = 1
        max_container_number = len(list_containers)
        container_index = 0

        while container_index == 0:
            AstroLogging.logPrint(
                '\nWhich container would you like to convert ?')
            container_index = input()
            try:
                container_index = int(container_index)
                if (container_index < min_container_number or container_index > max_container_number):
                    raise ValueError
            except ValueError:
                container_index = 0
                AstroLogging.logPrint(
                    f'Please use only values between {min_container_number} and {max_container_number}')
        container_name = list_containers[container_index-1]
    return container_name


def process_multiple_choices_input(choices, max_value):
    choices = choices.split(',').map(lambda x: int(x))
    choices = [number for number in choices if number >= 0 or number < max_value]
    return choices


def verify_choice_input(choices):
    if len(choices) == 0:
        raise ValueError

    if 0 in choices and len(choices) != 1:
        raise ValueError

    return choices


def multiple_choice_input(maximum_value):
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
        process_multiple_choices_input(choices, maximum_value)

        try:
            verify_choice_input(choices)
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


def get_args():
        parser = argparse.ArgumentParser()

        parser.add_argument(
            "-p", "--savesPath", help="Path from which to read the container and extract the saves", required=False)

        args = parser.parse_args()

        # Default values
        args.savesPath = args.savesPath or get_save_folder()

        return args


def exit(code):
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
        container_file_name = check_container_path(args.savesPath)
    except FileNotFoundError as e:
        AstroLogging.logPrint('\nSave folder or container not found, press any key to exit')
        AstroLogging.logPrint(e, 'exception')
        exit(1)

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
        container.xbox_to_steam(saves_to_export, export_saves_path)

        AstroLogging.logPrint(f'\nTask completed, press any key to exit')

        exit(0)
    except Exception as ex:
        AstroLogging.logPrint(ex)
        AstroLogging.logPrint('', 'exception')
        exit(1)

