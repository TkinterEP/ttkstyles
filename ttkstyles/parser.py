"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2020 RedFantom
"""
# Standard Library
import ast
import os
from typing import Any, Dict, Generator, List, Optional, Tuple
# Project Modules
from .exceptions import TtkStyleFileUnavailable, TtkStyleFileParseError
from .files import File, ZippedFile, RemoteFile, RemoteZippedFile, GitHubRepoFile
# Packages
import tinycss
import tinycss.token_data


class StyleFile(object):
    """Parser for example.ttkstyle configuration files"""

    def __init__(self, path: str):
        """
        :param path: Valid path to the configuration file
        """
        if not os.path.exists(path):
            raise TtkStyleFileUnavailable("Could not find style file '{}'".format(path))

        parser = tinycss.make_parser()
        with open(path, "rb") as fi:
            css = parser.parse_stylesheet_bytes(fi.read())
        self._config = self.css_rules_to_dict(css.rules)

    @staticmethod
    def css_rules_to_dict(rules: List[tinycss.css21.RuleSet]) -> Dict[str, Dict[str, Any]]:
        """Convert the tinycss rules to option dictionaries"""
        rules_dict = dict()
        print(rules)
        for rule in rules:
            key = "".join(map(lambda x: x.value, rule.selector))
            print(key)
            rules_dict[key] = {}
            for option in rule.declarations:
                option: tinycss.css21.Declaration
                val = StyleFile.flatten_to_string(option.value[0])
                try:
                    val = ast.literal_eval(val)
                except:
                    pass
                rules_dict[key][option.name] = val
        return rules_dict

    @property
    def theme(self) -> Tuple[File, str, str]:
        """Return theme File, type and name for the given settings"""
        if "#theme" not in self._config:
            raise TtkStyleFileParseError("Style file does not specify theme, yet it is required.")
        theme = dict(self._config["#theme"])
        StyleFile._validate_key(theme, ("name", "type"))
        return self.interpret_file_from_section(theme), theme["name"], theme["type"]

    @property
    def fonts(self) -> Generator[Tuple[File, str], None, None]:
        fonts = filter(lambda x: x.startswith("#font."), self._config.keys())
        for sec_name in fonts:
            section = dict(self._config[sec_name])
            family = section.get("family", None)
            if family is None:
                family = sec_name.split(".")[-1]
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

    @property
    def styles(self) -> Dict[str, Dict[str, Any]]:
        config = {k: v for k, v in self._config.items() if not k.startswith("#")}
        options = {k: self.style_options_to_tkinter(v) for k, v in config.items()}
        print(options)
        return options

    @staticmethod
    def style_options_to_tkinter(options: Dict[str, Any]) -> Dict[str, Any]:
        tk_options = {}
        # Font
        if "font-family" in options:
            font = (options.pop("font-family"),)
            if "font-size" in options:
                font += (options.pop("font-size"),)
            if "font-options" in options:
                font += tuple(map(str.strip, options.pop("font-options").split(",")))
            tk_options["font"] = font
        # Colors
        if "font-color" in options:
            tk_options["foreground"] = options.pop("font-color")
        tk_options.update(options)
        # Grid
        for option, value in options.copy().items():
            if option.startswith("grid-"):
                if "grid" not in tk_options:
                    tk_options["grid"] = {}
                tk_options["grid"][option[5:]] = value

        return tk_options

    @staticmethod
    def flatten_to_string(container: (tinycss.token_data.ContainerToken, tinycss.token_data.Token)) -> str:
        if not container.is_container:
            return container.value
        string = ""
        for element in container.content:
            if element.is_container:
                string += StyleFile.flatten_to_string(element)
            else:
                string += str(element.value)
        return string
