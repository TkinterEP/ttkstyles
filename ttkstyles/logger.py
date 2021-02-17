"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2020 RedFantom
"""
# Standard Library
import logging
import sys


LEVEL = logging.DEBUG
FORMAT = "[%(name)s]: %(levelname)s - %(message)s"


def get_logger(name: str, level=LEVEL) -> logging.Logger:
    """Build a new Logger instance """
    logger = logging.Logger("ttkstyles.{}".format(name), level=level)
    stdout = logging.StreamHandler(sys.stdout)
    logger.addHandler(stdout)
    fmt = logging.Formatter(FORMAT)
    stdout.setFormatter(fmt)
    return logger
