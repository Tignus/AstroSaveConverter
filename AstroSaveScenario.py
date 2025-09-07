import os
import glob
import utils
from io import BytesIO
from typing import List
from cogs import AstroLogging as Logger
from cogs import AstroMicrosoftSaveFolder
from cogs import AstroSteamSaveFolder
from cogs.AstroSaveContainer import AstroSaveContainer as Container
from cogs.AstroSave import AstroSave
from cogs.AstroConvType import AstroConvType


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

    Logger.logPrint(f"User choice: {choice_index}", "debug")
    return file_list[choice_index-1]


def print_list_elements(elements):
    for i, container in elements:
        Logger.logPrint(f'\t {i+1}) {container}')


def verify_choice_input(choice, min, max):
    if (choice < min or choice > max):
        raise ValueError


def ask_for_save_folder(conversion_type: AstroConvType) -> str:
    """ Obtains the save folder

    Lets the user pick between automatic save retrieving/copying or
    a custom save folder

    Arguments:
        conversion_type : Type of save conversion (for automatic folder retrieval purpose)

    Returns:
        The save folder path
    """
    while 1:
        try:
            Logger.logPrint("Which folder would you like to work with ?")
            Logger.logPrint("\t1) Automatically detect and copy my save folder (Please close Astroneer first)")
            Logger.logPrint("\t2) Chose a custom folder")

            work_choice = input()
            while work_choice not in ('1', '2'):
                Logger.logPrint(f'\nPlease choose 1 or 2')
                work_choice = input()

            Logger.logPrint(f"User choice: {work_choice}", "debug")
            if work_choice == '1':
                if conversion_type == AstroConvType.WIN2STEAM:
                    astroneer_save_folder = AstroMicrosoftSaveFolder.get_microsoft_save_folder()
                    Logger.logPrint(f'Microsoft folder path: {astroneer_save_folder}', 'debug')
                    save_path = ask_copy_target('MicrosoftAstroneerSavesBackup', 'microsoft')
                else:
                    astroneer_save_folder = AstroSteamSaveFolder.get_steam_save_folder()
                    Logger.logPrint(f'Steam folder path: {astroneer_save_folder}', 'debug')
                    save_path = ask_copy_target('SteamAstroSaveBackup', 'steam')

                utils.copy_files(astroneer_save_folder, save_path)

                Logger.logPrint(f'Save files copied to: {save_path}')

            elif work_choice == '2':
                save_path = ask_custom_folder_path()

            return save_path

        except FileNotFoundError as e:
            Logger.logPrint('\nNo container found in path: ' + save_path)
            Logger.logPrint(e, 'exception')


def ask_copy_target(folder_main_name: str, save_type: str):
    ''' Requests a target folder to the user
    TODO [doc] to explain the folder name format
    Arguments:
        folder_main_name:
        save_type:

    Returns
        ...
    '''
    Logger.logPrint(f'Where would you like to backup your {save_type} save folder ?')
    Logger.logPrint('\t1) New folder on my desktop')
    Logger.logPrint("\t2) New folder in a custom path")

    choice = input()
    while choice not in ('1', '2'):
        Logger.logPrint(f'\nPlease choose 1 or 2')
        choice = input()

    Logger.logPrint(f"User choice: {choice}", "debug")

    if choice == '1':
        # Winpath is needed here because Windows user can have a custom Desktop location
        save_path = utils.get_windows_desktop_path()
    elif choice == '2':
        Logger.logPrint(f'\nEnter your custom folder path:')
        save_path = input()
        Logger.logPrint(f"User choice: {save_path}", "debug")

    return utils.join_paths(save_path, utils.create_folder_name(folder_main_name))


def ask_custom_folder_path() -> str:
    Logger.logPrint(f'\nEnter your custom folder path:')
    path = input()

    if utils.is_folder_a_dir(path):
        Logger.logPrint(f"User choice: {path}", "debug")
        return path
    else:
        Logger.logPrint(f'\nWrong path for save folder, please enter a valid path : ')
        return ask_custom_folder_path()


