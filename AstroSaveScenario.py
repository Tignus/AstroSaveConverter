"""Interactive workflow for selecting and converting Astroneer saves."""

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


def ask_for_containers_to_convert(containers: List[str]) -> str:
    """Ask the user which container to convert.

    Args:
        containers: List of detected container filenames.

    Returns:
        str: Chosen container filename.
    """
    question = '\nWhich container would you like to convert ?'
    return ask_user_to_choose_in_a_list(question, containers)


def ask_user_to_choose_in_a_list(text: str, file_list: List[str]) -> str:
    """Display a list and return the user's choice.

    Args:
        text: Prompt presented to the user.
        file_list: Options the user can choose from.

    Returns:
        str: The element selected by the user.

    Raises:
        ValueError: If the user selects a value outside the allowed range.
    """
    max_container_number = len(file_list)
    min_container_number = 1
    choice_index = 0

    while choice_index == 0:
        Logger.logPrint('\nWhich container would you like to convert ?')
        print_list_elements(file_list)
        choice_index = input()
        Logger.logPrint(f"User choice: {choice_index}", "debug")
        try:
            choice_index = int(choice_index)
            verify_choice_input(choice_index, min_container_number, max_container_number)
        except ValueError:
            choice_index = 0
            Logger.logPrint(f'Please use only values between {min_container_number} and {max_container_number}')

    return file_list[choice_index-1]


def print_list_elements(elements: List[str]) -> None:
    """Log each element of a list with its index.

    Args:
        elements: Sequence of strings to display.
    """
    for i, container in enumerate(elements):
        Logger.logPrint(f'\t {i+1}) {container}')


def verify_choice_input(choice: int, min_value: int, max_value: int) -> None:
    """Ensure a numeric choice is within bounds.

    Args:
        choice: Value provided by the user.
        min_value: Minimum allowed value.
        max_value: Maximum allowed value.

    Raises:
        ValueError: If ``choice`` is outside the allowed range.
    """
    if choice < min_value or choice > max_value:
        raise ValueError


def ask_for_save_folder(conversion_type: AstroConvType) -> str:
    """Determine which folder should be used for conversion.

    Depending on ``conversion_type`` the user can automatically copy the
    detected save folder or provide a custom path.

    Args:
        conversion_type: Desired conversion direction.

    Returns:
        str: Path to work with.

    Raises:
        FileNotFoundError: If no save folder can be located automatically.
    """
    while 1:
        try:
            Logger.logPrint("Which folder would you like to work with ?")
            Logger.logPrint("\t1) Automatically detect and copy my save folder (Please close Astroneer first)")
            Logger.logPrint("\t2) Chose a custom folder")

            work_choice = input()
            Logger.logPrint(f"User choice: {work_choice}", "debug")
            while work_choice not in ('1', '2'):
                Logger.logPrint(f'\nPlease choose 1 or 2')
                work_choice = input()
                Logger.logPrint(f"User choice: {work_choice}", "debug")
            if work_choice == '1':
                if conversion_type == AstroConvType.WIN2STEAM:
                    try:
                        astroneer_save_folder = AstroMicrosoftSaveFolder.get_microsoft_save_folder()
                        Logger.logPrint(f'Microsoft folder path: {astroneer_save_folder}', 'debug')
                        save_path = ask_copy_target('MicrosoftAstroneerSavesBackup', 'Microsoft')
                        utils.copy_files(astroneer_save_folder, save_path)
                        Logger.logPrint(f'Save files copied to: {save_path}')
                    except FileNotFoundError:
                        Logger.logPrint('\nNo Microsoft save folder detected')
                        Logger.logPrint('\t1) Backup converted save to a new folder on the Desktop')
                        Logger.logPrint('\t2) Backup to a custom path')
                        Logger.logPrint('\t3) Cancel and launch the Microsoft version of Astroneer before retrying')
                        choice = input()
                        Logger.logPrint(f"User choice: {choice}", "debug")
                        while choice not in ('1', '2', '3'):
                            Logger.logPrint(f'\nPlease choose 1, 2 or 3')
                            choice = input()
                            Logger.logPrint(f"User choice: {choice}", "debug")
                        if choice == '3':
                            continue
                        save_path = ask_copy_target('MicrosoftAstroneerSavesBackup', 'Microsoft')
                else:
                    astroneer_save_folder = AstroSteamSaveFolder.get_steam_save_folder()
                    Logger.logPrint(f'Steam folder path: {astroneer_save_folder}', 'debug')
                    save_path = ask_copy_target('SteamAstroSaveBackup', 'Steam')
                    utils.copy_files(astroneer_save_folder, save_path)
                    Logger.logPrint(f'Save files copied to: {save_path}')

            elif work_choice == '2':
                save_path = ask_custom_folder_path()

            return save_path

        except FileNotFoundError as e:
            Logger.logPrint('\nNo container found in path: ' + save_path)
            Logger.logPrint(e, 'exception')


