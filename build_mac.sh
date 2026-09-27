#!/usr/bin/env bash
# ==============================================================================
# build_mac.sh - Build and package SafeEyes as a native macOS Application (.app)
# and register it into macOS Login Items for boot autostart.
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================================="
echo " Starting SafeEyes macOS Build and Packaging Procedure    "
echo "=========================================================="

VENV_DIR=".venv_mac"

# 1. Prepare Python virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "==> Creating virtual environment in $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
fi

echo "==> Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 2. Upgrade pip and install build dependencies
echo "==> Installing build dependencies (py2app, pystray, PyObjC, and app requirements)..."
pip install --upgrade pip setuptools wheel
pip install py2app pystray pyobjc-core pyobjc-framework-Cocoa pyobjc-framework-Quartz pyobjc-framework-UserNotifications PyGObject babel packaging Pillow

# Install safeeyes dependencies in editable mode
pip install -e . --no-deps || true

# 3. Clean previous build artifacts
echo "==> Cleaning previous build directories..."
rm -rf build dist

# 4. Compile gettext translations if msgfmt is present
if command -v msgfmt >/dev/null 2>&1; then
    echo "==> Compiling translations (.po -> .mo)..."
    python3 setup.py build_mo || true
fi

# 5. Build SafeEyes.app bundle using py2app
echo "==> Bundling SafeEyes.app via setup_mac.py..."

# Helper to restore pyproject.toml on exit or interruption
cleanup_pyproject() {
    if [ -f "pyproject.toml.bak" ]; then
        echo "==> Restoring pyproject.toml..."
        mv pyproject.toml.bak pyproject.toml
    fi
}
trap cleanup_pyproject EXIT INT TERM

if [ -f "pyproject.toml" ]; then
    echo "==> Temporarily hiding pyproject.toml to prevent dependency injection..."
    mv pyproject.toml pyproject.toml.bak
fi

BUILD_EXIT_CODE=0
python3 setup_mac.py py2app || BUILD_EXIT_CODE=$?

cleanup_pyproject
trap - EXIT INT TERM

if [ "$BUILD_EXIT_CODE" -ne 0 ]; then
    echo "Error: py2app build failed with exit code $BUILD_EXIT_CODE."
    exit "$BUILD_EXIT_CODE"
fi

APP_BUNDLE="$SCRIPT_DIR/dist/SafeEyes.app"

if [ -d "$APP_BUNDLE" ]; then
    echo "=========================================================="
    echo " Build Successful: $APP_BUNDLE"
    echo "=========================================================="

    # 6. Configure Autostart via macOS Login Items
    echo "==> Configuring macOS Login Items (autostart on boot)..."
    if command -v osascript >/dev/null 2>&1; then
        osascript -e '
        on run argv
            set appPath to (item 1 of argv)
            tell application "System Events"
                if not (exists login item "SafeEyes") then
                    make login item at end with properties {path:appPath, hidden:false, name:"SafeEyes"}
                else
                    set the path of login item "SafeEyes" to appPath
                end if
            end tell
        end run' "$APP_BUNDLE" && echo "==> Successfully registered SafeEyes.app in macOS Login Items!" || echo "==> Note: Could not register in Login Items automatically. You can add dist/SafeEyes.app manually in System Settings -> General -> Login Items."
    else
        echo "==> Note: 'osascript' command not found in the current environment (running on Linux/cross-compile)."
        echo "    On your macOS machine, run the following command to enable autostart:"
        echo "    osascript -e 'tell application \"System Events\" to make login item at end with properties {path:\"$APP_BUNDLE\", hidden:false, name:\"SafeEyes\"}'"
    fi

    echo ""
    echo "To launch SafeEyes immediately, run:"
    echo "    open \"$APP_BUNDLE\""
else
    echo "Error: Build finished but $APP_BUNDLE was not found."
    exit 1
fi
