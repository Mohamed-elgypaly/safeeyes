#!/usr/bin/env python3
"""Setup script for packaging SafeEyes as a native macOS application bundle using py2app.

Preserves the original setup.py intact for Linux packaging and builds.
"""

import os
from setuptools import setup

APP = ["safeeyes/__main__.py"]

DATA_FILES = []


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


# Collect all necessary assets (icons, glade files, config, audio/resources, plugins)
DATA_FILES.extend(collect_files("safeeyes/glade"))
DATA_FILES.extend(collect_files("safeeyes/platform"))
DATA_FILES.extend(collect_files("safeeyes/config"))
DATA_FILES.extend(collect_files("safeeyes/resource"))
DATA_FILES.extend(collect_files("safeeyes/plugins"))

APP_NAME = "SafeEyes"
VERSION = "3.5.1"

PLIST = {
    "CFBundleName": APP_NAME,
    "CFBundleDisplayName": "Safe Eyes",
    "CFBundleIdentifier": "io.github.slgobinath.SafeEyes",
    "CFBundleVersion": VERSION,
    "CFBundleShortVersionString": VERSION,
    "NSHumanReadableCopyright": "Copyright © 2017-2026 Gobinath Loganathan & Mohamed Elgypaly",
    "LSUIElement": True,  # Run purely as a top Menu Bar app (no Dock icon)
    "NSHighResolutionCapable": True,
}

OPTIONS = {
    "argv_emulation": False,
    "plist": PLIST,
    "packages": ["safeeyes"],
    "includes": [
        "gi",
        "babel",
        "packaging",
        "pystray",
        "PIL",
    ],
    "excludes": [
        "tkinter",
        "test",
        "unittest",
    ],
}

setup(
    name=APP_NAME,
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
