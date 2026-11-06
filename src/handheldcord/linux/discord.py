"""Finds the Discord app's main window (X11/XWayland) and switches between it and the game."""
from __future__ import annotations

import logging
import os
import shutil
import subprocess
import time
from pathlib import Path

from .x11 import X11

log = logging.getLogger(__name__)

DISCORD_CLASSES = frozenset({"discord", "discordptb", "discordcanary"})  # WM_CLASS, also of the Flatpak
DISCORD_PROCESSES = frozenset({"discord", "discordptb", "discordcanary"})  # /proc/<pid>/comm
COMMANDS = ("discord", "discord-ptb", "discord-canary")
FLATPAKS = ("com.discordapp.Discord", "com.discordapp.DiscordCanary")
CACHE_TTL_S = 5.0


class DiscordWindows:
    def __init__(self, maximize: bool = True, dry_run: bool = False) -> None:
        self.maximize = maximize
        self.dry_run = dry_run
        self.x = X11()
        self._previous = 0
        self._cache: dict[int, tuple[bool, float]] = {}

    def foreground(self) -> int:
        return self.x.active_window()

    def running(self) -> bool:
        """Whether a Discord process exists, even before (or without) a window."""
        for comm in Path("/proc").glob("[0-9]*/comm"):
            try:
                if comm.read_text().strip().lower() in DISCORD_PROCESSES:
                    return True
            except OSError:
                continue
        return False

    def is_discord(self, wid: int) -> bool:
        """Checked every input tick, so the lookup is cached per window."""
        if not wid:
            return False
        now = time.monotonic()
        cached = self._cache.get(wid)
        if cached and cached[1] > now:
            return cached[0]
        result = self.x.wm_class(wid) in DISCORD_CLASSES
        if len(self._cache) > 256:
            self._cache.clear()
        self._cache[wid] = (result, now + CACHE_TTL_S)
        return result

    def find(self) -> int:
        """The main window: a titled Discord window, preferring visible and large ones."""
        best, best_score = 0, (False, -1)
        for wid in self.x.client_windows():
            if not self.is_discord(wid) or not self.x.title(wid):
                continue
            score = (not self.x.is_minimized(wid), self.x.area(wid))
            if score > best_score:
                best, best_score = wid, score
        return best

    def show(self) -> str:
        """Bring Discord to the front, starting it if needed; returns "discord", "launching" or "missing"."""
        wid = self.find()
        if not wid:
            return "launching" if self._launch() else "missing"
        current = self.x.active_window()
        if current and current != wid and self.x.pid(current) != os.getpid():
            self._previous = current
        if self.dry_run:
            log.info("[dry-run] would bring Discord (%#x) to the front", wid)
            return "discord"
        if self.maximize and not self.x.is_maximized(wid):
            self.x.maximize(wid)
        self.x.activate(wid)
        return "discord"

    def toggle(self) -> str:
        if self.is_discord(self.x.active_window()):
            return self.back()
        return self.show()

    def back(self) -> str:
        """Return to the window that was active before Discord; returns "game" or "minimized"."""
        previous = self._previous
        if self.dry_run:
            log.info("[dry-run] would return to %#x", previous)
            return "game"
        if self.x.exists(previous) and not self.is_discord(previous):
            self.x.activate(previous)
            return "game"
        current = self.x.active_window()
        if current:
            self.x.minimize(current)
        return "minimized"

    def _launch(self) -> bool:
        if self.dry_run:
            log.info("[dry-run] would start Discord")
            return True
        for command in COMMANDS:
            path = shutil.which(command)
            if path:
                return _spawn([path])
        flatpak = shutil.which("flatpak")
        if flatpak:
            for app_id in FLATPAKS:
                if _flatpak_installed(app_id):
                    return _spawn([flatpak, "run", app_id])
        log.warning("Discord does not seem to be installed")
        return False


def _flatpak_installed(app_id: str) -> bool:
    return any(Path(base, app_id).is_dir() for base in (
        "/var/lib/flatpak/app", Path.home() / ".local/share/flatpak/app",
    ))


def _spawn(command: list[str]) -> bool:
    log.info("Starting %s", " ".join(command))
    try:
        subprocess.Popen(command, start_new_session=True, stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        log.warning("Could not start %s", command[0], exc_info=True)
        return False
    return True
