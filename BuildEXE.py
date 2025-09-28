"""Helper script to build the standalone executable using PyInstaller."""

import PyInstaller.__main__
import os
import shutil

args = [
    '--name=AstroSaveConverter',
    '--onefile',
    '--clean',
    '--noconfirm',
    '--add-data=assets/*;.',
    '--icon=assets/astroconverterlogo.ico',
    '--exclude-module=sphinx',
    '--exclude-module=sphinx_rtd_theme',
    'main.py'
]

PyInstaller.__main__.run(args)



# Remove PyInstaller work subfolder
work_subdir = os.path.join("build", "AstroSaveConverter")
if os.path.isdir(work_subdir):
    shutil.rmtree(work_subdir, ignore_errors=True)

# Remove the spec file if it exists
spec_file = "AstroSaveConverter.spec"
if os.path.isfile(spec_file):
    os.remove(spec_file)

# Remove the top-level build folder ONLY if it is now empty
build_dir = "build"
if os.path.isdir(build_dir) and not os.listdir(build_dir):
    os.rmdir(build_dir)

