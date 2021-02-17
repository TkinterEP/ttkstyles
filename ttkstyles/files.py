"""
Author: RedFantom
License: GNU GPLv3
Copyright (c) 2020 RedFantom
"""
# Standard Library
import os
import shutil
import site
import tempfile
from urllib.request import urlretrieve
import zipfile
# Packages
import appdirs
# Project Modules
from ttkstyles.exceptions import TtkStyleFileUnavailable, TtkStyleException
from ttkstyles.logger import get_logger


class File(object):
    CACHE_DIR = None

    def __init__(self, path: str):
        self.logger = get_logger(__class__.__name__)
        self._path = path

    def _make_available(self):
        """Make the file available and return an absolute path"""
        raise NotImplementedError()

    @property
    def abspath(self) -> str:
        """
        Return an absolute path to the file - or throw an Exception

        Note that this function may block due to IO and may thus be
        slow. Particularly for large ZIP files or remote files making
        the file available may take time.

        Once the file is made available, sub-classes should store the
        result in the file cache to ensure that IO operations that take
        too much time are only executed once.
        """
        if os.path.exists(self._path):
            self.logger.debug("Valid path to file '{}'".format(self._path))
            return os.path.abspath(self._path)
        elif os.path.exists(self._target):
            self.logger.debug("Found cached file '{}'".format(self._path))
            return self._target
        else:
            self.logger.debug("Did not find file '{}', making available".format(self._path))
            self._make_available()
        return self._target

    @property
    def _target(self) -> str:
        """Return the path any File subclass should make the file available to"""
        return os.path.join(self._cache, self._path)

    @property
    def _cache(self) -> str:
        """Return a path to the folder in which files should be cached"""
        return self.CACHE_DIR or appdirs.user_cache_dir("ttkstyles", "TkinterEP")

    @staticmethod
    def clear_cache():
        """Clear the file cache"""
        for p in os.listdir(File(None)._cache):
            shutil.rmtree(p)

    @staticmethod
    def set_cache_dir(path: str):
        """Set the cache directory to a custom folder"""
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        File.CACHE_DIR = path


class SitePackage(File):
    """Class to handle a file found in a Python site package"""

    def __init__(self, file_name: str, package: str):
        File.__init__(self, self._find_site_package_file(file_name, package))

    @staticmethod
    def _find_site_package_file(file_name: str, package: str):
        """Search for a file in the Python site packages"""
        for dir in site.getsitepackages():
            if not os.path.exists(dir):
                continue
            for pkg in os.listdir(dir):
                path = os.path.join(dir, pkg)
                f = os.path.join(path, file_name)
                if pkg == package and os.path.exists(f):
                    return f
        raise TtkStyleFileUnavailable("Could not find '{}' for package '{}'".format(file_name, package))

    def _make_available(self):
        pass


class RemoteFile(File):
    """Class to handle a remote file"""

    def __init__(self, file_name: str, url: str):
        """
        :param file_name: File name of the file to look for
        :param url: URL to the file if the file is not available locally
        """
        File.__init__(self, file_name)
        self._url = url

    def _make_available(self):
        """Download the file to the cache directory"""
        if not os.path.exists(os.path.dirname(self._target)):
            os.makedirs(os.path.dirname(self._target), exist_ok=True)
        urlretrieve(self._url, self._target)


class ZippedFile(File):
    """Handle a file that is a ZIP-archive file"""
    def __init__(self, path: str, archive: File, root=True):
        """
        :param path: Path to the file within the archive
        :param archive: File for the ZIP-archive the file is contained in
        :param root: Whether the path to the file is from root or a topmost folder
        """
        File.__init__(self, path)
        self._archive = archive
        self._root = root

    def _make_available(self):
        """Extract the requested file from the given archive File"""
        archive = self._archive.abspath
        with zipfile.ZipFile(archive) as fi:
            if self._root is False:
                path = "{}{}".format(self._find_topmost_folder(fi), self._path)
            else:
                path = self._path
            f = self._find_file_in_zip(fi, path)
            self._extract(fi, f, self._target)

    @staticmethod
    def _extract(archive: zipfile.ZipFile, info: zipfile.ZipInfo, target: str):
        """Extract file or folder specified by 'info' recursively to 'target'"""
        if info.is_dir():
            extract_to = os.path.join(tempfile.gettempdir(), os.path.basename(archive.filename))
            archive.extractall(extract_to)
            path = os.path.join(extract_to, info.orig_filename)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copytree(path, target)
            shutil.rmtree(path)
        else:
            archive.extract(info, target)

    @staticmethod
    def _find_file_in_zip(archive: zipfile.ZipFile, path: str) -> zipfile.ZipInfo:
        path = path.strip("/")
        for f in archive.filelist:
            if f.orig_filename.strip("/") == path:
                return f
        raise TtkStyleFileUnavailable("Unable to find '{}' in specified ZIP file".format(path))

    @staticmethod
    def _find_topmost_folder(archive: zipfile.ZipFile) -> str:
        """Return the relative path in the zipfile to the topmost folder"""
        folders = list(filter(lambda x: x.endswith("/") and x.count("/") == 1, archive.namelist()))
        if len(folders) != 1:
            raise TtkStyleException("Could not find a unique topmost folder in zipfile '{}' while specified".format(archive))
        return folders[0]


class RemoteZippedFile(ZippedFile):
    """Handle a file that is in a remote ZIP-archive file"""
    def __init__(self, path: str, name: str, url: str, root=True):
        ZippedFile.__init__(self, path, RemoteFile(name, url), root)


class GitHubRepoFile(RemoteZippedFile):
    """
    Handle a file from a GitHub repository

    The repository is downloaded as a ZIP file and the specified file
    is extracted to make it available.
    """
    def __init__(self, path: str, author: str, name: str, commit: str="master"):
        """
        :param path: Relative file path in the repository
        :param author: Author name for the repository
        :param name: Repository name
        :param commit: The commit to download the ZIP-file for
        """
        RemoteZippedFile.__init__(self, path, "{}.zip".format(name), self._build_url(author, name, commit), root=False)

    @staticmethod
    def _build_url(author: str, name: str, commit: str) -> str:
        """Build a URL to a download the zipped file from GitHub"""
        return "https://github.com/{}/{}/archive/{}.zip".format(author, name, commit)
