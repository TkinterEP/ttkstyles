"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2020 RedFantom
"""
# Standard Library
import inspect
import os
from threading import Lock
import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, Tuple
import weakref
# Packages
import appdirs
# Project Modules
from .exceptions import TtkStyleException, TtkStyleFileUnavailable
from .files import File
from . import hooks
from .parser import StyleFile
from .themes import LOADERS
from .utils import filter_suffix, resolve


class TkSingleton(type):
    """
    Ensure that only one instance per Tk instance exists

    While tkinter does not technically support multiple Tk instances, it
    is not impossible to define multiple Tk instances. Hence, this
    metaclass is here to ensure that only a single Style exists per Tk
    instance, rather than a single Style instance overall.
    """
    _instances = weakref.WeakKeyDictionary()
    _lock = Lock()

    _ROOT_KWARGS = {"root", "master"}

    def __init__(cls, *args, **kwargs):
        """Validate the use of TkSingleton by another class"""
        super().__init__(*args, **kwargs)
        if len(TkSingleton._init_parameters(cls).intersection(TkSingleton._ROOT_KWARGS)) == 0:
            raise RuntimeError("Invalid class to use TkSingleton: {}".format(cls))

    def __call__(cls, *args, **kwargs):
        """Intercept creation of an instance to find any existing instance"""
        with cls._lock:
            if any(kwarg in kwargs for kwarg in TkSingleton._ROOT_KWARGS):
                root = kwargs.get(set(kwargs.keys()).intersection(TkSingleton._ROOT_KWARGS).pop())
            elif len(args) != 0 and args[0] != None:
                args = list(args)
                root = args.pop()
                args = tuple(args)
            else:
                root = tk._get_default_root()
            root = TkSingleton.walk_to_tk(root)

            root_args = TkSingleton._init_parameters(cls)
            kwarg = root_args.intersection(TkSingleton._ROOT_KWARGS).pop()
            kwargs.update({kwarg: root})

            instance = cls._instances.get(root, None)
            if instance is None or instance() is None:
                instance = super().__call__(*args, **kwargs)
                cls._instances[root] = weakref.ref(instance)
                return instance
            return instance()

    @staticmethod
    def walk_to_tk(widget: tk.BaseWidget):
        """Get the tk.Tk root instance for a tk.BaseWidget"""
        while not isinstance(widget, tk.Tk):
            widget = widget._root()
        return widget

    @staticmethod
    def _init_parameters(cls):
        """Get the parameter names for the __init__ function of a class"""
        return set(map(lambda param: param.name, inspect.signature(cls.__init__).parameters.values()))


class Style(ttk.Style, metaclass=TkSingleton):
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

    def __init__(self, master: tk.Tk=None, allow_override: bool = True, auto_load: bool = True):
        """
        Set-up the loader for a tk.Tk instance

        :param master: tk.Tk instance to set up this Style for.
            Remember, only one tk.Tk instance is supported by Tkinter
            itself under normal circumstances.
        :param allow_override: Whether to allow overriding the specified
            style by custom settings found in the user's configuration
            directory.
        :param auto_load: Whether to automatically load from the file
            ``example.ttkstyle`` file if it exists.
        """
        ttk.Style.__init__(self, master)
        if not hooks.is_hooked({"style": None}):
            hooks.hook_ttk_widgets(_label_option_updater, {"style": None})
        self.tkinst = ttk.setup_master(master)

        # Load tksvg is available
        try:
            import tksvg
            tksvg.load(self.tkinst)
        except ImportError:
            pass

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
        try:
            import tkextrafont
        except ImportError:
            import warnings
            warnings.warn("Failed to load tkextrafont - no external fonts will be available", ImportWarning)
            return
        for font_tup in parser.fonts:
            self.load_font(font_tup)
        styles = parser.styles
        if "." in styles:
            self.configure(".", **styles.pop("."))
        for style, options in styles.items():
            print("Configuring style: {} -> {}".format(style, options))
            self.configure(style, **options)

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

    def load_font(self, font: Tuple[File, str]):
        """
        Load a font application wide by modifying the base style

        :param font: Tuple that starts with a file specifying the font
            file that should be loaded, followed by the font name
        :type font: Tuple[File, str]
        """
        f, family = font
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

    def set_theme(self, name: str):
        """Set the currently applied theme to a specific theme name"""
        name = name.split("::")[-1]
        self.tk.call("ttk::setTheme", name)

    theme_use = set_theme


def _label_option_updater(inst, _, value):
    """Hook into ttk.Widget for ttk.Label to have an updated font with a style"""
    if not isinstance(inst, ttk.Label):
        return getattr(ttk.Widget, hooks.generate_hook_name({"style": None})).original_configure(inst, option=value)
    style = ttk.Style(inst)
    if value is not None:
        inst.configure(font=style.lookup(value, "font"), foreground=style.lookup(value, "foreground"))
