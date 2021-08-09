"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2021 RedFantom
"""
from unittest import TestCase
import tkinter as tk
from tkinter import ttk
from ttkstyles.style import Style, TkSingleton


def define_invalid_cls():
    class InvalidClass(object, metaclass=TkSingleton):
        """This class is invalid as TkSingleton requires specific kwargs"""
        def __init__(self, invalid_param = None):
            pass


class TestStyle(TestCase):
    def setUp(self):
        self.window = tk.Tk()

    def test_initialization(self):
        style = Style(self.window)

        label = ttk.Label(self.window)
        self.assertIs(style, Style(self.window))
        self.assertIs(style, Style(master=self.window))
        self.assertIs(style, Style(root=self.window))
        self.assertIs(style, Style(label))
        self.assertIs(style, Style())

        second = tk.Tk()
        self.assertIsNot(style, Style(second))

    def test_tk_singleton(self):
        self.assertRaises(RuntimeError, define_invalid_cls)