"""Picks the backends for the running operating system; the rest of HandheldCord is platform-neutral."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

if sys.platform == "win32":
    from .windows import autostart
    from .windows.discord import DiscordWindows
    from .windows.gamepad import XInputBackend as GamepadBackend
    from .windows.hotkeys import GlobalHotkeys
    from .windows.sender import KeySender
    from .windows.win32 import acquire_single_instance

    def open_file(path: Path) -> None:
        try:
            os.startfile(path)
        except OSError:  # no program associated with .json
            subprocess.Popen(["notepad.exe", str(path)])
else:
    # An X11 client, through XWayland on Wayland desktops, just like the Discord app itself:
    # X11 lets overlays stay on top, send keys to Discord and register the overlay key.
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    from .linux import autostart
    from .linux.discord import DiscordWindows
    from .linux.gamepad import EvdevBackend as GamepadBackend
    from .linux.hotkeys import GlobalHotkeys
    from .linux.sender import KeySender
    from .linux.session import acquire_single_instance, open_file

__all__ = [
    "DiscordWindows", "GamepadBackend", "GlobalHotkeys", "KeySender",
    "acquire_single_instance", "autostart", "open_file",
]
