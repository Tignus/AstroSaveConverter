"""Build standalone GUI and CLI executables with PyInstaller."""

from __future__ import annotations

import os
import shutil

import PyInstaller.__main__


DATA_SEPARATOR = ";" if os.name == "nt" else ":"
COMMON_ARGS = [
    "--onefile",
    "--clean",
    "--noconfirm",
    f"--add-data=assets/*{DATA_SEPARATOR}.",
    "--icon=assets/astroconverterlogo.ico",
    "--exclude-module=sphinx",
    "--exclude-module=sphinx_rtd_theme",
]
BUILD_TARGETS = [
    (
        "AstroSaveConverter",
        ["main.py"],
    ),
    (
        "AstroSaveConverterGUI",
        [f"--add-data=web{DATA_SEPARATOR}web", "main_gui.py"],
    ),
]


def build_executable(name: str, extra_args: list[str]) -> None:
    """Build one executable target."""
    print(f"Building {name}...")
    PyInstaller.__main__.run([f"--name={name}", *COMMON_ARGS, *extra_args])


def cleanup_build_artifacts() -> None:
    """Remove PyInstaller working files while keeping generated executables."""
    for name, _ in BUILD_TARGETS:
        work_subdir = os.path.join("build", name)
        if os.path.isdir(work_subdir):
            shutil.rmtree(work_subdir, ignore_errors=True)

        spec_file = f"{name}.spec"
        if os.path.isfile(spec_file):
            os.remove(spec_file)

    build_dir = "build"
    if os.path.isdir(build_dir) and not os.listdir(build_dir):
        os.rmdir(build_dir)


def main() -> None:
    """Run the complete executable build pipeline."""
    for name, extra_args in BUILD_TARGETS:
        build_executable(name, extra_args)

    cleanup_build_artifacts()
    print("\nBuild pipeline finished successfully. Executables are in the 'dist' folder.")


if __name__ == "__main__":
    main()
