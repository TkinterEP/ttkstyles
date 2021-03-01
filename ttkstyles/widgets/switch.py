"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2021 RedFantom
"""
import tkinter as tk
from tkinter import ttk
import tooltip
from typing import Optional


class SwitchButton(ttk.Checkbutton):
    """Button that is like a checkbox, but looks different"""

    # TODO: Make themes pick one of these variants for the layout name
    ALLOWED_LAYOUTS = ["Switch", "SwitchButton", "Switchbutton", "ToggleButton", "Togglebutton", "Toggle"]


    def __init__(self, *args, **kwargs):
        """
        :param allow_fallback: Boolean to indicate whether falling back
            to the default Checkbutton style is allowed (False) or 
            an error must be raised if no proper SwitchButton style 
            is available (True)
        :type allow_fallback: bool 
        """
        allow_fallback = kwargs.pop("allow_fallback", False)
        layout = kwargs.pop("style", None)
        tooltiptext = kwargs.pop("tooltip", None)

        if layout is None:
            layout = self._determine_proper_layout()
        if layout is None and allow_fallback:
            layout = "Checkbutton"
        if layout is None:
            raise tk.TclError("No layout for SwitchButton is available. Must be one of {}".format(self.ALLOWED_LAYOUTS))

        kwargs.update(style=layout)
        ttk.Checkbutton.__init__(self, *args, **kwargs)
        self._tooltip = tooltip.ToolTip(self, text=tooltiptext)


    @staticmethod
    def _determine_proper_layout() -> Optional[str]:
        """Enumerate the layout and find one that's valid and return it"""
        style = ttk.Style()  # Style created with default root
        for layout in SwitchButton.ALLOWED_LAYOUTS:
            try:
                style.layout(layout)
                return layout  # Return if there is no error
            except tk.TclError:
                continue  # Error must be caught this way, checking otherwise not possible
        return None  # Return None if no valid layout found
