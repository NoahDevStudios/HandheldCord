"""Starts HandheldCord with Windows through the per-user Run key, so no admin rights are needed."""
from __future__ import annotations

import logging
import subprocess
import sys
import winreg
from pathlib import Path

log = logging.getLogger(__name__)

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "HandheldCord"
WAIT_FLAG = "--wait-for-discord"


def command(mode: str) -> str:
    """The command Windows runs at sign-in; in "discord" mode HandheldCord waits until Discord runs."""
    if getattr(sys, "frozen", False):
        parts = [sys.executable]
    else:  # from source: the windowless interpreter, so no console window opens
        pythonw = Path(sys.executable).with_name("pythonw.exe")
        parts = [str(pythonw if pythonw.exists() else sys.executable), "-m", "handheldcord"]
    if mode == "discord":
        parts.append(WAIT_FLAG)
    return subprocess.list2cmdline(parts)


def apply(mode: str) -> bool:
    """Write the entry for "discord" and "windows", remove it for "off"; False if the registry refused."""
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            if mode == "off":
                try:
                    winreg.DeleteValue(key, VALUE_NAME)
                except FileNotFoundError:
                    pass
            else:
                winreg.SetValueEx(key, VALUE_NAME, 0, winreg.REG_SZ, command(mode))
    except OSError:
        log.exception("Could not update the autostart entry")
        return False
    log.info("Autostart: %s", mode)
    return True
