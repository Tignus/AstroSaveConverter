"""Minimalistic PySciter sample for Windows."""

import sciter
import os

from AstroSaveConverter import get_container_list
from urllib.parse import urlparse

class Frame(sciter.Window):
    def __init__(self):
        super().__init__(ismain=True, uni_theme=True)
        pass

    @sciter.script
    def GetContainerList(self, path):
        p = urlparse(path)
        path = os.path.abspath(os.path.join(p.netloc, p.path))

        fileContainer = get_container_list(path)

        #print("Container: " + fileContainer)
        return fileContainer


if __name__ == '__main__':
    sciter.runtime_features(file_io=True, allow_sysinfo=True)

    #frame = sciter.Window(ismain=True, uni_theme=True)
    frame = Frame()
    frame.load_file("assets/gui/main.htm")
    frame.run_app()