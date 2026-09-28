# macOS py2app bundle: Set GI_TYPELIB_PATH before any submodule can import gi.
# This MUST run before any other safeeyes module is loaded, since translations.py
# and utility.py import gi at module level.
import os
import sys

if sys.platform == 'darwin' and (getattr(sys, 'frozen', False) or 'SafeEyes.app' in (sys.executable or '')):
    _res_dir = os.path.abspath(os.path.join(
        os.path.dirname(sys.executable), '..', 'Resources', 'girepository-1.0'
    ))
    if os.path.exists(_res_dir):
        os.environ['GI_TYPELIB_PATH'] = _res_dir
    # Ensure bundled Homebrew dylibs are searchable when app launched from Finder
    os.environ['DYLD_FALLBACK_LIBRARY_PATH'] = '/opt/homebrew/lib:/usr/local/lib'
