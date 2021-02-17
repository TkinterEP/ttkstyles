"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2020 RedFantom
"""


class TtkStyleException(Exception):
    pass


class TtkStyleFileUnavailable(TtkStyleException, FileNotFoundError):
    def __init__(self, message: str):
        TtkStyleException.__init__(self, "The specified file is unavailable: {}".format(message))


class TtkStyleFileParseError(TtkStyleException, ValueError):
    pass
