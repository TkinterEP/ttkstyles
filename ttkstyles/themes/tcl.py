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
        # Some Tcl packages depend on the working directory being the
        # directory that the script is in. Sometimes, Tcl scripts may
        # change their working directory, and we want to guarantee that
        # after execution of this code it is is the same as before.
        with chdir(self._path):
            try:
                # Often, Tcl packages refer to a variable named 'dir'
                # This is expected to be a string containing the abspath
                # to the directory the script being evaluated is in
                self._tk.eval("set dir {}".format(self._path))

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
