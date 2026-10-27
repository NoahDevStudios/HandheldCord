"""Finds the official Discord app's main window and switches between it and the game."""
from __future__ import annotations

import logging
import os
import subprocess
import time
from pathlib import Path

from ..windows import win32

log = logging.getLogger(__name__)

DISCORD_EXES = frozenset({"discord.exe", "discordptb.exe", "discordcanary.exe", "discorddevelopment.exe"})
LAUNCHERS = (("Discord", "Discord.exe"), ("DiscordPTB", "DiscordPTB.exe"), ("DiscordCanary", "DiscordCanary.exe"))
CACHE_TTL_S = 5.0


class DiscordWindows:
    def __init__(self, maximize: bool = True, dry_run: bool = False) -> None:
        self.maximize = maximize
        self.dry_run = dry_run
        self._previous = 0
        self._cache: dict[int, tuple[bool, float]] = {}

    def foreground(self) -> int:
        return win32.foreground_window()

    def is_discord(self, hwnd: int) -> bool:
        """Checked every input tick, so the process lookup is cached per window."""
        if not hwnd:
            return False
        now = time.monotonic()
        cached = self._cache.get(hwnd)
        if cached and cached[1] > now:
            return cached[0]
        exe = os.path.basename(win32.process_path(win32.window_pid(hwnd))).lower()
        result = exe in DISCORD_EXES
        if len(self._cache) > 256:
            self._cache.clear()
        self._cache[hwnd] = (result, now + CACHE_TTL_S)
        return result

    def find(self) -> int:
        """The main window: a titled Chromium window of a Discord process, preferring visible and large ones."""
        best, best_score = 0, (False, -1)
        for hwnd in win32.top_level_windows():
            if win32.window_class(hwnd) != "Chrome_WidgetWin_1" or not win32.window_title(hwnd):
                continue
            if not self.is_discord(hwnd):
                continue
            score = (win32.is_visible(hwnd), win32.window_area(hwnd))
            if score > best_score:
                best, best_score = hwnd, score
        return best

    def show(self) -> str:
        """Bring Discord to the front, starting it if needed.

        Returns "discord", "launching", "missing" or "failed".
        """
        hwnd = self.find()
        if not hwnd:
            return "launching" if self._launch() else "missing"
        current = win32.foreground_window()
        if current and current != hwnd and win32.window_pid(current) != os.getpid():
            self._previous = current
        if self.dry_run:
            log.info("[dry-run] would bring Discord (%#x) to the front", hwnd)
            return "discord"
        if self.maximize and not win32.is_maximized(hwnd):
            win32.show_window(hwnd, win32.SW_MAXIMIZE)
        return "discord" if win32.force_foreground(hwnd) else "failed"

    def toggle(self) -> str:
        if self.is_discord(win32.foreground_window()):
            return self.back()
        return self.show()

    def back(self) -> str:
        """Return to the window that was active before Discord; returns "game", "minimized" or "failed"."""
        previous = self._previous
        if self.dry_run:
            log.info("[dry-run] would return to %#x", previous)
            return "game"
        if win32.is_window(previous) and not self.is_discord(previous):
            return "game" if win32.force_foreground(previous) else "failed"
        win32.show_window(win32.foreground_window(), win32.SW_MINIMIZE)
        return "minimized"

    def _launch(self) -> bool:
        if self.dry_run:
            log.info("[dry-run] would start Discord")
            return True
        local = os.environ.get("LOCALAPPDATA", "")
        for folder, exe in LAUNCHERS:
            updater = Path(local, folder, "Update.exe")
            if updater.is_file():
                log.info("Starting %s", exe)
                subprocess.Popen(
                    [str(updater), "--processStart", exe],
                    close_fds=True,
                    creationflags=subprocess.DETACHED_PROCESS,
                )
                return True
        try:
            os.startfile("discord://")
        except OSError:
            log.warning("Discord does not seem to be installed")
            return False
        return True
