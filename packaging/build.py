"""Builds dist/HandheldCord-<version>-win64.zip: a one-folder PyInstaller build that needs no Python.

Usage: python packaging/build.py   (after: pip install -e .[build])
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
BUILD = ROOT / "build"
DIST = ROOT / "dist"
sys.path.insert(0, str(SRC))

from handheldcord import __version__  # noqa: E402


def make_icon(path: Path) -> Path:
    # Offscreen rendering works without a desktop session (CI); it needs to be told where the fonts are.
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("QT_QPA_FONTDIR", str(Path(os.environ.get("WINDIR", r"C:\Windows")) / "Fonts"))
    from PySide6.QtGui import QGuiApplication

    from handheldcord.ui.icon import render_icon

    app = QGuiApplication.instance() or QGuiApplication([])  # noqa: F841 (must stay alive while drawing)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not render_icon(256).save(str(path)):
        raise RuntimeError(f"could not write {path}")
    return path


def main() -> int:
    icon = make_icon(BUILD / "handheldcord.ico")
    subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            "--noconfirm",
            "--clean",
            "--windowed",
            "--name", "HandheldCord",
            "--icon", str(icon),
            "--paths", str(SRC),
            "--add-data", f"{SRC / 'handheldcord' / 'ui' / 'qml'}{os.pathsep}handheldcord/ui/qml",
            "--exclude-module", "tkinter",
            "--distpath", str(DIST),
            "--workpath", str(BUILD / "pyinstaller"),
            "--specpath", str(BUILD),
            str(ROOT / "packaging" / "launcher.py"),
        ],
        check=True,
    )
    app_dir = DIST / "HandheldCord"
    shutil.copy2(ROOT / "LICENSE", app_dir / "LICENSE.txt")
    archive = shutil.make_archive(str(DIST / f"HandheldCord-{__version__}-win64"), "zip", root_dir=DIST, base_dir="HandheldCord")
    print(f"Built {archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
