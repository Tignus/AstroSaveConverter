"""Thin wrapper around :mod:`logging` used throughout the project."""

import logging
import os
from logging.handlers import TimedRotatingFileHandler


def logPrint(message, msgType="info"):
    """Log a message with the provided severity and optionally print it.

    Args:
        message: Message to log.
        msgType: Logging level such as ``"info"`` or ``"debug"``.
    """
    message = str(message)
    if msgType == "debug":
        logging.debug(message)
    if msgType == "info":
        logging.info(message)
        print(message)
    if msgType == "warning":
        logging.warning(message)
    if msgType == "exception":
        logging.exception(message)
    if msgType == "error":
        logging.error(message)
    if msgType == "critical":
        logging.critical(message)


def setup_logging(astroPath: str, console_print: bool = True) -> None:
    """Configure the logging subsystem.

    Args:
        astroPath: Base directory where log files should be stored.
        console_print: Unused legacy flag to enable console output.
    """
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)-6s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)

    logsPath = os.path.join(astroPath, 'logs')
    if not os.path.exists(logsPath):
        os.makedirs(logsPath)

    fileLogHandler = TimedRotatingFileHandler(
        os.path.join(astroPath, 'logs', "astro_converter.log"), 'midnight', 1)
    fileLogHandler.setFormatter(formatter)

    rootLogger.addHandler(fileLogHandler)
