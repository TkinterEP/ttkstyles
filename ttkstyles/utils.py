"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2020 RedFantom
"""
# Standard Library
from contextlib import contextmanager
import os
import tkinter as tk
from typing import Optional, Tuple, Iterable, List
# Project Modules
from ttkstyles.files import File


def wm_geometry_box(inst: tk.Wm, box: Tuple[int, int, int, int] = None) -> Optional[Tuple[int, int, int, int]]:
    """Return box tuple (x1, y1, x2, y2) for Tkinter window"""
    if box is not None:
        x1, y1, x2, y2 = box
        return wm_geometry_xywh(inst, (x1, y1, x2-x1, y2-y1))

    else:
        x, y, w, h = wm_geometry_xywh(inst)
        return x, y, x+w, y+h


def wm_geometry_xywh(inst: tk.Wm, xywh: Tuple[int, int, int, int] = None) -> Optional[Tuple[int, int, int, int]]:
    """Return geometry tuple (x, y, w, h) for Tkinter window"""
    if xywh is not None:
        x, y, w, h = xywh
        inst.wm_geometry("{}x{}+{}+{}".format(w, h, x, y))

    else:
        geometry = inst.wm_geometry()
        elements = geometry.split("+")
        x, y = elements[1], elements[2]
        w, h = elements[0].split("x")
        x, y, w, h = map(int, (x, y, w, h))
        return x, y, w, h


def filter_suffix(items: Iterable[str], suffix: str) -> List[str]:
    """Filter an iterable of strings by suffix and return list"""
    return list(filter(lambda x: x.endswith(suffix), items))


@contextmanager
def chdir(target: str):
    """
    Context managed os.chdir

    By <https://github.com/Akuli> for <https://github.com/TkinterEP/ttkthemes>
    Copyright (c) 2017-2018 Akuli
    Licensed under GNU GPLv3
    """
    cwd = os.getcwd()
    os.chdir(target)
    try:
        yield
    finally:
        os.chdir(cwd)


def resolve(f: (File, str)) -> str:
    """Resolve the path to a File or a string"""
    if isinstance(f, File):
        return f.abspath
    else:
        return f


def first(x: Iterable) -> Optional:
    """Return the first element of an iterable or None if iterable empty"""
    x = list(x)
    if len(x) != 0:
        return x[0]
    return None


def subtup(tup1: tuple, tup2: tuple) -> tuple:
    """Remove all elements in tup2 from tup1"""
    tup1 = list(tup1)
    for t2 in tup2:
        while t2 in tup1:
            tup1.remove(t2)
    return tuple(tup1)


def comptup(tup1: tuple, tup2: tuple) -> bool:
    """Return whether all elements of tup1 are contained in tup2"""
    return all(e in tup2 for e in tup1) and all(e in tup1 for e in tup2)


def dicttupkey(d: dict, k: tuple):
    """Return the element of a dictionary using comptup"""
    max_key = max(d.keys(), key=lambda kd: sum(e in kd for e in k))
    return d[max_key]
