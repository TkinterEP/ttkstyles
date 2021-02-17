"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2020 RedFantom
"""
from .loader import ThemeLoader
# from .py import PyThemeLoader
from .tcl import TclThemeLoader
# from .gtk import GtkThemeLoader

from typing import Dict, Type

LOADERS: Dict[str, Type[ThemeLoader]] = {
    "tcl": TclThemeLoader
}
