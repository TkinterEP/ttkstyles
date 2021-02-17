"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2020 RedFantom
"""
# Standard Library
import os
import tkinter as tk
from typing import List, Optional, Tuple
# Project Modules
from ..exceptions import TtkStyleException
from .loader import ThemeLoader
from ..utils import chdir, first, subtup


class TclThemeLoader(ThemeLoader):
    """Load a Tcl theme from a directory"""

    def load(self) -> str:
        packages = self._loaded_pkgs
        entry = self._find_entry_point(self._path)
        if entry is None:
            raise TtkStyleException("Could not find entry point for Tcl theme in '{}'".format(self._path))
        with chdir(self._path):
            try:
                self._tk.eval("source {}".format(entry))
            except tk.TclError as e:
                message, = e.args
                if "already exists" in message:
                    return message.split(" ")[1]
                else:
                    raise
        pkg = subtup(self._loaded_pkgs, packages)
        theme = first(pkg)
        if theme is None:
            raise TtkStyleException("Loading '{}' from '{}' did not yield a theme. Is there a package provide line?"
                .format(entry, self._path))

        self._tk.call("package", "require", theme)
        return theme
        
    @property
    def _loaded_pkgs(self) -> Tuple[str, ...]:
        return self._tk.call("package", "names")

    @staticmethod
    def _find_entry_point(path: str) -> Optional[str]:
        path = path.rstrip(os.sep)
        candidates = ["pkgIndex.tcl", "{}.tcl".format(os.path.basename(path))]
        actual = [c for c in candidates if c in os.listdir(path)]
        return first(actual)

    def supports_extras(self) -> List[str]:
        raise NotImplementedError()

    @staticmethod
    def is_loader_capable(path: str) -> bool:
        return TclThemeLoader._find_entry_point(path) is not None
