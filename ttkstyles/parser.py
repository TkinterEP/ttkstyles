"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2020 RedFantom
"""
# Standard Library
from configparser import ConfigParser
import os
from typing import Dict, Generator, Optional, Tuple
# Project Modules
from .exceptions import TtkStyleFileUnavailable, TtkStyleFileParseError
from .files import File, ZippedFile, RemoteFile, RemoteZippedFile, GitHubRepoFile


class StyleFile(object):
    """Parser for example.ttkstyle configuration files"""

    def __init__(self, path: str):
        """
        :param path: Valid path to the configuration file
        """
        if not os.path.exists(path):
            raise TtkStyleFileUnavailable("Could not find style file '{}'".format(path))

        self._config = ConfigParser()
        with open(path) as fi:
            self._config.read_file(fi)

    @property
    def theme(self) -> Tuple[File, str, str]:
        """Return theme File, type and name for the given settings"""
        if "theme" not in self._config:
            raise TtkStyleFileParseError("Style file does not specify theme, yet it is required.")
        theme = dict(self._config["theme"])
        StyleFile._validate_key(theme, ("name", "type"))
        return self.interpret_file_from_section(theme), theme["name"], theme["type"]

    @property
    def font(self) -> Optional[Tuple[str, Tuple[str, ...]]]:
        """Return font File, family and options tuple"""
        if "font" not in self._config:
            return None
        if "family" not in self._config["font"]:
            raise TtkStyleFileParseError("'family' key missing from font section")
        family = self._config["font"]["family"]
        size = self._config["font"].get("size", "default")
        options = self._config["font"].get("options", "")
        options = tuple(map(str.strip, options.split(",")))
        return family, (size,)+options

    @property
    def fonts(self) -> Generator[Tuple[File, str], None, None]:
        fonts = filter(lambda x: x.startswith("font:"), self._config.sections())
        for sec_name in fonts:
            section = dict(self._config[sec_name])
            family = section.get("family", None)
            if family is None:
                family = sec_name.split(":")[-1]
            yield self.interpret_file_from_section(section), family

    @staticmethod
    def interpret_file_from_section(section: Dict[str, str]) -> File:
        """Build a File instance from the given settings"""
        StyleFile._validate_key(section, ("pkg", "path"))
        pkg = section["pkg"]

        if pkg == "local":
            return File(section["path"])

        elif pkg == "remote":
            StyleFile._validate_key(section, ("url",))
            return RemoteFile(section["path"], section["url"])

        elif pkg == "zip":
            StyleFile._validate_key(section, ("archive",))
            return ZippedFile(section["path"], File(section["archive"]), section.get("root", "true") == "true")

        elif pkg == "remote zip":
            StyleFile._validate_key(section, ("url",))
            return RemoteZippedFile(section["path"], section["url"], name=section.get("archive", None),
                                    root=section.get("root", "true") == "true")

        elif pkg == "github":
            StyleFile._validate_key(section, ("author", "repo", "commit"))
            return GitHubRepoFile(section["path"], section["author"], section["repo"], section["commit"])

        else:
            raise TtkStyleFileParseError("No valid value given for file pkg type: '{}'".format(pkg))

    @staticmethod
    def _validate_key(section: Dict[str, str], keys: Tuple[str, ...]):
        for key in keys:
            if key not in section:
                raise TtkStyleFileParseError("Expected key '{}' not found in style file".format(key))
