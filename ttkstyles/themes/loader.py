"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2020 RedFantom
"""
# Standard Library
import tkinter as tk
from typing import List, Tuple, Optional


class ThemeLoader(object):
    """Abstract class to be implemented by all classes capable of loading themes"""

    def __init__(self, tkinterp, path: str):
        """
        :param path: Valid path to directory in which theme files are
            located.
        """
        self._tk = tkinterp
        self._path = path

    def load(self) -> str:
        """Load the theme from the specified directory and return theme name"""
        raise NotImplementedError()

    def supports_extras(self) -> List[str]:
        """Return a list of the names of the extra widgets supported by this theme"""
        raise NotImplementedError()

    @staticmethod
    def is_loader_capable(path: str) -> bool:
        """Return whether this loader is capable of loading a theme from the path"""
        raise NotImplementedError()