def ask_copy_target(folder_main_name: str, save_type: str) -> str:
    """Request a destination folder for backups.

    Args:
        folder_main_name: Base name for the created folder.
        save_type: Label describing the platform (e.g. ``"Steam"``).

    Returns:
        str: Full path where the backup should be created.
    """
    Logger.logPrint(f'Where would you like to backup your {save_type.capitalize()} save folder ?')
    Logger.logPrint('\t1) New folder on my desktop')
    Logger.logPrint("\t2) New folder in a custom path")

    choice = input()
    Logger.logPrint(f"User choice: {choice}", "debug")
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
    """Ask the user for a custom directory path.

    Returns:
        str: A valid directory path provided by the user.
    """
    while True:
        Logger.logPrint(f'\nEnter your custom folder path:')
        input_path = input()
        path = os.path.normpath(input_path)
        path = os.path.expanduser(path)
        Logger.logPrint(f"User choice: {path}", "debug")

        if utils.is_folder_a_dir(path):
            return path
        Logger.logPrint('\nWrong path for save folder, please enter a valid path : ', 'error')


def print_save_from_container(save_list: List[AstroSave]) -> None:
    """Display saves contained in a container.

    Args:
        save_list: List of ``AstroSave`` objects to print.
    """
    for i, save in enumerate(save_list):
        Logger.logPrint(f'\t {str(i+1)}) {save.name}')


def ask_saves_to_export(save_list: List[AstroSave], platform_label: str) -> List[int]:
    """Prompt the user to select saves for export.

    Args:
        save_list: List of available saves.
        platform_label: Label for the originating platform.

    Returns:
        List[int]: Indexes of saves selected by the user.
    """
    Logger.logPrint(f"{platform_label.capitalize()} saves list :")
    print_save_from_container(save_list)
    Logger.logPrint('\nWhich saves would you like to convert ? (Choose 0 for all of them)')
    Logger.logPrint('(Multi-convert is supported. Ex: "1,2,4")')

    maximum_save_number = len(save_list)
    return ask_for_multiple_choices(maximum_save_number)


def ask_for_multiple_choices(maximum_value: int) -> List[int]:
    """Let the user choose multiple numbers between 0 and ``maximum_value``.

    The user's input is validated and converted to zero-based indexes.

    Args:
        maximum_value: Highest selectable value.

    Returns:
        List[int]: Selected indexes. ``[-1]`` indicates all values were chosen.

    Raises:
        ValueError: If input is malformed.
    """
    choices: List[int] = []
    while not choices:
        choices = input()
        Logger.logPrint(f"User choice: {choices}", "debug")
        try:
            choices = process_multiple_choices_input(choices)
            verify_choices_input(choices, maximum_value)
        except ValueError:
            choices = []
            Logger.logPrint(
                f'Please use only values between 1 and {maximum_value} or 0 alone'
            )

    if choices == [-1]:
        return list(range(0, maximum_value))
    return choices


def process_multiple_choices_input(choices: str) -> List[int]:
    """Convert a comma-separated string of numbers to a list of indexes.

    Args:
        choices: Comma-separated numbers provided by the user.

    Returns:
        List[int]: Parsed zero-based indexes.
    """
    split_choices = choices.split(',')
    return [int(x) - 1 for x in split_choices]


def verify_choices_input(choices: List[int], max_value: int) -> None:
    """Validate a list of numeric choices.

    Args:
        choices: Parsed choices from ``process_multiple_choices_input``.
        max_value: Maximum allowed value (exclusive).

    Raises:
        ValueError: If the choices list is empty or values are out of range.
    """
    if len(choices) == 0:
        raise ValueError

    if -1 in choices and len(choices) != 1:
        raise ValueError

    for choice in choices:
        if choice > max_value - 1 or choice < -1:
            raise ValueError


