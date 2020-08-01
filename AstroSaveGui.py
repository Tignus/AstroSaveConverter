import sys
import os
import sciter

from AstroSaveConverter import get_container_list
from urllib.parse import urlparse


class Frame(sciter.Window):
    def __init__(self):
        super().__init__(ismain=True, uni_theme=True)

    @sciter.script
    def GetContainerList(self, path):
        p = urlparse(path)
        path = os.path.abspath(os.path.join(p.netloc, p.path))

        fileContainer = get_container_list(path)

        return fileContainer


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


if __name__ == '__main__':
    sciter.runtime_features(file_io=True, allow_sysinfo=True)

    frame = Frame()
    frame.load_file(resource_path("./assets/gui/main.htm"))
    frame.run_app()
