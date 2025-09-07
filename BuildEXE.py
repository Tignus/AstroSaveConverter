"""Helper script to build the standalone executable using PyInstaller."""

import PyInstaller.__main__
import os
import shutil

PyInstaller.__main__.run([
    '--name=%s' % "AstroSaveConverter",
    '--onefile',
    '--add-data=%s' % "assets/*;.",
    '--icon=%s' % "assets/astroconverterlogo.ico",
    'main.py'
])

shutil.rmtree("build")
os.remove("AstroSaveConverter.spec")
