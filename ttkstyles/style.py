"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2020 RedFantom
"""
# Standard Library
import os
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Tuple
# Packages
import appdirs
# Project Modules
from .exceptions import TtkStyleException, TtkStyleFileUnavailable
from .files import File
from .parser import StyleFile
from .themes import LOADERS
from .utils import filter_suffix, resolve


class Style(ttk.Style):
    """
    Loader for ttk styles with fonts, Tcl themes, Python themes and more

    A ttk style consists of various elements, for which the information
    may be provided in the following two ways:

    - Calling the appropriate function to load from the source on an
      instance of this class.
    - Providing a style file. May be any file, default suffix
      ``example.ttkstyle``. Can be provided manually, but may also be
      overridden by program user default, if allowed.

    .. note::
        Program specific style instructions may be loaded automatically
        from the file ``example.ttkstyle`` in the working directory, if it
        exists.

    .. note::
        Allowing users to override the style for your program may have
        unintended consequences for the layout of your widgets if you
        use statically sized widgets, such as the ``tk.Canvas``.

    A style consists of the following elements:

    - Theme
      The ``ttk`` package provides themed widgets. Various themes are
      available from a selection of sources. The theme is the most
      important element of the style: It determines whether there is
      support for various other elements such as the `TristateCheckbox`.

    - Font
      A custom font can finish the unique look of your application.

    - Padding
      Tkinter geometry managers grid and pack support padding around
      the widgets. Use this option to set a default amount of padding
      around certain widgets. Overriding the option is of course always
      possible.

    - Tooltips
      When enabling the use of tooltips from ``ttkwidgets``, the style
      settings may be used to modify the default appearance of these
      tooltip widgets to more closely match your application.

    .. note::
        To control the padding of widgets, ``ttkstyles`` may hook into
        the ``Grid`` and ``Pack`` methods of all widgets. Default
        settings are applied only for specified widgets.

    .. note::
        In order to make use of the tooltip settings, make sure to have
        ``ttkwidgets`` installed.
    """

    THEME_TCL = "tcl"
    THEME_PY = "python"
    THEME_GTK = "gtk"

    def __init__(self, tkinst: tk.Tk, allow_override: bool = True, auto_load: bool = True):
        """
        Set-up the loader for a tk.Tk instance

        :param tkinst: tk.Tk instance to set up this Style for.
            Remember, only one tk.Tk instance is supported by Tkinter
            itself under normal circumstances.
        :param allow_override: Whether to allow overriding the specified
            style by custom settings found in the user's configuration
            directory.
        :param auto_load: Whether to automatically load from the file
            ``example.ttkstyle`` file if it exists.
        """
        ttk.Style.__init__(self, tkinst)
        self.tkinst = tkinst

        self._allow_override = allow_override

        self._settings = None

        if auto_load:
            self._load_auto()

    def _load_user_file(self):
        """Find the user's file with custom settings and load settings"""
        path = appdirs.user_config_dir("ttkstyles", "ttk")
        files = filter_suffix(os.listdir(path), "example.ttkstyle")

        for f in ("example.ttkstyle", "default.ttkstyle"):
            if f in files:
                self._load_file(f)
                break

    def _load_auto(self):
        """Load the style settings from the """
        if self._settings is not None:
            return

        if os.path.exists("example.ttkstyle"):
            self._load_file("example.ttkstyle")

    def _load_file(self, path: str):
        parser = StyleFile(path)
        theme, name, type = parser.theme
        self.load_theme(theme, type)
        font = parser.font
        if font is not None:
            self.load_font(font)

    def load_style_file(self, f: (File, str)):
        """Load style settings from example.ttkstyle file specified as File or as path"""
        if not isinstance(f, File) and not os.path.exists(f):
            raise TtkStyleFileUnavailable("'{}' not a valid path to an existing file.".format(f))
        f = resolve(f)
        self._load_file(f)

    def load_style(self, theme: (File, str), font: (File, str),
                   tooltips: Dict[str, Any] = None, padding: Dict[str, Any] = None):
        """Load a style based on specific settings"""
        raise NotImplementedError()

    def load_theme(self, f: (File, str), type: str):
        """Load a theme from a directory"""
        if not isinstance(f, File) and not (os.path.exists(f) and os.path.isdir(f)):
            raise TtkStyleException("'{}' is not a valid path to a directory.".format(f))

        if isinstance(f, File):
            f = f.abspath

        if not os.path.exists(f) or not os.path.isdir(f):
            raise TtkStyleException("'{}' did not yield a valid theme directory.")

        return self._load_theme(f, type)

    def _load_theme(self, path: str, type: str):
        """Load a theme from a specified directory"""
        if type not in LOADERS:
            raise TtkStyleException("Invalid theme type specified '{}'".format(type))

        loader = LOADERS[type](self.tk, path)
        theme = loader.load()

        self.set_theme(theme)

    def load_font(self, font: Tuple[File, str, Tuple[str, ...]]):
        """
        Load a font application wide by modifying the base style

        :param font: Tuple that starts with a file specifying the font
            file that should be loaded, followed by the font name and
            then any options applied to the font
        :type font: Tuple[File, str, Tuple[str, ...]]
        """
        f, family, options = font
        if f is not None:
            try:
                import tkextrafont
            except ImportError:
                import warnings
                warnings.warn("Failed to load font support", ImportWarning)
                return
            font = tkextrafont.Font(file=f.abspath)
            if not font.is_font_available(family):
                raise TtkStyleException("Specified font file did not provide specified font family")
        self.configure(".", font=(family,)+options)

    def set_theme(self, name: str):
        """Set the currently applied theme to a specific theme name"""
        name = name.split("::")[-1]
        self.tk.call("ttk::setTheme", name)

    theme_use = set_theme
