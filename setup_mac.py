#!/usr/bin/env python3
import os
from setuptools import setup
from setuptools.dist import Distribution

# Prevent setuptools from pulling dependencies from pyproject.toml into install_requires,
# which triggers py2app's "error: install_requires is no longer supported" check.
_orig_init = Distribution.__init__


def _clean_init(self, *args, **kwargs):
    _orig_init(self, *args, **kwargs)
    self.install_requires = []


Distribution.__init__ = _clean_init

APP = ["safeeyes/__main__.py"]


def collect_files(directory):
    files_list = []
    for root, _, files in os.walk(directory):
        valid_files = [
            os.path.join(root, f)
            for f in files
            if not f.endswith(".pyc") and "__pycache__" not in root
        ]
        if valid_files:
            files_list.append((root, valid_files))
    return files_list


DATA_FILES = []
DATA_FILES.extend(collect_files("safeeyes/glade"))
DATA_FILES.extend(collect_files("safeeyes/platform"))
DATA_FILES.extend(collect_files("safeeyes/config"))
DATA_FILES.extend(collect_files("safeeyes/resource"))
DATA_FILES.extend(collect_files("safeeyes/plugins"))

OPTIONS = {
    "argv_emulation": False,
    "plist": {"LSUIElement": True},
    "packages": ["safeeyes"],
    "includes": [
        "gi",
        "cairo",
        "babel",
        "croniter",
        "packaging",
        "pystray",
        "logging.handlers",
    ],
}

setup(
    name="SafeEyes",
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
