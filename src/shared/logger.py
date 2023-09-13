import logging
from logging import DEBUG
import sys


LOGGER_FORMAT = logging.Formatter('%(asctime)s %(levelname)s --- %(module)s:%(lineno)d @@@ %(message)s')

def __get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(LOGGER_FORMAT)
    return console_handler

def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(DEBUG)

    logger.addHandler(__get_console_handler())
    logger.propagate = False

    return logger
