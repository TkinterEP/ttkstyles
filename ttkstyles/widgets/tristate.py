"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2020 RedFantom
"""
from enum import IntEnum
import tkinter as tk
from tkinter import ttk
from typing import Dict


def tuple_comp(tup1: tuple, tup2: tuple) -> bool:
    """Compare the elements of one tuple to another"""
    return set(tup1) == set(tup2)


class TristateWidget(ttk.Widget):
    """
    Widget that supports a third, 'partially' selected state

    'Normal' widgets do include a third state (tristate) in their
    operation. Therefore, it must forcibly be set so that the widget is
    displayed properly.

    The state of the widget is internally tracked in the variable
    ``_state``, and the widget hooks into the proper Tkinter events
    to ensure that its display is continuously forced to match that
    state.
    """


    class State(IntEnum):
        NONE = 0
        TRISTATE = 1
        SELECTED = 2

        @staticmethod
        def next(current: int) -> int:
            """Return the state sequentially after the one given"""
            if current == TristateWidget.State.NONE:
                return TristateWidget.State.TRISTATE
            elif current == TristateWidget.State.TRISTATE:
                return TristateWidget.State.SELECTED
            else:
                return TristateWidget.State.NONE

    _state_map: Dict[State, str] = {
        State.NONE: "",
        State.TRISTATE: "alternate",
        State.SELECTED: "selected"
    }

    def __init__(self, *args, **kwargs):
        variable = kwargs.pop("variable", None)
        assert (isinstance(variable, tk.IntVar) or variable is None)  # TODO
        self._variable = tk.BooleanVar()
        # kwargs.update({"variable": self._variable, "offvalue": False, "onvalue": True})
        ttk.Widget.__init__(self, *args, kwargs)
        self.bind("<Button-1>", self._on_click)
        self.bind("<Configure>", self._update_state)
        self.bind("<Enter>", self._update_state)
        self.bind("<Leave>", self._update_state)
        self._state: TristateWidget.State = TristateWidget.State.NONE

    def _on_click(self, _: tk.Event):
        self._state: TristateWidget.State = TristateWidget.State.next(self._state)
        self._variable.set(self._state == TristateWidget.State.SELECTED)
        self._update_state()
        self.update_idletasks()
        assert self._variable.get() == (self._state == TristateWidget.State.SELECTED)

    def _update_state(self, _: tk.Event = None):
        """Force the state of the widget to be alternate if in tristate"""
        self.update_idletasks()
        tkstate = self.state()
        assert isinstance(tkstate, tuple)
        tkstate = list(tkstate)
        # Clean the current state from display state
        for value in self._state_map.values():
            if value in tkstate:
                tkstate.remove(value)
        # Add the proper display state
        if self._state != TristateWidget.State.NONE:
            tkstate.append(self._state_map[self._state])
        tkstate = tuple(tkstate)
        self.state(tkstate)
        self.update_idletasks()
        print(self._state, tkstate, self.state())
        # assert tuple_comp(self.state(), tkstate)


class TristateCheckbutton(TristateWidget):
    def __init__(self, master, **kwargs):
        kwargs.update(style="TCheckbutton")
        TristateWidget.__init__(self, master, "ttk::checkbutton", **kwargs)


class TristateRadiobutton(TristateWidget):
    def __init__(self, master, **kwargs):
        kwargs.update(style="TRadiobutton")
        TristateWidget.__init__(self, master, "ttk::radiobutton", **kwargs)
