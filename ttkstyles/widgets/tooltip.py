"""
Author: rdbende and RedFantom
License: GNU GPLv3
Copyright (c) ToolTip: rdbende 2021
Copyright (c) stylecheck: RedFantom 2021
"""

import tkinter as tk
from tkinter import ttk
from typing import Any, Optional, Tuple


class ToolTip(object):

    # TODO: Make themes pick one of these variants for the layout name
    ALLOWED_LAYOUTS = ["ToolTip", "Tooltip", "Tip", "Balloon"]

    def __init__(self, master, **kwargs):
        """
        Create a styleable ToolTip
        
        :param wait: wait before appearing (in seconds)
        :type wait: int
        :param duration: wait before disappearing (in seconds)
        :type duration: int
        :param direction: direction relative to the parent
            directions: cursor, above, below, right, left (default is cursor)
        :type: str
        :param ipadx: inner X padding of the tooltip
        :type ipadx: int
        :param ipady: inner Y padding of the tooltip
        :type ipady: int
        :param kwargs: options to be passed on to the :class:`ttk.Label` initializer inside the tooltip
        """
        self._toplevel = None
        self.master = master
        self._wait = int(kwargs.pop("wait", "2")) * 1000
        self._duration = int(kwargs.pop("duration", "10")) * 1000
        self._direction = kwargs.pop("direction", "cursor")
        self._ipadx = kwargs.pop("ipadx", "3")
        self._ipady = kwargs.pop("ipady", "1")
        kwargs.update(anchor="center")
        self._layout, self._bg = self._determine_proper_layout()
        if self._layout is None:
            kwargs.update(relief="solid", borderwidth=1)
        else:
            kwargs.update(style=self._layout)
        self.kwargs = kwargs
        if kwargs["text"] is not None:
            self._bind()

    def _bind(self):
        self.master.bind("<Enter>", self._enter)
        self.master.bind("<Leave>", self._hidetip)
        self.master.bind("<ButtonPress>", self._hidetip)

    def _unbind(self):
        # TODO: Improve this so as to only unbind our own methods
        self.master.unbind("<Enter>")
        self.master.unbind("<Leave>")
        self.master.unbind("<ButtonPress>")

    def _enter(self, *args):
        """Creates a ToolTip, and schedules it"""
        self._toplevel = tk.Toplevel(self.master)
        self._toplevel.overrideredirect(True)
        self._toplevel.withdraw()
        if self._bg is not None:
            self._toplevel.wm_attributes("-transparentcolor", self._bg)
        self.id0 = self.master.after(self._wait, self._showtip)
        self.id1 = self.master.after(self._duration, self._hidetip)

    def _hidetip(self, *args):
        """Destroys the ToolTip"""
        self.master.after_cancel(self.id0)
        self.master.after_cancel(self.id1)
        self._toplevel.destroy()

    def _showtip(self):
        """Displays the ToolTip"""
        self._toplevel.deiconify()
        label = ttk.Label(self._toplevel, **self.kwargs)
        label.pack(ipadx=self._ipadx, ipady=self._ipady)
        if self._direction == "above":
            self.x = int(self.master.winfo_rootx() + (self.master.winfo_width() / 2) - (label.winfo_reqwidth() / 2))
            self.y = self.master.winfo_rooty() - label.winfo_reqheight() - 5
        elif self._direction == "below":
            self.x = int(self.master.winfo_rootx() + (self.master.winfo_width() / 2) - (label.winfo_reqwidth() / 2))
            self.y = self.master.winfo_rooty() + self.master.winfo_reqheight() + 5
        elif self._direction == "right":
            self.x = self.master.winfo_rootx() + self.master.winfo_width() + 5
            self.y = int(self.master.winfo_rooty() + (self.master.winfo_height() / 2) - (label.winfo_reqheight() / 2))
        elif self._direction == "left":
            self.x = self.master.winfo_rootx() - label.winfo_reqwidth() - 5
            self.y = int(self.master.winfo_rooty() + (self.master.winfo_height() / 2) - (label.winfo_reqheight() / 2))
        elif self._direction == "cursor":
            self.x = label.winfo_pointerx() + 10
            self.y = label.winfo_pointery() + 20
        self._toplevel.geometry("+{}+{}".format(self.x, self.y))

    @staticmethod
    def _determine_proper_layout() -> Optional[Tuple[str, str]]:
        """Enumerate the layout and find one that's valid and return it"""
        style = ttk.Style()  # Style created with default root
        for layout in ToolTip.ALLOWED_LAYOUTS:
            try:
                style.layout(layout)
                bg = style.lookup(".", "background")
                return layout, bg  # Return if there is no error
            except tk.TclError:
                continue  # Error must be caught this way, checking otherwise not possible
        return None, None  # Return None if no valid layout found

    def configure(self, cnf={}, **kwargs):
        self.kwargs.update(kwargs)

    def cget(self, key: str) -> Any:
        return self.kwargs[key]

    def __setitem__(self, key: str, value: Any):
        return self.configure(key=value)

    def __getitem__(self, key: str) -> Any:
        return self.cget(key)

    def destroy(self):
        if self._toplevel is not None:
            self._toplevel.destroy()
            self._toplevel = None
