"""
Author: rdbende and RedFantom
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

class ToolTip(object):
    """
        wait (int): Wait before appearing (in seconds)
        duration (int): Wait before disappearing (in seconds)
        direction (str): Direction relative to the parent. Directions: cursor, above, below, right, left
        ipadx (int): Inner X padding of the tooltip
        ipady (int): Inner Y padding of the tooltip
    """
    
    ALLOWED_LAYOUTS = ["ToolTip", "Tooltip", "Tip", "Balloon"]
    
    def __init__(self, master, **kwargs):
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
        self.master.bind("<Enter>", self._enter)
        self.master.bind("<Leave>", self._hidetip)
        self.master.bind("<ButtonPress>", self._hidetip)
        
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
            self.y = int(self.master.winfo_rooty()  + (self.master.winfo_height() / 2) - (label.winfo_reqheight() / 2))
        elif self._direction == "left":
            self.x = self.master.winfo_rootx() - label.winfo_reqwidth() - 5
            self.y = int(self.master.winfo_rooty()  + (self.master.winfo_height() / 2) - (label.winfo_reqheight() / 2))
        elif self._direction == "cursor":
            self.x = label.winfo_pointerx() + 10
            self.y = label.winfo_pointery() + 20
        self._toplevel.geometry("+{}+{}".format(self.x, self.y))
        
    @staticmethod
    def _determine_proper_layout() -> Optional[str]:
        """Enumerate the layout and find one that's valid and return it"""
        style = ttk.Style()
        for layout in ToolTip.ALLOWED_LAYOUTS:
            try:
                style.layout(layout)
                bg = style.lookup(".", "background")
                return layout, bg
            except tk.TclError:
                continue   
        return None, None
