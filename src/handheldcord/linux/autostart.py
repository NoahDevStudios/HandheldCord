"""Starts HandheldCord at sign-in through an XDG autostart entry (KDE Plasma, GNOME and others)."""
from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

log = logging.getLogger(__name__)

WAIT_FLAG = "--wait-for-discord"
_SPECIAL = set(" \t\n\"'\\><~|&;$*?#()`")


def entry_path() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / "autostart" / "handheldcord.desktop"


def command(mode: str) -> str:
    """The Exec line; in "discord" mode HandheldCord waits until Discord runs."""
    parts = [sys.executable] if getattr(sys, "frozen", False) else [sys.executable, "-m", "handheldcord"]
    if mode == "discord":
        parts.append(WAIT_FLAG)
    return " ".join(_quote(part) for part in parts)


def _quote(argument: str) -> str:
    """The quoting rules of a desktop entry's Exec key."""
    argument = argument.replace("%", "%%")
    if not _SPECIAL & set(argument):
        return argument
    for char in ("\\", '"', "`", "$"):
        argument = argument.replace(char, "\\" + char)
    return '"' + argument.replace("\\", "\\\\") + '"'


def apply(mode: str) -> bool:
    """Write the entry for "discord" and "windows" (at sign-in), remove it for "off"."""
    path = entry_path()
    try:
        if mode == "off":
            path.unlink(missing_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "[Desktop Entry]\n"
                "Type=Application\n"
                "Name=HandheldCord\n"
                "Comment=Controller-first companion for the official Discord app\n"
                f"Exec={command(mode)}\n"
                "Terminal=false\n"
                "X-GNOME-Autostart-enabled=true\n",
                encoding="utf-8",
            )
    except OSError:
        log.exception("Could not update the autostart entry")
        return False
    log.info("Autostart: %s", mode)
    return True
