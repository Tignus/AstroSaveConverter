"""Web GUI entry point for AstroSaveConverter."""

import os

import gui_server
import utils
from cogs import AstroLogging as Logger
from main import APP_VERSION


def run_gui() -> None:
    """Run the application in Web GUI mode."""
    try:
        Logger.setup_logging(os.getcwd())
        Logger.logPrint(f"Starting AstroSaveConverter version {APP_VERSION} (GUI)")

        try:
            os.system(
                f"title AstroSaveConverter {APP_VERSION} (GUI) - Convert your Astroneer saves"
            )
        except Exception:
            pass

        gui_server.start_gui()
    except Exception as e:
        Logger.logPrint(e)
        Logger.logPrint("", "exception")
        utils.wait_and_exit(1)


if __name__ == "__main__":
    run_gui()
