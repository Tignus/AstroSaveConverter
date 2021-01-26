from cogs.AstroSaveContainer import AstroSaveContainer as Container
from cogs import AstroLogging as Logger
import utils
from errors import MultipleFolderFoundError
from cogs import AstroMicrosoftSaveFolder


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
        Logger.logPrint('\nWhich container would you like to convert ?')
        print_list_elements(file_list)
        choice_index = input()
        try:
            choice_index = int(choice_index)
            verify_choice_input(choice_index, min_container_number, max_container_number)
        except ValueError:
            choice_index = 0
            Logger.logPrint(f'Please use only values between {min_container_number} and {max_container_number}')

    return file_list[choice_index-1]


def print_list_elements(elements):
    for i, container in elements:
        Logger.logPrint(f'\t {i+1}) {container}')


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
            Logger.logPrint("Which  folder would you like to work with ?")
            Logger.logPrint("\t1) Automatically detect and copy my save folder (Please close Astroneer first)")
            Logger.logPrint("\t2) Chose a custom folder")

            work_choice = input()
            while work_choice not in ('1', '2'):
                Logger.logPrint(f'\nPlease choose 1 or 2')
                work_choice = input()
                Logger.logPrint(f'folder_type {work_choice}', 'debug')

            if work_choice == '1':
                microsoft_save_folder = AstroMicrosoftSaveFolder.get_microsoft_save_folder()
                Logger.logPrint(f'Microsoft folder path: {microsoft_save_folder}', 'debug')

                save_path = ask_copy_target()
                utils.copy_files(microsoft_save_folder, save_path)

                Logger.logPrint(f'Save files copied to: {save_path}')

            elif work_choice == '2':
                save_path = ask_custom_folder_path()

            return save_path

        except MultipleFolderFoundError:
            Logger.logPrint(f'\nToo many save folders found ! Please use custom folder mode.')
        except FileNotFoundError as e:
            Logger.logPrint('\nNo container found in path: ' + save_path)
            Logger.logPrint(e, 'exception')

def ask_copy_target():
    Logger.logPrint('Where would you like to copy your save folder ?')
    Logger.logPrint('\t1) New folder on my desktop')
    Logger.logPrint("\t2) New folder in a custom path")

    choice = input()
    while choice not in ('1', '2'):
        Logger.logPrint(f'\nPlease choose 1 or 2')
        choice = input()
        Logger.logPrint(f'copy_choice {choice}', 'debug')

    if choice == '1':
        # Winpath is needed here because Windows user can have a custom Desktop location
        save_path = utils.get_windows_desktop_path()
    elif choice == '2':
        Logger.logPrint(f'\nEnter your custom folder path:')
        save_path = input()
        Logger.logPrint(f'save_path {save_path}', 'debug')

    return utils.join_paths(save_path, utils.create_folder_name('AstroSaveFolder'))


def ask_custom_folder_path() -> str:
    Logger.logPrint(f'\nEnter your custom folder path:')
    path = input()
    Logger.logPrint(f'save_folder_path {path}', 'debug')

    if utils.is_folder_a_dir(path):
        return path
    else:
        Logger.logPrint(f'\nWrong path for save folder, please enter a valid path : ')
        return ask_custom_folder_path()


def print_save_from_container(save_list):
    """ Displays the human readable saves of a container """
    for i, save in enumerate(save_list):
        Logger.logPrint(f'\t {str(i+1)}) {save.name}')


def ask_saves_to_export(save_list):
    Logger.logPrint('Extracted save list :')
    print_save_from_container(save_list)
    Logger.logPrint('\nWhich saves would you like to convert ? (Choose 0 for all of them)')
    Logger.logPrint('(Multi-convert is supported. Ex: "1,2,4")')

    maximum_save_number = len(save_list)
    saves_to_export = ask_for_multiple_choices(maximum_save_number)

    return saves_to_export


def ask_for_multiple_choices(maximum_value) -> list:
    """ Let the user choose multiple numbers between 0 and a maximum value

    If the user choice is 0 then return an array with all values,
    the user choices are reduce by 1 in order to match future array indexes

    :Example:

    User choices:
    -  [1,2,4]  - returns 0, 1, 2
    -  [0]      - returns all choices

    :return: The list of numbers
    :exception: None (repeat until the choices are valid)
    """
    choices = []
    while not choices:
        choices = input()
        try:
            choices = process_multiple_choices_input(choices)
            verify_choices_input(choices, maximum_value)
        except ValueError:
            choices = []
            Logger.logPrint(f'Please use only values between 1 and {maximum_value} or 0 alone')

    if choices == [-1]:
        return list(range(0, maximum_value))
    else:
        return choices


def process_multiple_choices_input(choices) -> list:
    choices = choices.split(',')
    choices = [int(x) - 1 for x in choices]

    return choices


def verify_choices_input(choices, max_value):
    if len(choices) == 0:
        raise ValueError

    if -1 in choices and len(choices) != 1:
        raise ValueError

    for choice in choices:
        if (choice > max_value - 1 or choice < -1):
            raise ValueError


def ask_rename_saves(saves_indexes, container):
    do_rename = None
    while do_rename not in ('y', 'n'):
        Logger.logPrint('\nWould you like to rename a save ? (y/n)')
        do_rename = input().lower()

    if do_rename == 'y':
        for index in saves_indexes:
            save = container.save_list[index]
            rename_save(save)


def rename_save(save):
    """ Guide user in order to rename a save

    :param save_indexe: Index of the save in the container.save_list you want to rename
    :param container: Container from which to rename the save
    """
    new_name = None
    while not new_name:
        new_name = input(f'\nNew name for {save.name.split("$")[0]}: [ENTER = unchanged] > ').upper()
        if (new_name == ''): new_name = save.name
        try:
            save.rename(new_name)
        except ValueError:
            new_name = None
            Logger.logPrint(f'Please use only alphanum and a length < 30')


def ask_overwrite_if_file_exists(filename, target):
    file_url = utils.join_paths(target, filename)

    if utils.is_folder_exists(file_url):
        do_overwrite = None
        while do_overwrite not in ('y', 'n'):
            Logger.logPrint(f'\nFile {filename} already exists, overwrite it ? (y/n)')
            do_overwrite = input().lower()

        return do_overwrite == 'y'
    else:
        return True


def export_saves(container, saves_to_export, from_path, to_path):
    for save_index in saves_to_export:
        save = container.save_list[save_index]

        ask_overwrite_save_while_file_exists(save, to_path)

        Logger.logPrint(f'Container: {container.full_path} Export to: {to_path}', "debug")

        target_full_path = utils.join_paths(to_path, save.get_file_name())
        converted_save = save.convert_to_steam(from_path)
        utils.write_buffer_to_file(target_full_path, converted_save)

        Logger.logPrint(f"\nSave {save.name} has been exported succesfully.")


def ask_overwrite_save_while_file_exists(save, target):
    do_overwrite = None
    while not do_overwrite:
        do_overwrite = ask_overwrite_if_file_exists(save.get_file_name(), target)
        if not do_overwrite:
            rename_save(save)
