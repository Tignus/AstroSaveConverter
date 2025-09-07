import os
import utils
from argparse import ArgumentParser, Namespace
import AstroSaveScenario as Scenario
from cogs import AstroLogging as Logger
from cogs.AstroSaveContainer import AstroSaveContainer as Container
from cogs.AstroSave import AstroSave
from cogs.AstroConvType import AstroConvType
from cogs.LoadingBar import LoadingBar


def get_args() -> Namespace:
    parser = ArgumentParser()

    parser.add_argument(
        "-p", "--savesPath", help="Path from which to read the container and extract the saves", required=False)

    args = parser.parse_args()

    return args


def windows_to_steam_conversion(original_save_path: str) -> None:
    containers_list = Container.get_containers_list(original_save_path)

    Logger.logPrint('\nContainers found:' + str(containers_list))
    container_name = Scenario.ask_for_containers_to_convert(
        containers_list) if len(containers_list) > 1 else containers_list[0]
    container_url = utils.join_paths(original_save_path, container_name)

    Logger.logPrint('\nInitializing Astroneer save container...')
    container = Container(container_url)
    Logger.logPrint(f'Detected chunks: {container.chunk_count}')

    Logger.logPrint('Container file loaded successfully !\n')

    saves_to_export = Scenario.ask_saves_to_export(container.save_list)

    Scenario.ask_rename_saves(saves_to_export, container.save_list)

    to_path = utils.join_paths(original_save_path, 'Steam saves')
    utils.make_dir_if_doesnt_exists(to_path)

    Logger.logPrint(f'\nExtracting saves {str([i+1 for i in saves_to_export])}')
    Logger.logPrint(f'Container: {container.full_path} Export to: {to_path}', "debug")

    for save_index in saves_to_export:
        save = container.save_list[save_index]

        Scenario.ask_overwrite_save_while_file_exists(save, to_path)
        Scenario.export_save_to_steam(save, original_save_path, to_path)

        Logger.logPrint(f"\nSave {save.name} has been exported succesfully.")


def steam_to_windows_conversion(original_save_path: str) -> None:
    Logger.logPrint('\n\n/!\\ WARNING /!\\')
    Logger.logPrint('/!\\ Astroneer needs to be closed longer than 20 seconds before we can start exporting your saves /!\\')
    Logger.logPrint('/!\\ More info and save restoring procedure are available on Github (cf. README) /!\\')
    loading_bar = LoadingBar(15)
    loading_bar.start_loading()

    xbox_astroneer_save_folder = Scenario.backup_win_before_steam_export()

    steamsave_files_list = AstroSave.get_steamsaves_list(original_save_path)

    saves_list = AstroSave.init_saves_list_from(steamsave_files_list)

    original_saves_name = []
    for save in saves_list:
        original_saves_name.append(save.name)

    saves_indexes_to_export = Scenario.ask_saves_to_export(saves_list)

    Scenario.ask_rename_saves(saves_indexes_to_export, saves_list)

    Logger.logPrint(f'\nExtracting saves {str([i+1 for i in saves_indexes_to_export])}')
    Logger.logPrint(f'Working folder: {original_save_path} Export to: {xbox_astroneer_save_folder}', "debug")

    for save_index in saves_indexes_to_export:
        save = saves_list[save_index]
        original_save_full_path = utils.join_paths(original_save_path, original_saves_name[save_index]+'.savegame')
        Scenario.export_save_to_xbox(save, original_save_full_path, xbox_astroneer_save_folder)

        Logger.logPrint(f"\nSave {save.name} has been exported succesfully.")


if __name__ == "__main__":
    try:
        Logger.setup_logging(os.getcwd())

        try:
            os.system("title AstroSaveConverter 2.0 - Convert your Astroneer saves between Microsoft and Steam")
        except:
            pass

        args = get_args()

        conversion_type = Scenario.ask_conversion_type()

        try:
            if not args.savesPath:
                original_save_path = Scenario.ask_for_save_folder(conversion_type)
            else:
                original_save_path = args.savesPath
                if not utils.is_path_exists(original_save_path):
                    raise FileNotFoundError
        except FileNotFoundError as e:
            Logger.logPrint('\nSave folder or container not found, press any key to exit')
            Logger.logPrint(e, 'exception')
            utils.wait_and_exit(1)

        if conversion_type == AstroConvType.WIN2STEAM:
            windows_to_steam_conversion(original_save_path)
        elif conversion_type == AstroConvType.STEAM2WIN:
            steam_to_windows_conversion(original_save_path)

        Logger.logPrint(f'\nTask completed, press any key to exit')
        utils.wait_and_exit(0)
    except Exception as e:
        Logger.logPrint(e)
        Logger.logPrint('', 'exception')
        utils.wait_and_exit(1)
