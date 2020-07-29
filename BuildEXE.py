import sys

import PyInstaller.__main__
import os
import shutil

# Separator for Windows:           ';'
# Separator for Linux/MacOS/Unix:  ':'
separator = ';' if sys.platform == 'win32' else ':'

platform = 'windows' if sys.platform == 'win32' else 'linux'
binary_folder = './lib/' + platform + '/x64'


# Build CLI version
PyInstaller.__main__.run([
    '--name=%s' % "AstroSaveConverterCLI",
    '--onefile',
    '--add-data=%s' % "assets/astroconverterlogo.ico" + separator + "assets/astroconverterlogo.ico",
    '--icon=%s' % "assets/astroconverterlogo.ico",
    'AstroSaveConverter.py'
])

# Build GUI version
PyInstaller.__main__.run([
    '--name=%s' % "AstroSaveConverterGUI",
    '--onefile',
    '--add-data=%s' % "assets" + separator + "assets",
    '--add-binary=%s' % binary_folder + separator + "."
    '--icon=%s' % "assets/astroconverterlogo.ico",
    'AstroSaveGui.py'
])

shutil.rmtree("build")
if os.path.exists("AstroSaveConverterGUI.spec"):
    os.remove("AstroSaveConverterGUI.spec")
if os.path.exists("AstroSaveConverterCLI.spec"):
    os.remove("AstroSaveConverterCLI.spec")
