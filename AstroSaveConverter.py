import argparse
import os
import sys

from cogs.AstroLogging import AstroLogging
from cogs.AstroSaveContainer import AstroSaveContainer


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
        "\t1) Automatically detect and copy my save folder")
    AstroLogging.logPrint("\t2) Chose a custom folder")

    folder_type = input()
    while folder_type not in ('1', '2'):
        AstroLogging.logPrint(f'\nPlease choose 1 or 2')
        folder_type = input()
        AstroLogging.logPrint(f"folder_type {folder_type}", "debug")

    if folder_type == '1':
        AstroLogging.logPrint("This feature does not exist yet :)")
        AstroLogging.logPrint('\nPress any key to exit')
        input()
        exit(0)  # TODO: automatic behaviour
    elif folder_type == '2':
        AstroLogging.logPrint(f'\nEnter your custom folder path')
        save_folder_path = input()
        AstroLogging.logPrint(f"save_folder_path {save_folder_path}", "debug")

        while not os.path.isdir(save_folder_path):
            AstroLogging.logPrint(
                f"\nWrong path for save folder, please enter a valid path : ")
            save_folder_path = input()
            AstroLogging.logPrint(
                f"save_folder_path {save_folder_path}", "debug")

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
            AstroLogging.logPrint(f'\t {str(i + 1)}) {container}')

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


def choose_save_to_export(container):
    """
    Let the user choose the save(s) to export from the container

    The user can choose one or several saves to export.
    Multi-save is supported (separated by commas)
    Ex: 1,2,4

    Arguments:
        container -- Container from which to export the saves

    Returns:
        Returns the list of the saves number to extract

    Exception:
        None
    """
    save_numbers_list = []
    max_save_number = len(container.save_list)
    while save_numbers_list == []:
        AstroLogging.logPrint(
            '\nWhich saves would you like to convert ? (Choose 0 for all of them)')
        AstroLogging.logPrint(
            '(Multi-convert is supported. Ex: "1,2,4")')
        save_numbers = input()
        try:
            for number in save_numbers.split(','):
                number = int(number)
                if (number < 1 or number > max_save_number):
                    raise ValueError
                save_numbers_list.append(number)
            AstroLogging.logPrint(save_numbers_list)
            if 0 in save_numbers_list and len(save_numbers_list) != 1:
                raise ValueError
        except ValueError:
            save_numbers_list = []
            AstroLogging.logPrint(
                f'Please use only values between 1 and {max_save_number} or 0 alone')
    return save_numbers_list


def manage_rename(container):
    """
    Manage wether some saves have to be renamed or not

    Arguments:
        container -- Container from which to rename the saves

    Returns:
        Nothing

    Exception:
        None
    """
    is_rename = None
    while is_rename != 'y' and is_rename != 'n':
        AstroLogging.logPrint('\nWould you like to rename a save ? (y/n)')
        is_rename = input().lower()

    if is_rename == 'y':
        for number in save_numbers_list:
            container.save_list[number - 1].rename()


if __name__ == "__main__":
    try:
        os.system(
            "title AstroSaveConverter - Migrate your Astroneer save from Microsoft to Steam")
    except:
        pass
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "-p", "--savesPath", help="Path from which to read the container and extract the saves", required=False)

        args = parser.parse_args()
        AstroLogging.setup_logging(os.getcwd())

        try:
            if not args.savesPath:
                save_folder_path = get_save_folder()
                container_file_name = check_container_path(save_folder_path)
        except FileNotFoundError as e:
            AstroLogging.logPrint(
                '\nSave folder or container not found, press any key to exit')
            input()
            sys.exit(-1)

        container = AstroSaveContainer(os.path.join(
            save_folder_path, container_file_name))

        AstroLogging.logPrint('Container file loaded successfully !\n')
        container.print_container()

        save_numbers_list = choose_save_to_export(container)

        manage_rename(container)

        AstroLogging.logPrint(f'\nExtracting saves {str(save_numbers_list)}')

        container.xbox_to_steam(save_numbers_list)

        AstroLogging.logPrint(f'\nTask completed, press any key to exit')
        input()
    except Exception as ex:
        AstroLogging.logPrint(ex)
        AstroLogging.logPrint('', 'exception')

        sys.exit()