def ask_rename_saves(saves_indexes: List[int], save_list: List[AstroSave]) -> None:
    """Guide the user through optional save renaming.

    Args:
        saves_indexes: Indexes of saves in ``save_list`` to consider.
        save_list: Available saves.
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


def rename_save(save: AstroSave) -> None:
    """Prompt the user for a new name for a save.

    Args:
        save: Save object to rename.

    Raises:
        ValueError: If the provided name is invalid.
    """
    new_name = None
    while new_name is None:
        new_name = input(
            f'\nNew name for {save.name.split("$")[0]}: [ENTER = unchanged] > '
        ).upper()
        Logger.logPrint(f"User choice: {new_name}", "debug")
        if new_name != '':
            try:
                save.rename(new_name)
            except ValueError:
                new_name = None
                Logger.logPrint('Please use only alphanum and a length < 30')


def ask_overwrite_if_file_exists(filename: str, target: str) -> bool:
    """Ask the user whether to overwrite an existing file.

    Args:
        filename: Name of the file to check.
        target: Directory where the file would be written.

    Returns:
        bool: ``True`` if the file may be overwritten, ``False`` otherwise.
    """
    file_url = utils.join_paths(target, filename)

    if utils.is_path_exists(file_url):
        do_overwrite = None
        while do_overwrite not in ('y', 'n'):
            Logger.logPrint(f'\nFile {filename} already exists, overwrite it ? (y/n)')
            do_overwrite = input().lower()
            Logger.logPrint(f"User choice: {do_overwrite}", "debug")

        return do_overwrite == 'y'
    return True


def export_save_to_steam(save: AstroSave, from_path: str, to_path: str) -> str:
    """Export a Microsoft/Xbox save to the Steam format.

    Args:
        save: ``AstroSave`` instance to export.
        from_path: Directory where the chunk files are located.
        to_path: Destination directory for the Steam save.

    Returns:
        str: Full path to the exported save file.
    """
    target_full_path = utils.join_paths(to_path, save.get_file_name())
    converted_save = save.convert_to_steam(from_path)
    utils.write_buffer_to_file(target_full_path, converted_save)
    return target_full_path


def export_save_to_xbox(save: AstroSave, from_file: str, to_path: str) -> None:
    """Export a Steam save into multiple Xbox chunk files.

    Args:
        save: ``AstroSave`` instance to convert.
        from_file: Path to the Steam ``.savegame`` file.
        to_path: Destination directory for the Xbox chunks.

    Raises:
        FileExistsError: If generated chunk names already exist and cannot be
            regenerated.
    """
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
    """Prompt to overwrite a save file, renaming if necessary.

    Args:
        save: Save to potentially overwrite.
        target: Directory where the save would be written.
    """
    do_overwrite = None
    while not do_overwrite:
        do_overwrite = ask_overwrite_if_file_exists(save.get_file_name(), target)
        if not do_overwrite:
            rename_save(save)


def ask_conversion_type() -> AstroConvType:
    """Ask the user which conversion direction to use.

    Returns:
        AstroConvType: Selected conversion type.
    """
    Logger.logPrint(f'\nWhich conversion do you want to do ?')
    Logger.logPrint("\t1) Convert a Microsoft save into a Steam save")
    Logger.logPrint('\t2) Convert a Steam save into a Microsoft save')

    choice = input()
    Logger.logPrint(f"User choice: {choice}", "debug")
    while choice not in ('1', '2'):
        Logger.logPrint(f'\nPlease choose 1 or 2')
        choice = input()
        Logger.logPrint(f"User choice: {choice}", "debug")
    if choice == '1':
        return AstroConvType.WIN2STEAM
    return AstroConvType.STEAM2WIN


def backup_win_before_steam_export() -> str:
    """Backup existing Microsoft saves before exporting from Steam.

    Returns:
        str: Path to the first detected Microsoft save folder.

    Raises:
        FileNotFoundError: If no Microsoft save folders are discovered.
    """
    Logger.logPrint('\nFor safety reasons, we will now copy your current Microsoft Astroneer saves')
    try:
        folders = AstroMicrosoftSaveFolder.find_microsoft_save_folders()
    except FileNotFoundError:
        Logger.logPrint('No Microsoft save folders were found. Choose where to place the converted saves.')
        Logger.logPrint('\t1) Backup converted save to a new folder on the Desktop')
        Logger.logPrint('\t2) Backup to a custom path')
        Logger.logPrint('\t3) Cancel and launch the Microsoft version of Astroneer before retrying')
        choice = input()
        Logger.logPrint(f"User choice: {choice}", "debug")
        while choice not in ('1', '2', '3'):
            Logger.logPrint('\nPlease choose 1, 2 or 3')
            choice = input()
            Logger.logPrint(f"User choice: {choice}", "debug")
        if choice == '3':
            Logger.logPrint('Launch the Microsoft version of Astroneer once, then relaunch AstroSaveConverter.')
            return ''
        backup_path = ask_copy_target('MicrosoftAstroneerSavesBackup', 'Microsoft')
        return backup_path
    Logger.logPrint(f"{len(folders)} different Microsoft save folders have been detected. They will all be backed up.")
    backup_path = ask_copy_target('MicrosoftAstroneerSavesBackup', 'Microsoft')
    AstroMicrosoftSaveFolder.backup_microsoft_save_folders(folders, backup_path)
    Logger.logPrint(f'Save files copied to: {backup_path}')

    return folders[0]


def ask_microsoft_target_folder() -> str:
    """Ask the user which Microsoft save folder to use as target.

    Returns:
        str: Selected Microsoft save folder path.

    Raises:
        FileNotFoundError: If no Microsoft save folders are found.
    """
    save_folders: List[str] = []
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
        Logger.logPrint(f"\t{i}) {folder}")
        Logger.logPrint('\tFolder content:')
        details = AstroMicrosoftSaveFolder.get_save_details(folder)
        if details:
            for name, date in details:
                Logger.logPrint(f"\t\t{name} - {date}")
        else:
            Logger.logPrint("\t\t<vide>")

    while True:
        choice = input()
        try:
            choice_int = int(choice)
            if 1 <= choice_int <= len(save_folders):
                break
        except ValueError:
            pass
        Logger.logPrint(f'Please choose a number between 1 and {len(save_folders)}')

    Logger.logPrint(f"User choice: {choice}", "debug")
    return save_folders[choice_int - 1]
