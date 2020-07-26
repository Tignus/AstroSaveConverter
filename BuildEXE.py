import PyInstaller.__main__
import os
import shutil

PyInstaller.__main__.run([
    '--name=%s' % "AstroSaveConverter",
    '--onefile',
    '--add-data=%s' % "assets/*;.",
    '--icon=%s' % "assets/astroconverterlogo.ico",
    'AstroSaveConverter.py'
])

shutil.rmtree("build")
os.remove("AstroSaveConverter.spec")