def print_save_from_container(save_list):
    """ Displays the human readable saves of a container """
    for i, save in enumerate(save_list):
        Logger.logPrint(f'\t {str(i+1)}) {save.name}')


def ask_saves_to_export(save_list: List[AstroSave]) -> List[int]:
    """TODO [doc] explain that this function returns the indexes in the save list and not a sublist of the save_list
    """
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

    Logger.logPrint(f"User choice: {choices}", "debug")

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


def ask_rename_saves(saves_indexes, save_list):
    """ Guide the user in order to rename a save

    :param save_indexes: List of the saves in the save_list you want to rename
    :param save_list: List of the save objects you may rename
    """

    do_rename = None
    while do_rename not in ('y', 'n'):
        Logger.logPrint('\nWould you like to rename a save ? (y/n)')
        do_rename = input().lower()

    Logger.logPrint(f"User choice: {do_rename}", "debug")

    if do_rename == 'y':
        for index in saves_indexes:
            save = save_list[index]
            rename_save(save)


def rename_save(save):
    """ Rename a save
    Rename can be skipped by pressing Enter directly

    :param save: Save object to be renamed
    """
    new_name = None
    while new_name is None:
        new_name = input(f'\nNew name for {save.name.split("$")[0]}: [ENTER = unchanged] > ').upper()
        if (new_name != ''):
            try:
                save.rename(new_name)
            except ValueError:
                new_name = None
                Logger.logPrint(f'Please use only alphanum and a length < 30')

    Logger.logPrint(f"User choice: {new_name}", "debug")


def ask_overwrite_if_file_exists(filename: str, target: str) -> bool:
    file_url = utils.join_paths(target, filename)

    if utils.is_path_exists(file_url):
        do_overwrite = None
        while do_overwrite not in ('y', 'n'):
            Logger.logPrint(f'\nFile {filename} already exists, overwrite it ? (y/n)')
            do_overwrite = input().lower()

        Logger.logPrint(f"User choice: {do_overwrite}", "debug")
        return do_overwrite == 'y'
    else:
        return True


def export_save_to_steam(save: AstroSave, from_path: str, to_path: str) -> None:
    target_full_path = utils.join_paths(to_path, save.get_file_name())
    converted_save = save.convert_to_steam(from_path)
    utils.write_buffer_to_file(target_full_path, converted_save)


def export_save_to_xbox(save: AstroSave, from_file: str, to_path: str) -> None:
    chunk_uuids, converted_chunks = save.convert_to_xbox(from_file)

    chunk_count = len(chunk_uuids)

    if chunk_count >= 10:
        Logger.logPrint(
            f'The selected save contains {chunk_count} which is over the 9 chunks limit AstroSaveconverter can handle yet')
        Logger.logPrint(f'Congrats for having such a huge save, please open an issue on the GitHub :D')

    for i in range(chunk_count):

        # The file name is the HEX upper form of the uuid
        chunk_name = save.chunks_names[i]
        Logger.logPrint(f'UUID as file name: {chunk_name}', "debug")

        target_full_path = utils.join_paths(to_path, chunk_name)
        Logger.logPrint(f'Chunk file written to: {target_full_path}', "debug")

        # Regenerating chunk name if it already exists. Very, very unlikely
        while utils.is_path_exists(target_full_path):
            Logger.logPrint(f'UUID: {chunk_name} already exists ! (omg)', "debug")

            chunk_uuids[i] = save.regenerate_uuid(i)
            chunk_name = save.chunks_names[i]

            Logger.logPrint(f'Regenerated UUID: {chunk_name}', "debug")
            target_full_path = utils.join_paths(to_path, chunk_name)

        # TODO [enhance] raise exception if can't write, catch it then delete all the chunks already written and exit
        utils.write_buffer_to_file(target_full_path, converted_chunks[i])

    # Container is updated only after all the chunks of the save have been written successfully
    container_file_name = Container.get_containers_list(to_path)[0]

    container_full_path = utils.join_paths(to_path, container_file_name)

    with open(container_full_path, "r+b") as container:
        container.read(4)

        current_container_chunk_count = int.from_bytes(container.read(4), byteorder='little')

        new_container_chunk_count = current_container_chunk_count + chunk_count

        container.seek(-4, 1)
        container.write(new_container_chunk_count.to_bytes(4, byteorder='little'))

    chunks_buffer = BytesIO()
    for i in range(chunk_count):

        total_written_len = 0

        encoded_save_name = save.name.encode('utf-16le', errors='ignore')
        total_written_len += chunks_buffer.write(encoded_save_name)

        if chunk_count > 1:
            # Multi-chunks save. Adding metadata, format: '$${i}${chunk_count}$1'
            chunk_metadata = f'$${i}${chunk_count}$1'

            encoded_metadata = chunk_metadata.encode('utf-16le', errors='ignore')
            total_written_len += chunks_buffer.write(encoded_metadata)

        chunks_buffer.write(b"\00" * (144 - total_written_len))

        chunks_buffer.write(chunk_uuids[i].bytes_le)

    Logger.logPrint(f'Editing container: {container_full_path}', "debug")
    utils.append_buffer_to_file(container_full_path, chunks_buffer)


