import logging
import os
from logging.handlers import TimedRotatingFileHandler


"""
    This class has been modified from the original code to print only
    the "info" type to the console and add exception printing to the
    log file.
"""


def logPrint(message, msgType="info"):
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


def setup_logging(astroPath, console_print=True):
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)-6s %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.DEBUG)

    # The console print is managed with the "info" message type
    # console = logging.StreamHandler()
    # console.setFormatter(formatter)

    logsPath = os.path.join(astroPath, 'logs')
    if not os.path.exists(logsPath):
        os.makedirs(logsPath)

    fileLogHandler = TimedRotatingFileHandler(os.path.join(
        astroPath, 'logs', "astro_converter.log"), 'midnight', 1)
    fileLogHandler.setFormatter(formatter)

    # rootLogger.addHandler(console)
    rootLogger.addHandler(fileLogHandler)
