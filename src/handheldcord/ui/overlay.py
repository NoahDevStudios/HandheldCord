"""Turns the QML windows into overlays that never take the focus away from Discord."""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QWindow

from ..windows import win32

QML_DIR = Path(__file__).with_name("qml")
# (QML file, click-through)
OVERLAYS = (
    ("HintBar", True),
    ("Toast", True),
    ("Osk", False),
    ("QuickMenu", False),
    ("Wizard", False),
)


def prepare_overlay(window: QWindow, click_through: bool) -> None:
    flags = (
        Qt.WindowType.Tool
        | Qt.WindowType.FramelessWindowHint
        | Qt.WindowType.WindowStaysOnTopHint
        | Qt.WindowType.WindowDoesNotAcceptFocus
    )
    if click_through:
        flags |= Qt.WindowType.WindowTransparentForInput
    window.setFlags(flags)
    # Qt checks this property when showing a window and then uses SW_SHOWNOACTIVATE.
    window.setProperty("_q_showWithoutActivating", True)
    hwnd = int(window.winId())
    win32.make_no_activate(hwnd)
    win32.round_corners(hwnd)
