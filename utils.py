"""Miscellaneous utility helpers used across the project."""

import os
import shutil
import sys
import winpath
from io import StringIO
from datetime import datetime


def create_folder_name(prefix: str) -> str:
    """Create a timestamped folder name.

    Args:
        prefix: Base prefix for the folder.

    Returns:
        str: Generated folder name.
    """
    now = datetime.now().strftime('%Y.%m.%d-%H.%M')
    return f'{prefix}_{now}'


def is_folder_writable(path: str) -> bool:
    """Return ``True`` if ``path`` is writable."""
    return os.access(os.path.dirname(path), os.W_OK)


def is_path_exists(path: str) -> bool:
    """Check whether ``path`` exists."""
    return os.path.exists(path)


def is_folder_a_dir(path: str) -> bool:
    """Return ``True`` if ``path`` is a directory."""
    return os.path.isdir(path)


def is_a_file(path: str) -> bool:
    """Return ``True`` if ``path`` points to a file."""
    return os.path.isfile(path)


def list_folder_content(path: str) -> list:
    """List files in ``path``."""
    return os.listdir(path)


def make_dir_if_doesnt_exists(path: str) -> None:
    """Create ``path`` if it does not already exist."""
    if not os.path.isdir(path):
        os.mkdir(path)


def get_dir_name(path: str) -> str:
    """Return the directory name of ``path``."""
    return os.path.dirname(path)


def join_paths(path1: str, path2: str) -> str:
    """Join two path components."""
    return os.path.join(path1, path2)


def copy_files(source: str, target: str) -> None:
    """Copy directory ``source`` to ``target``."""
    if os.path.isdir(target):
        shutil.rmtree(target)
    shutil.copytree(source, target)


def get_windows_desktop_path() -> str:
    """Return the current user's desktop path."""
    return winpath.get_desktop()


def rcontains(rgexp: str, string: str) -> bool:
    """Return ``True`` if ``string`` contains ``rgexp``."""
    return string.rfind(rgexp) != -1


def write_buffer_to_file(target: str, buffer: StringIO) -> None:
    """Write an in-memory buffer to disk."""
    with open(target, "wb") as target_save:
        target_save.write(buffer.getvalue())


def append_buffer_to_file(target: str, buffer: StringIO) -> None:
    """Append an in-memory buffer to a file."""
    with open(target, "ab") as target_save:
        target_save.write(buffer.getvalue())


def wait_and_exit(code: int) -> None:
    """Wait for user input then exit with ``code``."""
    input()
    sys.exit(code)
