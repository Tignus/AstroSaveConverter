from cogs.AstroSaveContainer import AstroSaveContainer
from cogs.AstroLogging import AstroLogging
import utils
from cogs.AstroSaveErrors import MultipleFolderFoundError
from cogs import AstroMicrosoftSaveFolder

def ask_for_container(save_path = None):
    save_path = None
    while not save_path:
        try:
            save_path = ask_for_save_folder()
            containers_list = AstroSaveContainer.get_containers_list(save_path)
        except FileNotFoundError as e:
            AstroLogging.logPrint('\nNo container found in path: ' + save_path)
            AstroLogging.logPrint(e, 'exception')

    AstroLogging.logPrint('\nContainers found:' + str(containers_list))
    container_name = ask_for_containers_to_convert(containers_list) if len(containers_list) > 1 else containers_list[0]

    container = AstroSaveContainer(utils.join_paths(save_path, container_name))

    return container


def ask_for_containers_to_convert(containers):
    question = '\nWhich container would you like to convert ?'
    return ask_user_to_choose_in_a_list(question, containers)


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


def print_list_elements(elements):
    for i, container in elements:
        AstroLogging.logPrint(f'\t {i+1}) {container}')


def verify_choice_input(choice, min, max):
    if (choice < min or choice > max):
        raise ValueError


def ask_for_save_folder():
    """ Obtains the save folder

    Lets the user pick between automatic save retrieving/copying or
    a custom save folder

    :return: The save folder path
    """
    while 1:
        try:
            AstroLogging.logPrint("Which  folder would you like to work with ?")
            AstroLogging.logPrint("\t1) Automatically detect and copy my save folder (Please close Astroneer first)")
            AstroLogging.logPrint("\t2) Chose a custom folder")

            work_choice = input()
            while work_choice not in ('1', '2'):
                AstroLogging.logPrint(f'\nPlease choose 1 or 2')
                work_choice = input()
                AstroLogging.logPrint(f'folder_type {work_choice}', 'debug')

            if work_choice == '1':
                microsoft_save_folder = AstroMicrosoftSaveFolder.get_microsoft_save_folder()
                AstroLogging.logPrint(f'Microsoft folder path: {microsoft_save_folder}', 'debug')

                save_path = ask_copy_target()
                utils.copy_files(microsoft_save_folder, save_path)

                AstroLogging.logPrint(f'Save files copied to: {save_path}')

            elif work_choice == '2':
                save_path = ask_custom_folder_path()

            return save_path

        except MultipleFolderFoundError:
            AstroLogging.logPrint(f'\nToo many save folders found ! Please use custom folder mode.')


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
        save_path = utils.get_windows_desktop_path()
    elif choice == '2':
        AstroLogging.logPrint(f'\nEnter your custom folder path:')
        save_path = input()
        AstroLogging.logPrint(f'save_path {save_path}', 'debug')

    return utils.join_paths(save_path, utils.create_folder_name('AstroSaveFolder'))


def ask_custom_folder_path() -> str:
    AstroLogging.logPrint(f'\nEnter your custom folder path:')
    path = input()
    AstroLogging.logPrint(f'save_folder_path {path}', 'debug')

    if utils.is_folder_a_dir(path):
        return path
    else:
        AstroLogging.logPrint(f'\nWrong path for save folder, please enter a valid path : ')
        return ask_custom_folder_path()


def ask_saves_to_export(container):
    AstroLogging.logPrint('\nWhich saves would you like to convert ? (Choose 0 for all of them)')
    AstroLogging.logPrint('(Multi-convert is supported. Ex: "1,2,4")')

    maximum_save_number = len(container.save_list)
    saves_to_export = ask_for_multiple_choices(maximum_save_number)

    return saves_to_export


def ask_for_multiple_choices(maximum_value) -> list:
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

        if choices == [0]:
            return list(range(0, maximum_value))
        else:
            return choices


def process_multiple_choices_input(choices, max_value) -> list:
    choices = choices.split(',').map(lambda x: int(x))
    choices = [number - 1 for number in choices if number >= 0 or number < max_value]
    return choices


def verify_choices_input(choices):
    if len(choices) == 0:
        raise ValueError

    if -1 in choices and len(choices) != 1:
        raise ValueError


def ask_rename_container(saves, container):
    do_rename = None
    while do_rename not in ('y', 'n'):
        AstroLogging.logPrint('\nWould you like to rename a save ? (y/n)')
        do_rename = input().lower()
    if do_rename == 'y': rename_saves(saves, container)


def rename_saves(index_to_rename, container):
    """ Rename all the list of save in the container

    :param container: Container from which to rename the saves
    """
    for i in index_to_rename:
        container.save_list[i].rename()

