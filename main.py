import os
from argparse import ArgumentParser, Namespace

import AstroSaveScenario as Scenario
import utils
from cogs import AstroLogging as Logger
from cogs.AstroSaveContainer import AstroSaveContainer as Container
from cogs.AstroSaveErrors import MultipleFolderFoundError


def get_args() -> Namespace:
        parser = ArgumentParser()

        parser.add_argument(
            "-p", "--savesPath", help="Path from which to read the container and extract the saves", required=False)

        args = parser.parse_args()

        return args


if __name__ == "__main__":
    try:
        Logger.setup_logging(os.getcwd())

        try:
            os.system("title AstroSaveConverter - Migrate your Astroneer save from Microsoft to Steam")
        except:
            pass

        args = get_args()
        save_path = Scenario.ask_for_save_folder()

        containers_list = Container.get_containers_list(save_path)
        Logger.logPrint('\nContainers found:' + str(containers_list))
        container_name = Scenario.ask_for_containers_to_convert(containers_list) if len(containers_list) > 1 else containers_list[0]

        container = Container(utils.join_paths(save_path, container_name))

        Logger.logPrint('Container file loaded successfully !\n')

        saves_to_export = Scenario.ask_saves_to_export(container.save_list)

        Scenario.ask_rename_save(saves_to_export, container)

        to_path = utils.join_paths(save_path, 'Steam saves')

        Logger.logPrint(f'\nExtracting saves {str([i+1 for i in saves_to_export])}')
        utils.rm_dir_if_exists(to_path)

        container.xbox_to_steam(saves_to_export, to_path)

        Logger.logPrint(f'\nTask completed, press any key to exit')
        utils.wait_and_exit(0)
    except Exception as e:
        Logger.logPrint(e)
        Logger.logPrint('', 'exception')
        utils.wait_and_exit(1)
