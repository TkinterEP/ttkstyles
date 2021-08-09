"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2020 RedFantom
"""
from ttkstyles.files import File, ZippedFile, RemoteFile, RemoteZippedFile, GitHubRepoFile
from ttkstyles.parser import StyleFile
from ttkstyles.style import Style


def set_logging_level(level):
    from ttkstyles import logger
    logger.LEVEL = level
