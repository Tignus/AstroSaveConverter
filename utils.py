from datetime import datetime
from cogs.AstroLogging import AstroLogging
import shutil
import os
import sys
import winpath


def create_folder_name(prefix) -> str:
    now = datetime.now().strftime('%Y.%m.%d-%H.%M')
    return f'{prefix}_{now}'


def is_folder_writable(path) -> bool:
    return os.access(os.path.dirname(path), os.W_OK)


def is_folder_exists(path) -> bool:
    return os.path.exists(path)


def is_folder_a_dir(path) -> bool:
    return os.path.isdir(path)


def is_a_file(path) -> bool:
    return os.path.isfile(path)


def is_a_container_file(path) -> bool:
    return is_a_file(path) and path.rfind('container') != -1


def list_folder_content(path) -> list:
    return os.listdir(path)


def rm_dir_if_exists(path):
    if not os.path.isdir(path):
        os.mkdir(path)


def join_paths(path1, path2):
    return os.path.join(path1, path2)


def copy_files(source, target):
    if os.path.isdir(target):
        shutil.rmtree(target)
    shutil.copytree(source, target)


def get_windows_desktop_path() -> str:
    return winpath.get_desktop()


def wait_and_exit(code):
    input()
    sys.exit(code)

