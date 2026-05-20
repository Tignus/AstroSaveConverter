"""Helper script to build the standalone executable using PyInstaller."""

import os
import shutil

import PyInstaller.__main__

data_sep = ";" if os.name == "nt" else ":"

# 1. Build GUI Executable
gui_args = [
    "--name=AstroSaveConverter",
    "--onefile",
    "--clean",
    "--noconfirm",
    f"--add-data=assets/*{data_sep}.",
    f"--add-data=web{data_sep}web",
    "--icon=assets/astroconverterlogo.ico",
    "--exclude-module=sphinx",
    "--exclude-module=sphinx_rtd_theme",
    "main.py",
]
print("Building GUI Executable...")
PyInstaller.__main__.run(gui_args)

# 2. Build CLI Executable
cli_args = [
    "--name=AstroSaveConverterCLI",
    "--onefile",
    "--clean",
    "--noconfirm",
    f"--add-data=assets/*{data_sep}.",
    "--icon=assets/astroconverterlogo.ico",
    "--exclude-module=sphinx",
    "--exclude-module=sphinx_rtd_theme",
    "main_cli.py",
]
print("\nBuilding CLI Executable...")
PyInstaller.__main__.run(cli_args)


# Cleanup PyInstaller temporary build directories
for name in ["AstroSaveConverter", "AstroSaveConverterCLI"]:
    work_subdir = os.path.join("build", name)
    if os.path.isdir(work_subdir):
        shutil.rmtree(work_subdir, ignore_errors=True)
        
    spec_file = f"{name}.spec"
    if os.path.isfile(spec_file):
        os.remove(spec_file)

# Remove the top-level build folder ONLY if it is now empty
build_dir = "build"
if os.path.isdir(build_dir) and not os.listdir(build_dir):
    os.rmdir(build_dir)

print("\nBuild pipeline finished successfully! Both GUI and CLI executables are in the 'dist' folder.")
