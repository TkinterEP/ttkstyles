"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2020 RedFantom
"""
# Standard Library
import os
from unittest import TestCase
# Module Under Test
from ttkstyles import files


class TestFiles(TestCase):
    """Test the 'files.py' module"""

    def setUp(self):
        if os.getcwd().endswith("tests"):
            os.chdir("..")

        import logging
        from ttkstyles import set_logging_level
        set_logging_level(logging.DEBUG)

    def test_file(self):
        f = files.File("README.md")
        self.assertTrue(os.path.exists(f.abspath))

    def test_zipped_file(self):
        f = files.ZippedFile("breeze", files.File("breeze.zip"))
        self.assertTrue(os.path.exists(f.abspath))

    def test_remote_file(self):
        pass

    def test_github_file(self):
        f = files.GitHubRepoFile("ttkthemes/png/breeze", "TkinterEP", "ttkthemes")
        self.assertTrue(os.path.exists(f.abspath))
        print(f.abspath)