def ask_overwrite_save_while_file_exists(save: AstroSave, target: str) -> None:
    do_overwrite = None
    while not do_overwrite:
        do_overwrite = ask_overwrite_if_file_exists(save.get_file_name(), target)
        if not do_overwrite:
            rename_save(save)


def ask_conversion_type() -> AstroConvType:
    Logger.logPrint(f'\nWhich conversion do you want to do ?')
    Logger.logPrint("\t1) Convert a Microsoft save into a Steam save")
    Logger.logPrint('\t2) Convert a Steam save into a Microsoft save')

    choice = input()
    while choice not in ('1', '2'):
        Logger.logPrint(f'\nPlease choose 1 or 2')
        choice = input()

    Logger.logPrint(f"User choice: {choice}", "debug")
    if choice == '1':
        return AstroConvType.WIN2STEAM
    else:
        return AstroConvType.STEAM2WIN


def backup_win_before_steam_export() -> str:
    Logger.logPrint('\nFor safety reasons, we will now copy your current Microsoft Astroneer saves')
    folders = AstroMicrosoftSaveFolder.find_microsoft_save_folders()
    Logger.logPrint(f"{len(folders)} different Microsoft save folders have been detected. They will all be backed up.")
    backup_path = ask_copy_target('MicrosoftAstroneerSavesBackup', 'microsoft')
    AstroMicrosoftSaveFolder.backup_microsoft_save_folders(folders, backup_path)
    Logger.logPrint(f'Save files copied to: {backup_path}')

    return folders[0]


def ask_microsoft_target_folder() -> str:
    save_folders = []
    try:
        target = os.environ['LOCALAPPDATA'] + '\\Packages\\SystemEraSoftworks*\\SystemAppData\\wgs'
    except KeyError:
        Logger.logPrint("Local Appdata are missing, maybe you're on linux ?")
        Logger.logPrint("Press any key to exit")
        utils.wait_and_exit(1)

    for path in glob.iglob(target):
        save_folders.extend(AstroMicrosoftSaveFolder.get_save_folders_from_path(path))

    if not save_folders:
        raise FileNotFoundError

    if len(save_folders) == 1:
        return save_folders[0]

    Logger.logPrint('\nWhich Microsoft save folder would you like to copy your Steam save to?')

    for i, folder in enumerate(save_folders, 1):
        Logger.logPrint(f"{i}) {folder}")
        Logger.logPrint('Contenu du dossier :')
        details = AstroMicrosoftSaveFolder.get_save_details(folder)
        if details:
            for name, date in details:
                Logger.logPrint(f"\t{name} - {date}")
        else:
            Logger.logPrint("\t<vide>")

    while True:
        choice = input()
        try:
            choice_int = int(choice)
            if 1 <= choice_int <= len(save_folders):
                Logger.logPrint(f"User choice: {choice_int}", "debug")
                return save_folders[choice_int - 1]
        except ValueError:
            pass
        Logger.logPrint(f'Please choose a number between 1 and {len(save_folders)}')
