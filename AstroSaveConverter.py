import argparse
import os
import sys

from cogs.AstroLogging import AstroLogging
from cogs.AstroSaveContainer import AstroSaveContainer
"""
D

I

Arguments:

Returns:
    Returns 

Exception:
    None
"""


def check_container_path(path):
    """
    Defines the container to use

    If the path variable is empty, find every *container* file in the
    current directory and make the user chose one

    Arguments:
        path -- current known path for the container

    Returns:
        Returns "path" if it was non-empty
        Else returns the chosen container

    Exception:
        Raise FileNotFoundError if no container is found
    """
    list_containers = []

    for file in os.listdir():
        if file.rfind("container") != -1:
            list_containers.append(file)

        if len(list_containers) == 0:
            raise FileNotFoundError

        AstroLogging.logPrint('\nContainers found:')
        for i, container in enumerate(list_containers):
            AstroLogging.logPrint(f'\t {str(i+1)}) {container}')

    min_container_number = 1
    max_container_number = len(list_containers)
    path_index = 0

    while path_index == 0:
        AstroLogging.logPrint(
            '\nWhich container would you like to convert ?')
        path_index = input()
        try:
            path_index = int(path_index)
            if (path_index < min_container_number or path_index > max_container_number):
                raise ValueError
        except ValueError:
            path_index = 0
            AstroLogging.logPrint(
                f'Please use only values between {min_container_number} and {max_container_number}')

    path = list_containers[path_index-1]
    return path


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
            "-f", "--fileContainer", help="File container to parse", required=False)

        args = parser.parse_args()

        path = os.getcwd()
        # TODO verifier si le dossier courant est un sous-dossier de %appadata% et warning
        # TODO quelquepart: si qqun rentre "connard" dans un prompt, insulter copieusement EmptyProfile
        AstroLogging.setup_logging(path)

        try:
            if not args.fileContainer:
                fileContainer = check_container_path(args.fileContainer)
        except FileNotFoundError as e:
            AstroLogging.logPrint('\nNo container found, press a key to exit')
            input()
            sys.exit(-1)

        container = AstroSaveContainer(fileContainer)

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
