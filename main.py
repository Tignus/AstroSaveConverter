import os
from argparse import ArgumentParser, Namespace

import AstroSaveScenario as Scenario
import utils
from cogs import AstroLogging as Logger
from cogs.AstroSaveContainer import AstroSaveContainer as Container
from cogs.AstroSaveErrors import MultipleFolderFoundError


def print_container(container):
    """ Displays the saves of a container """
    Logger.logPrint('Extracted save list :')
    for i, save in enumerate(container.save_list):
        Logger.logPrint(f'\t {str(i+1)}) {save.save_name}')


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
        container = Scenario.ask_for_container(args.savesPath)

        Logger.logPrint('Container file loaded successfully !\n')
        print_container(container)

        saves_to_export = Scenario.ask_saves_to_export(container)
        Logger.logPrint(saves_to_export)

        Scenario.ask_rename_container(saves_to_export, container)
        to_path = utils.join_paths(args.savesPath, 'Steam saves')

        Logger.logPrint(f'\nExtracting saves {str([i+1 for i in saves_to_export])}')
        utils.rm_dir_if_exists(to_path)

        container.xbox_to_steam(saves_to_export, to_path)

        Logger.logPrint(f'\nTask completed, press any key to exit')
        utils.wait_and_exit(0)
    except Exception as e:
        Logger.logPrint(e)
        Logger.logPrint('', 'exception')
        utils.wait_and_exit(1)
